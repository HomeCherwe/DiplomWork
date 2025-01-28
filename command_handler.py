import json
import speech_recognition as sr
from tuya_connector import TuyaOpenAPI
import os
import sys
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

class CommandHandler:
    def __init__(self, tts_handler, config_file='commands.json'):
        self.tts_handler = tts_handler
        self.load_env_and_connect()
        self.load_commands(config_file)

    def load_env_and_connect(self):
        from dotenv import load_dotenv
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.openapi = TuyaOpenAPI(
            os.getenv('ENDPOINT'),
            os.getenv('ACCESS_ID'),
            os.getenv('ACCESS_KEY')
        )
        self.openapi.connect()
        self.reload_device()

    def load_commands(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            self.commands = json.load(file)["commands"]

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
        for cmd in self.commands:
            if cmd["keyword"] in command:
                if cmd["action"] == "exit":
                    self.tts_handler.play_sound("Вихід з програми.")
                    print("Вихід з програми.")
                    sys.exit()
                elif cmd["action"] == "control_device":
                    device_name = self.extract_device_name(command)
                    self.control_device(device_name, cmd["value"])
                elif cmd["action"] == "check_temperature":
                    room_name = command.split(' ')[-1:][0]
                    self.check_temperature(room_name)
                return
        self.tts_handler.play_sound("Я не розумію цієї команди!")
        print("Я не розумію цієї команди!")

    def extract_device_name(self, command):
        # Функція для вилучення назви пристрою з команди
        words = command.split()
        highest_ratio = 0

        for word in words:
                for device in self.get_all_device_names():
                    match_ratio = fuzz.partial_ratio(device, word)
                    print(match_ratio)
                    print(word)
                    print(device)
                    if match_ratio > highest_ratio:
                        highest_ratio = match_ratio
                    if highest_ratio > 70:
                        return device
        self.tts_handler.play_sound("Девайс не знайдено.")
        print("Девайс не знайдено.")
        return None

    def get_all_device_names(self):
        # Отримати всі назви пристроїв з списку пристроїв
        return [device["name"].lower() for device in self.list_devices]

    def control_device(self, device_name, value):
        if not device_name:
            return
        for device in self.list_devices:
            if device_name.lower() == device['name'].lower():
                device_id = device["id"]
                code = device["status"][0]["code"]
                status = device["status"][0]["value"]
                if value:
                    self.tts_handler.play_sound(f'Вмикаю {device_name}')
                    print(f'Вмикаю {device_name}')
                else:
                    self.tts_handler.play_sound(f'Вимикаю {device_name}')
                    print(f'Вимикаю {device_name}')
                self.on_off_controll_devices(value, status, device_id, code)
        

    def check_temperature(self, room_name_partial):
        res_homes = self.openapi.get(f"/v1.0/users/{os.getenv('UID')}/homes")
        home_id = res_homes['result'][0]['home_id']

        res_rooms = self.openapi.get(f"/v1.0/homes/{home_id}/rooms")
        rooms_list = res_rooms['result']['rooms']

        best_match = None
        highest_ratio = 0
        for room in rooms_list:
            match_ratio = fuzz.partial_ratio(room_name_partial.lower(), room['name'].lower())
            if match_ratio > highest_ratio:
                highest_ratio = match_ratio
                best_match = room
        room_id = best_match['room_id'] if highest_ratio > 70 else None

        if not room_id:
            self.tts_handler.play_sound(f'Кімната {room_name_partial} не знайдена!')
            print(f'Кімната {room_name_partial} не знайдена!')
            return

        devices_in_room = self.openapi.get(f"/v1.0/homes/{home_id}/rooms/{room_id}/devices")

        if devices_in_room.get('success'):
            for device in devices_in_room['result']:
                if device['status'][0]['code'] == 'va_temperature':
                    temp = float(device['status'][0]['value'])/10
                    temp = str(temp).split('.')
                    if temp[1] == '0':
                        text_say = f"У {room_name_partial} {temp[0]} градуса!"
                    else:
                        text_say = f"У {room_name_partial} {temp[0]} і {temp[1]} градуса!"
                    self.tts_handler.play_sound(text_say)
                    return
            self.tts_handler.play_sound(f"У {room_name_partial} немає датчика температури!")
            print(f"У {room_name_partial} немає датчика температури!")
        else:
            print("Error: 'result' not found in response.")
            print("Response:", res)
        
    def on_off_controll_devices(self, value, status, device_id, code):
        
        commands = {'commands': [{'code': code, 'value': value}]}
        res = self.openapi.post(f"/v1.0/devices/{device_id}/commands", commands)
        

        if "msg" in res:
            if res['msg'] == 'device is offline':
                self.tts_handler.play_sound('Девайс офлайн')
                print('Девайс офлайн')
            else:
                self.tts_handler.play_sound(res['msg'])
                print(res['msg'])
            return
        if 'success' in res:
            success = res['success']
            if not success:
                self.tts_handler.play_sound(res['msg'])
                print(res['msg'])
                return
        if status == value:
            if value:
                self.tts_handler.play_sound('Девайс вже включений')
                print('Девайс вже включений')
            else:
                self.tts_handler.play_sound('Девайс вже виключений')
                print('Девайс вже виключений')
            return

        

