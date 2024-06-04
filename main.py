import warnings

# Ignore specific warning
warnings.filterwarnings("ignore", message="TypedStorage is deprecated")

import time
import os 
import threading
import hashlib

import speech_recognition as sr                     # pip install SpeechRecognition
from tuya_connector import TuyaOpenAPI              # pip3 install tuya-connector-python
from ukrainian_tts.tts import TTS, Voices, Stress   # pip install git+https://github.com/robinhad/ukrainian-tts.git
from playsound import playsound                     # pip install playsound
from dotenv import load_dotenv                      # pip install python-dotenv

import pvporcupine
import pyaudio
import struct
from IPython.display import Audio, display
from pydub import AudioSegment
from pydub.playback import play

load_dotenv()

access_id = os.getenv('ACCESS_ID')
access_key = os.getenv('ACCESS_KEY')
end_point = os.getenv('ENDPOINT')
uid= os.getenv('UID')
picovoice_key = os.getenv('PICOVOICE_KEY')

class Assistant:
    def __init__(self):
        self.tts = TTS(device="cpu")
        self.openapi = TuyaOpenAPI(end_point, access_id, access_key)
        self.openapi.connect()
        try:
            self.res = self.openapi.get(f"/v1.0/users/{uid}/devices")
            if 'result' in self.res:
                self.list_devices = self.res['result']
            else:
                print("Error: 'result' not found in response.")
                print("Response:", self.res)
                return

            self.PlaySound('Я увімкнутий!')
            threading.Thread(target=self.run_assistant).start()
        except Exception as e:
            print("Failed to get devices:", e)


    def run_assistant(self):
        while True:
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
                    start_time = time.time()    
                    pcm = audio_stream.read(porcupine.frame_length)
                    pcm = struct.unpack_from('h' * porcupine.frame_length, pcm)
                    keyword_index = porcupine.process(pcm)
                    if keyword_index >= 0:
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Скрипт виконувався {execution_time} секунд")
                        self.takeCommand()
            except Exception as e:
                print(e)
                continue
    
    def takeCommand(self):
        self.PlaySound(f'Я слухаю вас сер!') 
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print('Listening...')
            audio = r.listen(source)
            try:
                print('Recognizing...')
                text = r.recognize_google(audio, language='uk-UA').lower()
                print("You said:", text)

                if text == 'стоп':
                    self.root.destroy()
                    sys.exit()
                else:
                    if text is not None:
                        if "включи" in text or "виключи" in text:
                            for device in self.list_devices:
                                name_device = device['name'].lower()
                                status = device['status'][0]['value']
                                code = device['status'][0]['code']
                                device_id = device['id']

                                if name_device in text:
                                    if "включи" in text:
                                        if "через" in text:
                                            mnojnik = 1
                                            count = int(text.split()[3])
                                            time_what = text.split()[4]
                                            if time_what == 'минут' or time_what == 'минуту':
                                                mnojnik = 60
                                            elif time_what == 'годин':
                                                mnojnik = 120
                                            self.PlaySound(f'{name_device} буде увімкнуто через {count} {time_what}!')
                                            threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(True, device_id, code)).start()
                                        else:
                                            self.PlaySound(f'Вмикаю {name_device}')
                                            self.on_off_controll_devices(True, device_id, code)
                                        
                                    elif "виключи" in text:
                                        if "через" in text:
                                            mnojnik = 1
                                            count = int(text.split()[3])
                                            time_what = text.split()[4]
                                            if time_what == 'минут' or time_what == 'минуту':
                                                mnojnik = 60
                                            elif time_what == 'годин':
                                                mnojnik = 120
                                            self.PlaySound(f'{name_device} буде вимкнуто через {count} {time_what}!')
                                            threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(False, device_id, code)).start()
                                        else:
                                            self.PlaySound(f'Вимикаю {name_device}')
                                            self.on_off_controll_devices(False, device_id, code)

                        elif "який" in text or "яка" in text or "яке" in text:
                            if 'температура' in text:
                                for device in self.list_devices:
                                    name_device = device['name'].lower()
                                    status = device['status'][0]['value']
                                    code = device['status'][0]['code']
                                    device_id = device['id']

                                    if name_device == 'температура спальня':
                                        status = str(status/10)
                                        status_res = status.split('.')
                                        if status_res[1] == '0':
                                            text_say = f'Температура в спальні {status_res[0]} градуса' 
                                        else:
                                            text_say = f'Температура в спальні {status_res[0]} і {status_res[1]} градуса' 
                                            self.PlaySound(text_say)
            except Exception as e:
                print(e)

    def on_off_controll_devices(self, value, device_id, code):
        commands = {'commands': [{'code': code, 'value': value}]}
        res = self.openapi.post(f"/v1.0/devices/{device_id}/commands", commands)
        print(res)
    
    def PlaySound(self, text):
        
        def get_hashed_filename(text):
            # Generate a unique filename based on the hash of the text
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
 
Assistant()