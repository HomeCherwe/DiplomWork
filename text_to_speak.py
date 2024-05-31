
import os 
import torch
from IPython.display import Audio, display

from pydub import AudioSegment
from pydub.playback import play

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'model_ua.pt'

if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ua/v4_ua.pt',
                                   local_file)  

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

example_text = 'Привіт'
sample_rate = 48000
speaker='mykyta'

audio_paths = model.save_wav(text=example_text,
                             speaker=speaker,
                             sample_rate=sample_rate)

# Завантажуємо .wav файл
audio = AudioSegment.from_wav(audio_paths)

# Відтворюємо аудіо
play(audio)