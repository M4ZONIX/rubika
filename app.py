import os
import time
import threading
import requests
from flask import Flask
from openai import OpenAI

app = Flask("RubikaBot")

RUBIKA_TOKEN = os.environ.get("RUBIKA_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def poll_updates():
    last_update_id = 0
    while True:
        try:
            # از روبیکا می‌پرسیم پیام جدید داری؟
            url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/getUpdates"
            payload = {"offset": last_update_id}
            response = requests.post(url, json=payload).json()
            
            if response.get("status") == "ok" and response.get("result"):
                for update in response["result"]:
                    last_update_id = update["update_id"] + 1
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg.get("chat_id")
                        text = msg.get("text")
                        if chat_id and text:
                            # فرستادن به هوش مصنوعی
                            ai_res = client.chat.completions.create(
                                model="deepseek-chat",
                                messages=[{"role": "user", "content": text}]
                            )
                            reply = ai_res.choices[0].message.content
                            # فرستادن جواب به روبیکا
                            requests.post(f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
        except Exception as e:
            print("Error:", e)
        time.sleep(3) # هر ۳ ثانیه یه بار چک می‌کنه

@app.route('/')
def home():
    return "Bot is running!"

# این خط باعث میشه ربات در پس‌زمینه مدام چک کنه
threading.Thread(target=poll_updates, daemon=True).start()
