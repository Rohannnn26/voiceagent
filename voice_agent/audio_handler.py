import pyaudio
import threading
import logging
from threading import Event
from queue import Queue
from logger import logger

class AudioHandler:
    """
    Handles audio input and output using PyAudio.
    """
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_buffer = b''
        self.chunk_size = 1024  # Number of audio frames per buffer
        self.format = pyaudio.paInt16  # Audio format (16-bit PCM)
        self.channels = 1  # Mono audio
        self.rate = 24000  # Sampling rate in Hz
        self.is_recording = False
        self.playback_thread = None
        self.stop_playback_event = Event()
        
        # Streaming audio playback attributes
        self.streaming_queue = Queue()
        self.streaming_thread = None
        self.is_streaming = False
        self.streaming_output_stream = None
        self.audio_response_complete = False

    def start_audio_stream(self):
        """
        Start the audio input stream.
        """
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

    def stop_audio_stream(self):
        """
        Stop the audio input stream.
        """
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def start_recording(self):
        """Start continuous recording"""
        self.is_recording = True
        self.audio_buffer = b''
        self.start_audio_stream()

    def stop_recording(self):
        """Stop recording and return the recorded audio"""
        self.is_recording = False
        self.stop_audio_stream()
        return self.audio_buffer

    def record_chunk(self):
        """Record a single chunk of audio"""
        if self.stream and self.is_recording:
            data = self.stream.read(self.chunk_size)
            self.audio_buffer += data
            return data
        return None
    
    def start_streaming_playback(self):
        """
        Start streaming audio playback mode.
        Audio chunks will be played as they arrive.
        """
        if self.is_streaming:
            return  # Already streaming
            
        self.is_streaming = True
        self.audio_response_complete = False
        self.stop_playback_event.clear()
        
        # Clear any remaining items in queue
        while not self.streaming_queue.empty():
            try:
                self.streaming_queue.get_nowait()
            except:
                break
        
        def streaming_playback():
            try:
                # Create output stream for streaming
                self.streaming_output_stream = self.p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    output=True,
                    frames_per_buffer=self.chunk_size
                )
                
                logger.info("🔊 Started streaming audio playback")
                
                while self.is_streaming and not self.stop_playback_event.is_set():
                    try:
                        # Get audio chunk from queue (with timeout)
                        audio_chunk = self.streaming_queue.get(timeout=0.5)
                        
                        if audio_chunk is None:  # Sentinel to stop
                            break
                            
                        # Play the chunk immediately
                        self.streaming_output_stream.write(audio_chunk)
                        self.streaming_queue.task_done()
                        
                    except:
                        # Timeout - check if audio response is complete and queue is empty
                        if self.audio_response_complete and self.streaming_queue.empty():
                            logger.info("🔊 All audio chunks played, ending stream")
                            break
                        # Otherwise continue waiting for more chunks
                        continue
                            
            except Exception as e:
                logger.error(f"Error in streaming playback: {e}")
            finally:
                if self.streaming_output_stream:
                    self.streaming_output_stream.stop_stream()
                    self.streaming_output_stream.close()
                    self.streaming_output_stream = None
                self.is_streaming = False
                logger.info("🔊 Stopped streaming audio playback")
        
        self.streaming_thread = threading.Thread(target=streaming_playback, daemon=True)
        self.streaming_thread.start()

    def mark_audio_response_complete(self):
        """
        Mark that no more audio chunks will arrive for this response.
        """
        self.audio_response_complete = True
        logger.debug("🔊 Audio response marked as complete")

    def add_streaming_audio(self, audio_data):
        """
        Add audio data to the streaming queue for immediate playback.
        """
        if not self.is_streaming:
            self.start_streaming_playback()
            
        self.streaming_queue.put(audio_data)

    def stop_streaming_playback(self):
        """
        Stop streaming audio playback immediately.
        """
        if not self.is_streaming:
            return
            
        logger.info("🔊 Force stopping streaming audio playback...")
        self.is_streaming = False
        self.audio_response_complete = True
        self.stop_playback_event.set()
        
        # Add sentinel to wake up the streaming thread
        try:
            self.streaming_queue.put_nowait(None)
        except:
            pass  # Queue might be full, that's ok
        
        # Wait for streaming thread to finish
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=1.0)

    def play_audio(self, audio_data):
        """
        Play audio data, stopping any previous playback in progress.
        This is the original buffered playback method.
        """
        # Stop any streaming playback first
        self.stop_streaming_playback()
        
        def play():
            stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True
            )
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if self.stop_playback_event.is_set():
                    break  # Stop playback if new input starts
                stream.write(audio_data[i:i+chunk_size])
            stream.stop_stream()
            stream.close()

        # If already playing, stop it
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_playback_event.set()         # Signal the thread to stop
            self.playback_thread.join()            # Wait for it to finish

        self.stop_playback_event.clear()           # Clear stop flag
        self.playback_thread = threading.Thread(target=play)
        self.playback_thread.start()

    def cleanup(self):
        """
        Clean up resources by stopping the stream and terminating PyAudio.
        """
        self.stop_streaming_playback()
        if self.stream:
            self.stop_audio_stream()
        self.p.terminate()

