import os
import time
from dotenv import load_dotenv
from wakeword import Wakeword
from command_handler import CommandHandler
from tts import TTSHandler

tts_handler = TTSHandler()

def start_assistant():
    if not os.path.isfile('.env'):
        tts_handler.play_sound("Відсутні ключі доступу! Додайте їх на локальному веб-сайті!")
        print("Відсутні ключі доступу! Додайте їх на локальному веб-сайті!")
        return

    load_dotenv()
    wakeword = Wakeword(picovoice_key=os.getenv("PICOVOICE_KEY"))
    command_handler = CommandHandler(tts_handler)
    tts_handler.play_sound("Голосовий асистент запущений!")
    print("Голосовий асистент запущений!")

    def on_wakeword_detected():
        tts_handler.play_sound("Чим можу допомогти?")
        print("Чим можу допомогти?")
        command = command_handler.listen_for_command()
        command_handler.execute_command(command)

    wakeword.listen_for_wakeword(on_wakeword_detected)

