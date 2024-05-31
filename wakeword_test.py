import os
import pvporcupine
import pyaudio
import struct 


# AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)
picovoice_key = os.getenv('PICOVOICE_KEY')

try:
    porcupine = pvporcupine.create(access_key=picovoice_key, keyword_paths=['wakeup-wakeword.ppn'])
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
        )

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from('h' * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print('есть')
finally:
    if porcupine is not None:
        porcupine.delete()