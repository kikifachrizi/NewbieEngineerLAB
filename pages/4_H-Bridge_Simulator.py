import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="Forgix H-Bridge Simulator", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; }
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
    st.info("Voltage memengaruhi kecepatan rotasi jarum secara real-time.")

# Mapping Sakelar untuk dikirim ke JS
sw_states = {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "speed": 0, "status": "Idle"}
speed_val = (v_input / 24.0) * 5 # Base speed multiplier

if command == "FORWARD":
    sw_states.update({"S1": 1, "S4": 1, "speed": speed_val, "status": "Clockwise ↻"})
elif command == "REVERSE":
    sw_states.update({"S2": 1, "sw3": 1, "S3": 1, "speed": -speed_val, "status": "Counter-Clockwise ↺"})
elif command == "BRAKE":
    sw_states.update({"S3": 1, "S4": 1, "speed": 0, "status": "Braking (Locked)"})
else:
    sw_states["status"] = "Coast / Idle"

# Metrics di Streamlit
m1, m2 = st.columns(2)
m1.metric("Motor Status", sw_states["status"])
m2.metric("Effective Power", f"{(v_input/24*100):.0f} %")

# --- JAVASCRIPT ENGINE ---
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

        let rotation = 0;
        const s1 = {sw_states['S1']}, s2 = {sw_states['S2']}, s3 = {sw_states['S3']}, s4 = {sw_states['S4']};
        const speed = {sw_states['speed']};

        function drawSwitch(x, y, state, label) {{
            const color = state ? "#00f2ff" : "#ff4b4b";
            ctx.strokeStyle = "gray";
            ctx.lineWidth = 2;
            
            // Terminal Atas
            ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 20); ctx.stroke();
            
            // Lid Sakelar
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x, y + 20);
            if (state) {{
                ctx.lineTo(x, y + 60); // Tertutup
            }} else {{
                ctx.lineTo(x + 20, y + 50); // Terbuka
            }}
            ctx.stroke();

            // Label
            ctx.fillStyle = "white";
            ctx.font = "bold 14px Arial";
            ctx.fillText(label, x - 25, y + 40);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // 1. Draw Wires (H-Pattern)
            ctx.strokeStyle = "#30363d";
            ctx.lineWidth = 2;
            ctx.strokeRect(cx - 100, cy - 100, 200, 200); // Frame Utama
            
            // Jalur Tengah (Motor)
            ctx.beginPath(); ctx.moveTo(cx - 100, cy); ctx.lineTo(cx + 100, cy); ctx.stroke();

            // 2. Draw Motor Stator
            ctx.fillStyle = "#1e2130";
            ctx.strokeStyle = "#00f2ff";
            ctx.lineWidth = 4;
            ctx.beginPath(); ctx.arc(cx, cy, 50, 0, Math.PI*2); ctx.fill(); ctx.stroke();

            // 3. Draw Rotating Shaft
            rotation += speed;
            const rad = (rotation * Math.PI) / 180;
            ctx.strokeStyle = "white";
            ctx.lineWidth = 6;
            ctx.lineCap = "round";
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(rad) * 35, cy + Math.sin(rad) * 35);
            ctx.stroke();

            // 4. Draw Switches
            drawSwitch(cx - 100, cy - 110, s1, "S1"); // Kiri Atas
            drawSwitch(cx + 100, cy - 110, s2, "S2"); // Kanan Atas
            drawSwitch(cx - 100, cy + 30, s3, "S3");  // Kiri Bawah
            drawSwitch(cx + 100, cy + 30, s4, "S4");  // Kanan Bawah
            
            // Power Indicators
            ctx.fillStyle = "orange"; ctx.fillText("+ VCC", cx - 20, cy - 120);
            ctx.fillStyle = "white"; ctx.fillText("GND", cx - 15, cy + 130);

            requestAnimationFrame(draw);
        }}
        draw();
    </script>
</body>
</html>
"""

components.html(hbridge_js, height=470)


st.info("""
**Logika Aliran Arus:**
- **FORWARD:** Jalur S1 → Motor → S4 terbuka (Arus mengalir Kiri ke Kanan).
- **REVERSE:** Jalur S2 → Motor → S3 terbuka (Arus dibalik).
- **BRAKE:** Motor dikunci karena kedua terminal terhubung ke Ground.
""")

st.divider()
st.caption("© 2026 Newbie Engineer Lab")