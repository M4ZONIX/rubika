import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(name)

RUBIKA_TOKEN = os.environ.get("RUBIKA_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def get_text_and_chat(data):
    chat_id = None
    text = None
    if 'message' in data:
        msg = data['message']
        chat_id = msg.get('chat_id')
        text = msg.get('text')
    elif 'update' in data:
        update = data['update']
        if update.get('type') == 'NewMessage':
            chat_id = update.get('chat_id')
            new_msg = update.get('new_message', {})
            text = new_msg.get('text')
    return chat_id, text

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/receiveUpdate', methods=['POST'])
def receive_update():
    data = request.json
    chat_id, text = get_text_and_chat(data)
    if chat_id and text:
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": text}]
            )
            reply_text = response.choices[0].message.content
        except Exception as e:
            reply_text = "متاسفانه الان نمی‌تونم جواب بدم."
        send_url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": reply_text}
        requests.post(send_url, json=payload)
    return jsonify({"status": "ok"})

if name == 'main':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
