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

# --- Sidebar ---
with st.sidebar:
    st.header("Control Panel")
    command = st.radio("Motor Direction", ["STOP", "FORWARD", "REVERSE", "BRAKE"])
    st.divider()
    v_input = st.slider("Input Voltage (V)", 0.0, 24.0, 12.0)
    
    st.info("Gunakan tombol di bawah jika ingin memulai dari nol derajat.")
    if st.button("🔄 Reset Total Position", use_container_width=True):
        # Trik JS: Hapus memori browser lewat iframe
        st.session_state.reset_trigger = True
        st.rerun()

# Mapping Sakelar & Speed (Hanya kirim delta speed, biarkan JS handle akumulasi)
sw_states = {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "speed": 0, "status": "Idle"}
speed_val = (v_input / 24.0) * 8 # Percepat multiplier biar lebih berasa

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

# Reset logic trigger
should_reset = "true" if st.session_state.get('reset_trigger', False) else "false"
if st.session_state.get('reset_trigger', False):
    st.session_state.reset_trigger = False

# --- JAVASCRIPT ENGINE (DENGAN LOCAL STORAGE PERSISTENCE) ---
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

        // --- PERSISTENCE ENGINE ---
        const STORAGE_KEY = 'hbridge_rotation_pos';
        let rotation = parseFloat(localStorage.getItem(STORAGE_KEY)) || 0;
        
        if ({should_reset}) {{
            rotation = 0;
            localStorage.setItem(STORAGE_KEY, 0);
        }}

        const s1 = {sw_states['S1']}, s2 = {sw_states['S2']}, s3 = {sw_states['S3']}, s4 = {sw_states['S4']};
        const speed = {sw_states['speed']};

        function drawSwitch(x, y, state, label) {{
            const color = state ? "#00f2ff" : "#ff4b4b";
            ctx.strokeStyle = "#4a4f5d"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 20); ctx.stroke();
            
            ctx.strokeStyle = color; ctx.lineWidth = 4;
            ctx.shadowBlur = state ? 10 : 0; ctx.shadowColor = color;
            ctx.beginPath(); ctx.moveTo(x, y + 20);
            if (state) ctx.lineTo(x, y + 65);
            else ctx.lineTo(x + 25, y + 55);
            ctx.stroke();
            ctx.shadowBlur = 0;

            ctx.fillStyle = "white"; ctx.font = "bold 13px Arial";
            ctx.fillText(label, x - 30, y + 45);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // Frame & Wires
            ctx.strokeStyle = "#2c313c"; ctx.lineWidth = 3;
            ctx.strokeRect(cx - 120, cy - 100, 240, 200);
            ctx.beginPath(); ctx.moveTo(cx - 120, cy); ctx.lineTo(cx + 120, cy); ctx.stroke();

            // Motor Stator (Glow effect)
            ctx.fillStyle = "#161b22"; ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(cx, cy, 55, 0, Math.PI*2); ctx.fill(); ctx.stroke();

            // --- ANIMATION UPDATE ---
            rotation += speed;
            localStorage.setItem(STORAGE_KEY, rotation); // Simpan posisi secara real-time
            
            const rad = (rotation * Math.PI) / 180;
            ctx.strokeStyle = "white"; ctx.lineWidth = 8; ctx.lineCap = "round";
            ctx.shadowBlur = 15; ctx.shadowColor = "rgba(255,255,255,0.5)";
            ctx.beginPath(); ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(rad) * 40, cy + Math.sin(rad) * 40);
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Sakelar
            drawSwitch(cx - 120, cy - 120, s1, "S1 (HS)");
            drawSwitch(cx + 120, cy - 120, s2, "S2 (HS)");
            drawSwitch(cx - 120, cy + 35, s3, "S3 (LS)");
            drawSwitch(cx + 120, cy + 35, s4, "S4 (LS)");

            // Terminal
            ctx.fillStyle = "#ffaa00"; ctx.font = "bold 14px Arial"; ctx.fillText("+VCC", cx - 18, cy - 125);
            ctx.fillStyle = "#9ea4b0"; ctx.fillText("GND", cx - 15, cy + 135);

            requestAnimationFrame(draw);
        }}
        draw();
    </script>
</body>
</html>
"""

components.html(hbridge_js, height=470)



st.info("""
**Karakteristik H-Bridge v3.0 (Persistent Memory):**
- **Client-Side Storage:** Posisi jarum sekarang disimpan di memori browser lo. 
- **Continuity:** Pindah mode (Forward ke Reverse) tidak akan mereset jarum ke nol.
- **Hardware Accuracy:** Animasi merepresentasikan inersia visual saat pergantian arah.
""")

st.divider()
st.caption("© 2026 Newbie Engineer Lab")