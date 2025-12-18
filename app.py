from flask import Flask, jsonify, request
import requests

# ---------------- BASIC APP ----------------
app = Flask(__name__)

OWNER = "-"

# ---------------- HEALTH CHECK ----------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "Owner": OWNER
    })

# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({
        "api": "Vehicle Merge API",
        "status": "running",
        "Owner": OWNER,
        "endpoints": {
            "/vehicle-merge?reg=UP63BJ8585": "Merge Anuj RCC + Flipcartstore APIs (using query parameter)",
            "/health": "Health check"
        }
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

    # -------- PRIMARY API (anuj-rcc) --------
    try:
        primary_url = f"https://anuj-rcc.vercel.app/rc?query={vehicle_no}"
        p = requests.get(primary_url, timeout=8)
        if p.status_code == 200:
            primary_response = p.json()
        else:
            primary_response = {
                "error": "Primary API returned non-200",
                "status_code": p.status_code
            }
    except Exception as e:
        primary_response = {
            "error": "Primary API failed",
            "details": str(e)
        }

    # -------- SECONDARY API (flipcartstore) --------
    try:
        secondary_url = (
            "https://flipcartstore.serv00.net/vehicle/api.php"
            f"?reg={vehicle_no}&key=Tofficial"
        )
        s = requests.get(secondary_url, timeout=8)
        if s.status_code == 200:
            secondary_response = s.json()
        else:
            secondary_response = {
                "error": "Secondary API returned non-200",
                "status_code": s.status_code
            }
    except Exception as e:
        secondary_response = {
            "error": "Secondary API failed",
            "details": str(e)
        }

    # -------- FINAL PURE COPY-PASTE RESPONSE --------
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
