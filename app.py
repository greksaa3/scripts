import os
import threading
from flask import Flask
from bot import main  # предполагаю, что в bot.py есть функция main() или запуск

app = Flask(__name__)


@app.route('/')
def home():
    return "Game Mod Bot is running!"


@app.route('/health')
def health():
    return "OK"


def run_bot():
    # Запускаем твоего бота
    main()  # или то, что у тебя запускает бота


if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)