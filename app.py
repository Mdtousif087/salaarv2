from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------- BASIC APP ----------------
app = Flask(__name__)

OWNER = os.getenv("OWNER", "-")  # Default "-" if not set

# Get API configurations from environment variables
PRIMARY_API_BASE_URL = os.getenv("PRIMARY_API_BASE_URL", "https://anuj-rcc.vercel.app/rc")
SECONDARY_API_BASE_URL = os.getenv("SECONDARY_API_BASE_URL", "https://flipcartstore.serv00.net/vehicle/api.php")
SECONDARY_API_KEY = os.getenv("SECONDARY_API_KEY", "Tofficial")

# ---------------- HEALTH CHECK ----------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "Owner": OWNER,
        "config": {
            "primary_api_configured": bool(PRIMARY_API_BASE_URL),
            "secondary_api_configured": bool(SECONDARY_API_BASE_URL),
            "secondary_key_configured": bool(SECONDARY_API_KEY)
        }
    })

# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({
        "api": "Vehicle Merge API",
        "status": "running",
        "Owner": OWNER,
        "endpoints": {
            "/vehicle-merge?reg=UP63BJ8585": "Merge APIs (using query parameter)",
            "/health": "Health check"
        },
        "config_source": "environment_variables"
    })

# ---------------- VEHICLE MERGE API ----------------
@app.route("/vehicle-merge")
def vehicle_merge():
    # Query parameter से vehicle नंबर लें
    vehicle_no = request.args.get('reg')
    
    # अगर vehicle number नहीं दिया गया है
    if not vehicle_no:
        return jsonify({
            "success": False,
            "error": "Missing 'reg' query parameter",
            "example": "/vehicle-merge?reg=UP63BJ8585"
        }), 400
    
    primary_response = None
    secondary_response = None

    # -------- PRIMARY API --------
    if PRIMARY_API_BASE_URL:
        try:
            # Primary API: /rc?query={vehicle_no}
            primary_url = f"{PRIMARY_API_BASE_URL}?query={vehicle_no}"
            p = requests.get(primary_url, timeout=8)
            if p.status_code == 200:
                primary_response = p.json()
            else:
                primary_response = {
                    "error": "Primary API returned non-200",
                    "status_code": p.status_code,
                    "url_used": primary_url
                }
        except Exception as e:
            primary_response = {
                "error": "Primary API failed",
                "details": str(e),
                "url_used": primary_url
            }
    else:
        primary_response = {
            "error": "Primary API URL not configured"
        }

    # -------- SECONDARY API --------
    if SECONDARY_API_BASE_URL and SECONDARY_API_KEY:
        try:
            # Secondary API: /vehicle/api.php?reg={vehicle_no}&key={key}
            # यहाँ पूरा URL पहले से ही है, बस parameters add करने हैं
            secondary_url = f"{SECONDARY_API_BASE_URL}?reg={vehicle_no}&key={SECONDARY_API_KEY}"
            s = requests.get(secondary_url, timeout=8)
            if s.status_code == 200:
                secondary_response = s.json()
            else:
                secondary_response = {
                    "error": "Secondary API returned non-200",
                    "status_code": s.status_code,
                    "url_used": secondary_url
                }
        except Exception as e:
            secondary_response = {
                "error": "Secondary API failed",
                "details": str(e),
                "url_used": secondary_url
            }
    else:
        secondary_response = {
            "error": "Secondary API not configured",
            "missing": []
        }
        if not SECONDARY_API_BASE_URL:
            secondary_response["missing"].append("SECONDARY_API_BASE_URL")
        if not SECONDARY_API_KEY:
            secondary_response["missing"].append("SECONDARY_API_KEY")

    # -------- FINAL RESPONSE --------
    return jsonify({
        "success": True,
        "query": vehicle_no,
        "primary_api_response": primary_response,
        "secondary_api_response": secondary_response,
        "Owner": OWNER
    })

# Run the app
if __name__ == "__main__":
    app.run(debug=True)