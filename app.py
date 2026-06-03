import os
import asyncio
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Roblox Script Bot is running!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    """Запускаем Flask в фоновом потоке (а не бота)"""
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False, threaded=True)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Бота запускаем в главном потоке
    from bot import main
    asyncio.run(main())
