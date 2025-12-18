from flask import Flask, jsonify, request
import requests
import os

# ---------------- BASIC APP ----------------
app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
# Yeh variables Vercel ke Environment Variables se aayenge
OWNER = os.environ.get("OWNER", "DefaultOwner")
PRIMARY_API_URL = os.environ.get("PRIMARY_API_URL", "https://vechile2.vercel.app/api/vehicle-info")
SECONDARY_API_URL = os.environ.get("SECONDARY_API_URL", "https://flipcartstore.serv00.net/vehicle/api.php")
SECONDARY_API_KEY = os.environ.get("SECONDARY_API_KEY", "Tofficial")

# ---------------- HEALTH CHECK ----------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "Owner": OWNER,
        "config_loaded": True
    })

# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({
        "api": "Vehicle Merge API",
        "status": "running",
        "Owner": OWNER,
        "endpoints": {
            "/vehicle-merge?reg=<vehicle_no>": "Merge APIs using query parameter",
            "/health": "Health check"
        }
    })

# ---------------- VEHICLE MERGE API ----------------
@app.route("/vehicle-merge")
def vehicle_merge():
    # Get vehicle number from query parameter
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
        p = requests.get(primary_url, timeout=8)
        if p.status_code == 200:
            primary_response = p.json()
        else:
            primary_response = {
                "error": f"Primary API returned status {p.status_code}",
                "status_code": p.status_code,
                "url_used": primary_url
            }
    except Exception as e:
        primary_response = {
            "error": "Primary API failed",
            "details": str(e),
            "url_used": primary_url
        }

    # -------- SECONDARY API --------
    try:
        secondary_url = f"{SECONDARY_API_URL}?reg={vehicle_no}&key={SECONDARY_API_KEY}"
        s = requests.get(secondary_url, timeout=8)
        if s.status_code == 200:
            secondary_response = s.json()
        else:
            secondary_response = {
                "error": f"Secondary API returned status {s.status_code}",
                "status_code": s.status_code
            }
    except Exception as e:
        secondary_response = {
            "error": "Secondary API failed",
            "details": str(e)
        }

    # -------- FINAL RESPONSE --------
    return jsonify({
        "success": True,
        "query": vehicle_no,
        "primary_api_response": primary_response,
        "secondary_api_response": secondary_response,
        "Owner": OWNER
    })

if __name__ == "__main__":
    app.run(debug=True)