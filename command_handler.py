import speech_recognition as sr
from tuya_connector import TuyaOpenAPI
import os
from dotenv import load_dotenv

class CommandHandler:
    def __init__(self, tts_handler):
        self.tts_handler = tts_handler
        self.load_env_and_connect()

    def load_env_and_connect(self):
        load_dotenv()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.openapi = TuyaOpenAPI(
            os.getenv('ENDPOINT'),
            os.getenv('ACCESS_ID'),
            os.getenv('ACCESS_KEY')
        )
        self.openapi.connect()
        self.reload_device()

    def reload_device(self):
        res = self.openapi.get(f"/v1.0/users/{os.getenv('UID')}/devices")
        if 'result' in res:
            self.list_devices = res['result']
        else:
            print("Error: 'result' not found in response.")
            print("Response:", res)
            return

    def listen_for_command(self):
        print("Listening for command...")
        print(self.list_devices)
        command = ''
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print('Recognizing...')
                command = self.recognizer.recognize_google(audio, language='uk-UA').lower()
                print("You said:", command)
            except sr.UnknownValueError:
                print("Не вдалося розпізнати аудіо")
            except sr.RequestError as e:
                print(f"Не вдалося з'єднатися з сервісом розпізнавання мови; {e}")
            except sr.WaitTimeoutError:
                print("Час очікування закінчився")
            return command

    def execute_command(self, command):
        self.reload_device()
        if command == 'стоп':
            self.root.destroy()
            sys.exit()
        else:
            if command is not None:
                if "включи" in command or "виключи" in command:
                    for device in self.list_devices:
                        name_device = device['name'].lower()
                        status = device['status'][0]['value']
                        code = device['status'][0]['code']
                        device_id = device['id']

                        if name_device in command:
                            if "включи" in command:
                                if "через" in command:
                                    mnojnik = 1
                                    count = int(command.split()[3])
                                    time_what = command.split()[4]
                                    if time_what == 'минут' or time_what == 'минуту':
                                        mnojnik = 60
                                    elif time_what == 'годин':
                                        mnojnik = 120
                                    self.tts_handler.play_sound(f'{name_device} буде увімкнуто через {count} {time_what}!')
                                    threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(True, status, device_id, code)).start()
                                else:
                                    self.tts_handler.play_sound(f'Вмикаю {name_device}')
                                    self.on_off_controll_devices(True, status, device_id, code)
                                
                            elif "виключи" in command:
                                if "через" in command:
                                    mnojnik = 1
                                    count = int(command.split()[3])
                                    time_what = command.split()[4]
                                    if time_what == 'минут' or time_what == 'минуту':
                                        mnojnik = 60
                                    elif time_what == 'годин':
                                        mnojnik = 120
                                    self.tts_handler.play_sound(f'{name_device} буде вимкнуто через {count} {time_what}!')
                                    threading.Timer(count*mnojnik, self.on_off_controll_devices, args=(False, status, device_id, code)).start()
                                else:
                                    self.tts_handler.play_sound(f'Вимикаю {name_device}')
                                    self.on_off_controll_devices(False, status, device_id, code)


                        # else:
                        #     self.tts_handler.play_sound(f'Такого девайсу не знайдено')

                elif "який" in command or "яка" in command or "яке" in command:
                    if 'температура' in command:
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
                                    self.tts_handler.play_sound(text_say)
                else:
                    self.tts_handler.play_sound('Я не розумію цієї команди!')
    def on_off_controll_devices(self, value, status, device_id, code):
        
        commands = {'commands': [{'code': code, 'value': value}]}
        res = self.openapi.post(f"/v1.0/devices/{device_id}/commands", commands)

        if "msg" in res:
            msg = res['msg']
            if msg == 'device is offline':
                self.tts_handler.play_sound('Девайс офлайн')
            else:
                self.tts_handler.play_sound(msg)
            return
        if 'success' in res:
            success = res['success']
            if not success:
                msg = res['msg']
                self.tts_handler.play_sound(msg)
                return
        if status == value:
            if value:
                self.tts_handler.play_sound('Девайс вже включений')
            else:
                self.tts_handler.play_sound('Девайс вже виключений')
            return

        

