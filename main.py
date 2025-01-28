import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning, message='invalid escape sequence')

import threading
import time
from assistant import start_assistant
from server import start_flask



if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    start_assistant()