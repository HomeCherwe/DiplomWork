import time
import os 
import threading

import speech_recognition as sr                     # pip install SpeechRecognition
from tuya_connector import TuyaOpenAPI              # pip3 install tuya-connector-python
from ukrainian_tts.tts import TTS, Voices, Stress   # pip install git+https://github.com/robinhad/ukrainian-tts.git
from playsound import playsound                     # pip install playsound
from dotenv import load_dotenv                      # pip install python-dotenv

import pvporcupine
import pyaudio
import struct
import torch
from IPython.display import Audio, display
from pydub import AudioSegment
from pydub.playback import play

# device = torch.device('cpu')
# torch.set_num_threads(4)
# local_file = 'model_ua.pt'

# if not os.path.isfile(local_file):
#     torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ua/v4_ua.pt',
#                                    local_file)  

load_dotenv()

tts = TTS(device="cpu")


access_id = os.getenv('ACCESS_ID')
access_key = os.getenv('ACCESS_KEY')
end_point = os.getenv('ENDPOINT')
uid= os.getenv('UID')
# AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)
picovoice_key = os.getenv('PICOVOICE_KEY')

openapi = TuyaOpenAPI(end_point, access_id, access_key)
openapi.connect()

res = openapi.get(f"/v1.0/users/{uid}/devices")
list_devices = res['result']

class Assistant:
    def __init__(self):
        self.PlaySound('Я увімкнутий!')
        threading.Thread(target=self.run_assistant).start()
        print('Я увімкнутий!')

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
                    pcm = audio_stream.read(porcupine.frame_length)
                    pcm = struct.unpack_from('h' * porcupine.frame_length, pcm)
                    keyword_index = porcupine.process(pcm)
                    if keyword_index >= 0:
                        self.takeCommand()
            except Exception as e:
                print(e)
                continue
    
    def takeCommand(self):
        # self.PlaySound(f'Я слухаю вас сер!') 
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print('Listening...')
            audio = r.listen(source)
            try:
                print('Recognizing...')
                text = r.recognize_google(audio, language='uk-UA').lower()
                print("You said:", text)

                if text == 'stop':
                    self.root.destroy()
                    sys.exit()
                else:
                    if text is not None:
                        if "включи" in text or "виключи" in text:
                            for device in list_devices:
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
                                            # self.PlaySound(f'{name_device} буде увімкнуто через {count} {time_what}!')
                                            threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(True, device_id, code)).start()
                                        else:
                                            # self.PlaySound(f'Вмикаю {name_device}')
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
                                            # self.PlaySound(f'{name_device} буде вимкнуто через {count} {time_what}!')
                                            threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(False, device_id, code)).start()
                                        else:
                                            # self.PlaySound(f'Вимикаю {name_device}')
                                            self.on_off_controll_devices(False, device_id, code)

                        elif "який" in text or "яка" in text or "яке" in text:
                            if 'температура' in text:
                                for device in list_devices:
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
        res = openapi.post(f"/v1.0/devices/{device_id}/commands", commands)
        print(res)
    
    def PlaySound(self, text):

        model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        model.to(device)

        sample_rate = 24000
        speaker='mykyta'

        audio_paths = model.save_wav(text=text,
                                    speaker=speaker,
                                    sample_rate=sample_rate)

        # Завантажуємо .wav файл
        audio = AudioSegment.from_wav(audio_paths)

        # Відтворюємо аудіо
        play(audio)
 
Assistant()