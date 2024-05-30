import time
import os 
import threading

import speech_recognition as sr                     # pip install SpeechRecognition
from tuya_connector import TuyaOpenAPI              # pip3 install tuya-connector-python
from ukrainian_tts.tts import TTS, Voices, Stress   # pip install git+https://github.com/robinhad/ukrainian-tts.git
from playsound import playsound                     # pip install playsound
from dotenv import load_dotenv                      # pip install python-dotenv

load_dotenv()

tts = TTS(device="cpu")


access_id = os.getenv('ACCESS_ID')
access_key = os.getenv('ACCESS_KEY')
end_point = os.getenv('ENDPOINT')
uid= os.getenv('UID')

openapi = TuyaOpenAPI(end_point, access_id, access_key)
openapi.connect()

res = openapi.get(f"/v1.0/users/{uid}/devices")
list_devices = res['result']

class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500 
        self.recognizer.dynamic_energy_threshold = False

        threading.Thread(target=self.run_assistant).start()
        self.PlaySound('Я увімкнутий!')

    def run_assistant(self):
        while True:
            try:
                with sr.Microphone() as mic:
                    print('Чекає wakeword')
                    self.recognizer.adjust_for_ambient_noise(mic)

                    audio = self.recognizer.listen(mic, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language='uk-UA').lower()

                    print("You said:", text)

                    if 'привіт дім' in text:
                    # if True:
                        print('Привіт Макс')
                        print('Що для вас зробити?')
                        self.PlaySound(f'Я слухаю вас сер!') 

                        audio = self.recognizer.listen(mic, phrase_time_limit=5)
                        text = self.recognizer.recognize_google(audio, language='uk-UA').lower()
                        
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
                                                    threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(True, device_id, code)).start()
                                                    self.PlaySound(f'{name_device} буде увімкнуто через {count} {time_what}!')
                                                else:
                                                    self.on_off_controll_devices(True, device_id, code)
                                                    self.PlaySound(f'{name_device} увімкнено!')
                                                
                                            elif "виключи" in text:
                                                if "через" in text:
                                                    mnojnik = 1
                                                    count = int(text.split()[3])
                                                    time_what = text.split()[4]
                                                    if time_what == 'минут' or time_what == 'минуту':
                                                        mnojnik = 60
                                                    elif time_what == 'годин':
                                                        mnojnik = 120
                                                    threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(False, device_id, code)).start()
                                                    self.PlaySound(f'{name_device} буде вимкнуто через {count} {time_what}!')
                                                else:
                                                    self.on_off_controll_devices(False, device_id, code)
                                                    self.PlaySound(f'{name_device} вимкнено!')    
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
            except:
                continue
    
    def on_off_controll_devices(self, value, device_id, code):
        commands = {'commands': [{'code': code, 'value': value}]}
        res = openapi.post(f"/v1.0/devices/{device_id}/commands", commands)
        print(res)
    
    def PlaySound(self, text):

        with open("test.wav", mode="wb") as file:
            _, output_text = tts.tts(text, Voices.Dmytro.value, Stress.Dictionary.value, file)
        while True:
            try:
                playsound('test.wav')
            except Exception as e:
                pass
            else:
                break
 
Assistant()