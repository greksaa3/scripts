import os
import asyncio
import threading
from flask import Flask
from bot import main

app = Flask(__name__)

@app.route('/')
def home():
    return "Roblox Script Bot is running!"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    """Запускаем бота в отдельном потоке"""
    asyncio.run(main())  # ВОТ ТАК ПРАВИЛЬНО — через asyncio.run()

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Поток завершится вместе с main
    bot_thread.start()
    
    # Запускаем Flask для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
