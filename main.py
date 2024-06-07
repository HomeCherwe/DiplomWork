import threading
import time
from assistant import start_assistant
from server import start_flask

if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    start_assistant()