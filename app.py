from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Environment variables से values लें (Vercel में set करेंगे)
OWNER = os.environ.get("OWNER", "YourName")
PRIMARY_API = os.environ.get("PRIMARY_API", "https://anuj-rcc.vercel.app/rc")
SECONDARY_API = os.environ.get("SECONDARY_API", "https://flipcartstore.serv00.net/vehicle/api.php")
SECONDARY_KEY = os.environ.get("SECONDARY_KEY", "Tofficial")

@app.route("/")
def home():
    return jsonify({
        "message": "Vehicle API",
        "use": "/vehicle-merge?reg=UP63BJ8585",
        "owner": OWNER
    })

@app.route("/vehicle-merge")
def vehicle_merge():
    vehicle_no = request.args.get('reg')
    
    if not vehicle_no:
        return jsonify({
            "error": "Use: /vehicle-merge?reg=YOUR_VEHICLE_NO"
        }), 400
    
    # Primary API
    try:
        primary_url = f"{PRIMARY_API}?query={vehicle_no}"
        p = requests.get(primary_url, timeout=5)
        primary_data = p.json() if p.status_code == 200 else {"error": f"Status: {p.status_code}"}
    except:
        primary_data = {"error": "Primary API failed"}

    # Secondary API
    try:
        secondary_url = f"{SECONDARY_API}?reg={vehicle_no}&key={SECONDARY_KEY}"
        s = requests.get(secondary_url, timeout=5)
        secondary_data = s.json() if s.status_code == 200 else {"error": f"Status: {s.status_code}"}
    except:
        secondary_data = {"error": "Secondary API failed"}

    return jsonify({
        "vehicle": vehicle_no,
        "primary": primary_data,
        "secondary": secondary_data,
        "owner": OWNER
    })

if __name__ == "__main__":
    app.run(debug=True)