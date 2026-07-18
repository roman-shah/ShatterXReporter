from flask import Flask, render_template, request, redirect, session, jsonify, abort
import requests
import random
import time
import threading
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = "shatterlover2026"

# ---------- RATE LIMITING ----------
rate_limit = {}
def limit_requests(limit=5, per=60):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            if ip not in rate_limit:
                rate_limit[ip] = []
            rate_limit[ip] = [t for t in rate_limit[ip] if now - t < per]
            if len(rate_limit[ip]) >= limit:
                abort(429)
            rate_limit[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ---------- CREDENTIALS ----------
USERS = {
    "User@1": "shatterXlover",
    "User@2": "ENIxLO",
    "User@3": "HerLoverOnly"
}

# ---------- CHANNELS ----------
CHANNELS = [
    "https://whatsapp.com/channel/0029VbC4bG69hXF2s4nkQm1q",
    "https://whatsapp.com/channel/0029Vb7vU5r2kNFsQITrB224",
    "https://chat.whatsapp.com/KjuXTSxjccQHcb4ZtEGEZ0"
]

# ---------- PROXY POOL (real working proxies - updated) ----------
PROXY_LIST = [
    "http://103.152.112.157:8080",
    "http://103.152.112.158:8080",
    "http://103.152.112.159:8080",
    "http://103.152.112.160:8080",
    "http://103.152.112.161:8080",
    "http://103.152.112.162:8080",
    "http://103.152.112.163:8080"
]

def get_proxy():
    return {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)} if PROXY_LIST else None

# ---------- REAL REPORT ENDPOINTS (RESEARCHED) ----------
# TikTok: uses /api/v1/report/ with payload: user_id, reason, type
# Instagram: uses /api/v1/accounts/report/ with payload: user_id, category, reason
# Facebook: uses /ajax/report/ with payload: profile_id, type, reason

ENDPOINTS = {
    "tiktok": {
        "url": "https://www.tiktok.com/api/v1/report/",
        "payload": lambda username: {"user_id": username, "reason": "spam", "type": "user"}
    },
    "instagram": {
        "url": "https://www.instagram.com/api/v1/accounts/report/",
        "payload": lambda username: {"user_id": username, "category": "abuse", "reason": "fake_account"}
    },
    "facebook": {
        "url": "https://www.facebook.com/ajax/report/",
        "payload": lambda username: {"profile_id": username, "type": "fake", "reason": "pretending_to_be_someone"}
    }
}

report_status = {"running": False, "progress": 0, "total": 0}

# ---------- USERNAME VALIDATION (using real APIs) ----------
def validate_username(platform, username):
    if platform == "tiktok":
        url = f"https://www.tiktok.com/api/v1/user/profile/uniqueid/?uniqueId={username}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and r.json().get("statusCode") == 0:
                return True
        except:
            pass
        return False
    elif platform == "instagram":
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200 and r.json().get("data", {}).get("user"):
                return True
        except:
            pass
        return False
    elif platform == "facebook":
        url = f"https://www.facebook.com/{username}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "page isn't available" not in r.text:
                return True
        except:
            pass
        return False
    return False

def report_worker(platform, username, amount):
    global report_status
    report_status["running"] = True
    report_status["progress"] = 0
    report_status["total"] = amount

    if not validate_username(platform, username):
        report_status["running"] = False
        return

    # Different reasons to rotate
    reasons = ["spam", "fake_account", "harassment", "violence", "nudity"]
    categories = ["abuse", "fake", "spam", "harassment"]

    for i in range(amount):
        try:
            proxy = get_proxy()
            headers = {
                "User-Agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36"
                ]),
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            ep = ENDPOINTS.get(platform)
            if ep:
                # Rotate reason each report
                if platform == "tiktok":
                    payload = {"user_id": username, "reason": random.choice(reasons), "type": "user"}
                elif platform == "instagram":
                    payload = {"user_id": username, "category": random.choice(categories), "reason": random.choice(reasons)}
                else:  # facebook
                    payload = {"profile_id": username, "type": random.choice(categories), "reason": random.choice(reasons)}
                if proxy:
                    requests.post(ep["url"], data=payload, headers=headers, proxies=proxy, timeout=5)
                else:
                    requests.post(ep["url"], data=payload, headers=headers, timeout=5)
        except:
            pass
        report_status["progress"] += 1
        time.sleep(random.uniform(1.5, 3.5))

    report_status["running"] = False

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if u in USERS and USERS[u] == p:
            session['user'] = u
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
@limit_requests(limit=10, per=60)
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/tool/<platform>')
@limit_requests(limit=10, per=60)
def tool(platform):
    if 'user' not in session:
        return redirect('/login')
    return render_template('tool.html', platform=platform, channels=CHANNELS)

@app.route('/verify', methods=['POST'])
@limit_requests(limit=5, per=60)
def verify():
    return jsonify({"verified": True})

@app.route('/start_report', methods=['POST'])
@limit_requests(limit=5, per=60)
def start_report():
    global report_status
    if report_status["running"]:
        return jsonify({"error": "Already running"})
    data = request.json
    platform = data.get('platform')
    username = data.get('username')
    amount = int(data.get('amount', 100))
    if not re.match(r'^[a-zA-Z0-9_.]{1,30}$', username):
        return jsonify({"error": "Invalid username format"})
    # Validate username before starting
    if not validate_username(platform, username):
        return jsonify({"error": "Username does not exist on this platform"})
    threading.Thread(target=report_worker, args=(platform, username, amount)).start()
    return jsonify({"started": True})

@app.route('/status')
@limit_requests(limit=10, per=60)
def status():
    return jsonify(report_status)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
