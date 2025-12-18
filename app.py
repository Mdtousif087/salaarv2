from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
OWNER = os.environ.get("OWNER", "SALAARTHEBOSS")
PRIMARY_API_URL = os.environ.get("PRIMARY_API_URL", "https://vechile2.vercel.app/api/vehicle-info")
SECONDARY_API_URL = os.environ.get("SECONDARY_API_URL", "https://flipcartstore.serv00.net/vehicle/api.php")
SECONDARY_API_KEY = os.environ.get("SECONDARY_API_KEY", "Tofficial")

print(f"DEBUG: OWNER = {OWNER}")
print(f"DEBUG: PRIMARY_API_URL = {PRIMARY_API_URL}")
print(f"DEBUG: SECONDARY_API_URL = {SECONDARY_API_URL}")
print(f"DEBUG: SECONDARY_API_KEY = {SECONDARY_API_KEY}")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "owner": OWNER,
        "primary_url": PRIMARY_API_URL,
        "secondary_url": SECONDARY_API_URL,
        "secondary_key_set": bool(SECONDARY_API_KEY)
    })

@app.route("/")
def home():
    return jsonify({
        "api": "Vehicle Merge API",
        "status": "running",
        "owner": OWNER,
        "endpoints": {
            "/vehicle-merge?reg=<vehicle_no>": "Merge APIs using query parameter",
            "/health": "Health check"
        }
    })

@app.route("/vehicle-merge")
def vehicle_merge():
    vehicle_no = request.args.get('reg')
    
    if not vehicle_no:
        return jsonify({
            "success": False,
            "error": "Missing 'reg' query parameter",
            "example": "/vehicle-merge?reg=UP63BJ8585"
        }), 400
    
    primary_response = None
    secondary_response = None
    
    # -------- PRIMARY API --------
    try:
        primary_url = f"{PRIMARY_API_URL}?rc={vehicle_no}"
        print(f"DEBUG: Calling Primary URL: {primary_url}")
        p = requests.get(primary_url, timeout=5)
        print(f"DEBUG: Primary API Status: {p.status_code}")
        
        if p.status_code == 200:
            primary_response = p.json()
        else:
            primary_response = {
                "error": f"Primary API returned status {p.status_code}",
                "status_code": p.status_code,
                "response_text": p.text[:100] if p.text else "No response"
            }
    except Exception as e:
        print(f"DEBUG: Primary API Exception: {str(e)}")
        primary_response = {
            "error": "Primary API failed",
            "details": str(e)
        }

    # -------- SECONDARY API --------
    try:
        secondary_url = f"{SECONDARY_API_URL}?reg={vehicle_no}&key={SECONDARY_API_KEY}"
        print(f"DEBUG: Calling Secondary URL: {secondary_url}")
        s = requests.get(secondary_url, timeout=5)
        print(f"DEBUG: Secondary API Status: {s.status_code}")
        
        if s.status_code == 200:
            secondary_response = s.json()
        else:
            secondary_response = {
                "error": f"Secondary API returned status {s.status_code}",
                "status_code": s.status_code,
                "response_text": s.text[:100] if s.text else "No response"
            }
    except Exception as e:
        print(f"DEBUG: Secondary API Exception: {str(e)}")
        secondary_response = {
            "error": "Secondary API failed",
            "details": str(e)
        }

    return jsonify({
        "owner": OWNER,
        "primary": primary_response,
        "secondary": secondary_response,
        "vehicle": vehicle_no
    })

if __name__ == "__main__":
    app.run(debug=True)