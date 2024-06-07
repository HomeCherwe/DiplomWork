import os
import time
import hashlib
from ukrainian_tts.tts import TTS, Voices, Stress
from pydub import AudioSegment
from pydub.playback import play

class TTSHandler:
    def __init__(self):
        self.tts = TTS(device="cpu")

    def play_sound(self, text):
        def get_hashed_filename(text):
            hash_object = hashlib.md5(text.encode())
            return f"{hash_object.hexdigest()}.wav"

        filename = get_hashed_filename(text)
        filepath = os.path.join("cache", filename)
        os.makedirs("cache", exist_ok=True)

        start_time = time.time()

        if not os.path.exists(filepath):
            with open(filepath, mode="wb") as file:
                _, output_text = self.tts.tts(text, Voices.Dmytro.value, Stress.Dictionary.value, file)
            print("Accented text:", output_text)
        else:
            print("Using cached file:", filepath)

        while True:
            try:
                audio = AudioSegment.from_wav(filepath)
                play(audio)
                break
            except Exception as e:
                print(e)
                continue

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Скрипт виконувався {execution_time} секунд")
