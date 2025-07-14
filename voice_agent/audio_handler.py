import pyaudio
import threading
import logging
from threading import Event
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

    def cleanup(self):
        """
        Clean up resources by stopping the stream and terminating PyAudio.
        """
        if self.stream:
            self.stop_audio_stream()
        self.p.terminate()

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
    
    def play_audio(self, audio_data):
        """
        Play audio data, stopping any previous playback in progress.
        """
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

