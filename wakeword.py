import pvporcupine
import pyaudio
import struct

class Wakeword:
    def __init__(self, picovoice_key):
        self.picovoice_key = picovoice_key
        self.porcupine = pvporcupine.create(access_key=picovoice_key, keyword_paths=['wakeup-wakeword.ppn'])
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(rate=self.porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=self.porcupine.frame_length)
    def listen_for_wakeword(self, callback):
        print("Listening for wakeword...")
        while True:
            pcm = self.stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Wakeword detected")
                callback()
