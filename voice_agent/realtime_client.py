import json, ssl, base64, asyncio, websockets, logging
from config import AZURE_WS_URL, AZURE_RTOPENAI_KEY
from tools import FUNCTION_SCHEMAS, TOOLS
from audio_handler import AudioHandler
import os
from logger import logger

# ── Optional: Keyboard help text ─────────────────────────
KEYBOARD_COMMANDS = """
q: Quit
t: Send text message
a: Send audio message
"""

class RealtimeClient:
    def __init__(self, instructions, voice="verse"):
        # WebSocket Configuration
        resource = os.getenv('AZURE_RTOPENAI_RESOURCE')
        deployment = os.getenv('AZURE_RTOPENAI_DEPLOYMENT')
        api_version = os.getenv('AZURE_RTOPENAI_API_VERSION')

        self.url = f"wss://{resource}/openai/realtime?deployment={deployment}&api-version={api_version}"
        self.model = deployment
        self.api_key = os.getenv('AZURE_RTOPENAI_KEY')

        self.ws = None
        self.audio_handler = AudioHandler()

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        self.instructions = instructions
        self.voice = voice

        self.VAD_turn_detection = True
        self.VAD_config = {
            "type": "server_vad",
            "threshold": 0.9,  # Increased from 0.5 to 0.8 - requires louder speech to activate
            "prefix_padding_ms": 300,
            "silence_duration_ms": 1000  # Increased from 600 to 800ms - requires longer silence to stop
        }

        self.session_config = {
            "modalities": ["audio", "text"],
            "instructions": self.instructions,
            "voice": self.voice,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": self.VAD_config if self.VAD_turn_detection else None,
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "temperature": 0.6,
            "tools": FUNCTION_SCHEMAS,
            "tool_choice": "auto"
        }

    async def connect(self):
        logger.info(f"Connecting to WebSocket: {self.url}")
        headers = {
            "api-key": self.api_key,
            "OpenAI-Beta": "realtime=v1"
        }

        self.ws = await websockets.connect(
            self.url,
            extra_headers=headers,
            ssl=self.ssl_context
        )
        logger.info("Successfully connected to OpenAI Realtime API")

        await self.send_event({
            "type": "session.update",
            "session": self.session_config
        })

        await self.send_event({"type": "response.create"})

    async def send_event(self, event):
        await self.ws.send(json.dumps(event))
        logger.debug(f"Event sent - type: {event['type']}")

    async def receive_events(self):
        try:
            async for message in self.ws:
                event = json.loads(message)
                await self.handle_event(event)
        except websockets.ConnectionClosed as e:
            logger.error(f"WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    async def handle_event(self, event):
        event_type = event.get("type")
        logger.debug(f"Received event type: {event_type}")

        if event_type == "error":
            logger.error(f"Error event received: {event['error']['message']}")

        # ── User Input Transcription Events ──
        elif event_type == "conversation.item.input_audio_transcription.completed":
            user_transcript = event.get("transcript", "")
            logger.info(f"🎤 USER INPUT TRANSCRIPTION: '{user_transcript}'")

        elif event_type == "conversation.item.input_audio_transcription.failed":
            logger.warning(f"⚠️  USER TRANSCRIPTION FAILED: {event.get('error', 'Unknown error')}")

        # ── Agent Output Text Events ──
        elif event_type == "response.text.delta":
            print(event["delta"], end="", flush=True)

        elif event_type == "response.text.done":
            agent_text = event.get("text", "")
            if agent_text:
                logger.info(f"🤖 AGENT SPEECH TRANSCRIPT: '{agent_text}'")
                print(f"\n🤖 Agent text: {agent_text}")

        # ── Agent Audio Events ──
        elif event_type == "response.audio.delta":
            audio_data = base64.b64decode(event["delta"])
            # Stream audio immediately instead of buffering
            self.audio_handler.add_streaming_audio(audio_data)
            logger.debug(f"🔊 Streaming audio chunk: {len(audio_data)} bytes")

        elif event_type == "response.audio.done":
            # Mark that no more audio chunks will come
            self.audio_handler.mark_audio_response_complete()
            logger.info("🔊 Audio response complete - letting remaining chunks finish playing")

        elif event_type == "response.done":
            outputs = event["response"]["output"]

            if outputs and outputs[0]["type"] == "function_call":
                # ✅ Tool handling for all tools
                fc = outputs[0]
                name = fc["name"]
                call_id = fc["call_id"]
                args = json.loads(fc["arguments"])

                logger.info(f"Function call requested: {name} with args {args}")
                
                # Special handling for backend tool - make it non-blocking
                if name in ["query_chatbot_backend"]:
                    logger.info(f"🔄 Backend tool detected - sending status and running async")
                    
                    # Send immediate status message
                    await self.send_event({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "text", "text": "**talk natually like using normal humans words such as hmm sure or something like that"
                            "tell the user that we you have understood the request and are processing it ,"
                            " it might take some time , "
                            "please wait"
                            "**TALK IN GAP , KEEP TALKING UNTIL THE BACKEND TOOL IS DONE**"}]
                        }
                    })
                    await self.send_event({"type": "response.create"})
                    
                    # Run backend tool in background without blocking
                    asyncio.create_task(self._execute_backend_tool_async(call_id, args))
                    return  # Exit early, don't block on tool execution
                
                try:
                    # Handle other tools normally (synchronously)
                    result = TOOLS[name](**args)
                except Exception as e:
                    result = {"error": str(e)}
                    logger.exception(f"Tool {name} failed")

                await self.send_event({
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps(result)
                    }
                })
                await self.send_event({"type": "response.create"})

        elif event_type == "input_audio_buffer.speech_started":
            logger.debug("Speech started - stopping any ongoing audio playback")
            # Stop any ongoing audio playback when user starts speaking
            self.audio_handler.stop_streaming_playback()

        elif event_type == "input_audio_buffer.speech_stopped":
            logger.debug("Speech stopped")

        # ── Additional Transcription Events ──
        elif event_type == "conversation.item.created":
            item = event.get("item", {})
            if item.get("type") == "message" and item.get("role") == "assistant":
                # Log when assistant creates a message
                content = item.get("content", [])
                if content and len(content) > 0:
                    if content[0].get("type") == "text":
                        text_content = content[0].get("text", "")
                        logger.info(f"🤖 ASSISTANT MESSAGE CREATED: '{text_content}'")

        elif event_type == "conversation.item.truncated":
            logger.info(f"Conversation item truncated: {event}")

    async def send_text(self, text):
        logger.info(f"📤 USER TEXT INPUT: '{text}'")
        print(f"📤 Sending: {text}")
        
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": text
                }]
            }
        }
        await self.send_event(event)
        await self.send_event({"type": "response.create"})

    async def send_audio(self):
        """
        Record and send audio using server-side turn detection
        """
        logger.debug("Starting audio recording for user input")
        self.audio_handler.start_recording()
        
        try:
            while True:
                chunk = self.audio_handler.record_chunk()
                if chunk:
                    # Encode and send audio chunk
                    base64_chunk = base64.b64encode(chunk).decode('utf-8')
                    await self.send_event({
                        "type": "input_audio_buffer.append",
                        "audio": base64_chunk
                    })
                    await asyncio.sleep(0.01)
                else:
                    break

        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
            self.audio_handler.stop_recording()
            logger.debug("Audio recording stopped")
    
        finally:
            # Stop recording even if an exception occurs
            self.audio_handler.stop_recording()
            logger.debug("Audio recording stopped")
            if not self.VAD_turn_detection:
                await self.send_event({"type": "input_audio_buffer.commit"})
                logger.debug("Audio buffer committed")

    async def run(self):
        await self.connect()
        receive_task = asyncio.create_task(self.receive_events())

        try:
            while True:
                command = await asyncio.get_event_loop().run_in_executor(None, input, KEYBOARD_COMMANDS)
                if command == 'q':
                    logger.info("Quit command received")
                    break
                elif command == 't':
                    text = await asyncio.get_event_loop().run_in_executor(None, input, "Enter TEXT message: ")
                    await self.send_text(text)
                elif command == 'a':
                    await self.send_audio()
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            receive_task.cancel()
            await self.cleanup()

    async def cleanup(self):
        self.audio_handler.stop_streaming_playback()  # Stop any streaming
        self.audio_handler.cleanup()
        if self.ws:
            await self.ws.close()

    async def send_immediate_response(self, message: str):
        """Send an immediate text response to the user."""
        logger.info(f"Sending immediate acknowledgment: {message}")
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": message}]
            }
        })  
        await self.send_event({"type": "response.create"})

    async def _execute_backend_tool_async(self, call_id: str, args: dict):
        """Execute backend tool asynchronously and send result when complete"""
        try:
            logger.info(f"🔄 Starting non-blocking backend execution with args: {args}")
            result = await TOOLS["query_chatbot_backend"](**args)
            logger.info(f"✅ Backend tool completed successfully")
        except Exception as e:
            result = {"error": str(e)}
            logger.exception(f"❌ Backend tool failed")
        
        # Send the tool result when ready
        logger.info(f"📤 Sending backend tool result")
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            }
        })
        await self.send_event({"type": "response.create"})