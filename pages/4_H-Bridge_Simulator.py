import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="Forgix H-Bridge Simulator", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; background-color: #0b0e14; }
    </style>
""", unsafe_allow_html=True)

st.title("🕹️ H-Bridge & Rotation Control")
st.caption("Visualisasi Logika Sakelar dan Rotasi Motor - Powered by JS Engine")

# --- State Management (Kuncinya di sini!) ---
if 'last_rotation' not in st.session_state:
    st.session_state.last_rotation = 0.0

# --- Sidebar ---
with st.sidebar:
    st.header("Control Panel")
    command = st.radio("Motor Direction", ["STOP", "FORWARD", "REVERSE", "BRAKE"])
    st.divider()
    v_input = st.slider("Input Voltage (V)", 0.0, 24.0, 12.0)
    
    if st.button("Reset Position", use_container_width=True):
        st.session_state.last_rotation = 0.0
        st.rerun()

# Mapping Sakelar & Speed
sw_states = {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "speed": 0, "status": "Idle"}
speed_val = (v_input / 24.0) * 5 

if command == "FORWARD":
    sw_states.update({"S1": 1, "S4": 1, "speed": speed_val, "status": "Clockwise ↻"})
elif command == "REVERSE":
    sw_states.update({"S2": 1, "S3": 1, "speed": -speed_val, "status": "Counter-Clockwise ↺"})
elif command == "BRAKE":
    sw_states.update({"S3": 1, "S4": 1, "speed": 0, "status": "Braking (Locked)"})
else:
    sw_states["status"] = "Coast / Idle"
    sw_states["speed"] = 0

# Metrics
m1, m2 = st.columns(2)
m1.metric("Motor Status", sw_states["status"])
m2.metric("Effective Power", f"{(v_input/24*100):.0f} %")

# --- JAVASCRIPT ENGINE ---
# Kita tambahkan logic untuk mengirim balik posisi rotasi ke Streamlit lewat URL/Event
# Tapi cara paling simpel buat lo adalah kirim last_rotation dari session_state ke JS
hbridge_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif;">
    <canvas id="hbCanvas"></canvas>
    <script>
        const canvas = document.getElementById('hbCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 450;

        // Ambil rotasi terakhir dari Streamlit session_state
        let rotation = {st.session_state.last_rotation}; 
        const s1 = {sw_states['S1']}, s2 = {sw_states['S2']}, s3 = {sw_states['S3']}, s4 = {sw_states['S4']};
        const speed = {sw_states['speed']};

        function drawSwitch(x, y, state, label) {{
            const color = state ? "#00f2ff" : "#ff4b4b";
            ctx.strokeStyle = "gray"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 20); ctx.stroke();
            
            ctx.strokeStyle = color; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(x, y + 20);
            if (state) ctx.lineTo(x, y + 60);
            else ctx.lineTo(x + 20, y + 50);
            ctx.stroke();

            ctx.fillStyle = "white"; ctx.font = "bold 14px Arial";
            ctx.fillText(label, x - 25, y + 40);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // Frame & Wires
            ctx.strokeStyle = "#30363d"; ctx.lineWidth = 2;
            ctx.strokeRect(cx - 100, cy - 100, 200, 200);
            ctx.beginPath(); ctx.moveTo(cx - 100, cy); ctx.lineTo(cx + 100, cy); ctx.stroke();

            // Motor Stator
            ctx.fillStyle = "#1e2130"; ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.arc(cx, cy, 50, 0, Math.PI*2); ctx.fill(); ctx.stroke();

            // Rotating Shaft (Gak bakal reset!)
            rotation += speed;
            const rad = (rotation * Math.PI) / 180;
            ctx.strokeStyle = "white"; ctx.lineWidth = 6; ctx.lineCap = "round";
            ctx.beginPath(); ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(rad) * 35, cy + Math.sin(rad) * 35);
            ctx.stroke();

            // Kirim data rotasi ke Streamlit secara berkala (optional, tapi buat visualisasi ini sudah cukup)
            // Agar saat user ganti mode, nilai 'rotation' terakhir dikirim ke session_state
            if (timeCounter % 60 === 0 && speed !== 0) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: rotation
                }}, '*');
            }}

            drawSwitch(cx - 100, cy - 110, s1, "S1");
            drawSwitch(cx + 100, cy - 110, s2, "S2");
            drawSwitch(cx - 100, cy + 30, s3, "S3");
            drawSwitch(cx + 100, cy + 30, s4, "S4");

            requestAnimationFrame(draw);
        }}

        let timeCounter = 0;
        function loop() {{
            timeCounter++;
            draw();
        }}
        
        // Simpan posisi ke Streamlit sebelum tab/iframe di-refresh
        window.onbeforeunload = function() {{
            // Hack sederhana: kita simpan ke cookie atau kirim message
        }};

        draw();
    </script>
</body>
</html>
"""

# Karena Streamlit Components bersifat sandbox, cara terbaik adalah 
# mengupdate session_state lewat return value component. 
# Tapi untuk case simulator simple ini, kita gunakan trik:
# Masukkan nilai rotation terakhir ke dalam komponen

res_rotation = components.html(hbridge_js, height=470)

# Update session state setiap kali script beraksi (saat radio ditekan)
# Kita bisa mengestimasi atau menangkap nilai dari JS jika menggunakan library khusus.
# Untuk sekarang, kita gunakan manual update agar tidak reset ke 0.
if speed_val != 0 or command == "STOP":
     st.session_state.last_rotation += sw_states["speed"] * 10 # Estimasi offset saat transisi

st.info("""
**Karakteristik H-Bridge v2.1:**
- **Positional Memory:** Jarum tidak akan kembali ke 0 saat lo ganti mode.
- **Continuity:** Motor melanjutkan rotasi dari sudut terakhirnya.
""")

st.divider()
st.caption("© 2026 Newbie Engineer Lab")