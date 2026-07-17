from flask import Flask, render_template, request, redirect, session, jsonify
import requests
import random
import time
import threading

app = Flask(__name__)
app.secret_key = "shatterlover2026"

# 🔐 TERI CREDENTIALS (hidden from public)
USERS = {
    "User@1": "shatterXlover",
    "User@2": "ENIxLO",
    "User@3": "HerLoverOnly"
}

CHANNELS = [
    "https://whatsapp.com/channel/0029Vb7vU5r2kNFsQITrB224",
    "https://chat.whatsapp.com/KjuXTSxjccQHcb4ZtEGEZ0",
    "https://whatsapp.com/channel/0029VbC4bG69hXF2s4nkQm1q"
]

PROXY_LIST = [
    "http://103.152.112.157:8080",
    "http://103.152.112.158:8080",
    "http://103.152.112.159:8080",
    "http://103.152.112.160:8080",
    "http://103.152.112.161:8080"
]

report_status = {"running": False, "progress": 0, "total": 0}

def get_proxy():
    return {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)} if PROXY_LIST else None

def report_worker(platform, username, amount):
    global report_status
    report_status["running"] = True
    report_status["progress"] = 0
    report_status["total"] = amount

    endpoints = {
        "tiktok": {"url": "https://www.tiktok.com/api/v1/report/", "payload": {"user_id": username, "reason": "spam"}},
        "instagram": {"url": "https://www.instagram.com/api/v1/accounts/report/", "payload": {"user_id": username, "category": "abuse"}},
        "facebook": {"url": "https://www.facebook.com/ajax/report/", "payload": {"profile_id": username, "type": "fake"}}
    }

    for i in range(amount):
        try:
            proxy = get_proxy()
            headers = {"User-Agent": random.choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)", "Mozilla/5.0 (Linux; Android 11)"])}
            ep = endpoints.get(platform)
            if ep:
                if proxy:
                    requests.post(ep["url"], data=ep["payload"], headers=headers, proxies=proxy, timeout=5)
                else:
                    requests.post(ep["url"], data=ep["payload"], headers=headers, timeout=5)
        except:
            pass
        report_status["progress"] += 1
        time.sleep(random.uniform(1, 3))
    
    report_status["running"] = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in USERS and USERS[u] == p:
            session['user'] = u
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/tool/<platform>')
def tool(platform):
    if 'user' not in session:
        return redirect('/login')
    return render_template('tool.html', platform=platform, channels=CHANNELS)

@app.route('/verify', methods=['POST'])
def verify():
    return jsonify({"verified": True})

@app.route('/start_report', methods=['POST'])
def start_report():
    global report_status
    if report_status["running"]:
        return jsonify({"error": "Already running"})
    data = request.json
    threading.Thread(target=report_worker, args=(data['platform'], data['username'], int(data['amount']))).start()
    return jsonify({"started": True})

@app.route('/status')
def status():
    return jsonify(report_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)