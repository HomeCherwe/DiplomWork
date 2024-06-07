import os
from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import signal
import psutil
import subprocess
from assistant import tts_handler

def start_flask():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        error_message = ""
        if request.method == 'POST':
            access_id = request.form['access_id']
            access_key = request.form['access_key']
            end_point = request.form.get('end_point', 'https://openapi.tuyaeu.com')
            uid = request.form['uid']
            picovoice_key = request.form['picovoice_key']
            
            if not access_id or not access_key or not uid or not picovoice_key:
                error_message = "Всі поля повинні бути заповнені!"
            else:
                if save_env(access_id, access_key, end_point, uid, picovoice_key):
                    tts_handler.play_sound("Данні збережено! Перезавантажте прилад")
                else:
                    error_message = "Помилка при запису до .env файлу."
        
        return render_template_string('''
            <!doctype html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Налаштування ключів</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 400px;
                        box-sizing: border-box;
                    }
                    h1 {
                        text-align: center;
                        color: #333;
                    }
                    label {
                        display: block;
                        margin-top: 10px;
                        color: #555;
                    }
                    input[type="text"], input[type="password"] {
                        width: 100%;
                        padding: 10px;
                        margin-top: 5px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        box-sizing: border-box;
                    }
                    input[type="submit"] {
                        width: 100%;
                        padding: 10px;
                        margin-top: 20px;
                        border: none;
                        border-radius: 4px;
                        background-color: #28a745;
                        color: white;
                        font-size: 16px;
                        cursor: pointer;
                    }
                    input[type="submit"]:hover {
                        background-color: #218838;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Введіть ключі</h1>
                    <form method="post">
                        <label for="access_id">ACCESS_ID:</label>
                        <input type="text" id="access_id" name="access_id" required>
                        <label for="access_key">ACCESS_KEY:</label>
                        <input type="text" id="access_key" name="access_key" required>
                        <label for="end_point">ENDPOINT (за замовчуванням https://openapi.tuyaeu.com):</label>
                        <input type="text" id="end_point" name="end_point" value="https://openapi.tuyaeu.com">
                        <label for="uid">UID:</label>
                        <input type="text" id="uid" name="uid" required>
                        <label for="picovoice_key">PICOVOICE_KEY:</label>
                        <input type="text" id="picovoice_key" name="picovoice_key" required>
                        <input type="submit" value="Зберегти">
                    </form>
                </div>
            </body>
            </html>
        ''', error_message=error_message)
    
    def save_env(access_id, access_key, end_point, uid, picovoice_key):
        try:
            with open('.env', 'w') as f:
                f.write(f'ACCESS_ID={access_id}\n')
                f.write(f'ACCESS_KEY={access_key}\n')
                f.write(f'ENDPOINT={end_point}\n')
                f.write(f'UID={uid}\n')
                f.write(f'PICOVOICE_KEY={picovoice_key}\n')
            return True
        except Exception as e:
            print(str(e))
            return False

    app.run(port=5000)

if __name__ == "__main__":
    start_flask()

