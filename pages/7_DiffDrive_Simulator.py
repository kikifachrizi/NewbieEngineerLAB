import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="Kinematics Lab | Newbie Engineer", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #00f2ff33; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; background-color: #0b0e14; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics")
st.caption("High-Speed Kinetic Engine - Real-Time Path Tracing")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01)
    
    st.divider()
    st.header("🕹️ Real-Time Control")
    v_lin = st.slider("Linear Velocity (v) [m/s]", -1.0, 1.0, 0.4)
    w_ang = st.slider("Angular Velocity (ω) [rad/s]", -2.0, 2.0, 0.5)
    
    st.divider()
    if st.button("🔄 Reset Animation", use_container_width=True):
        st.rerun()

# --- Inverse Kinematics Calculation ---
vr = (v_lin + (w_ang * L / 2)) / R
vl = (v_lin - (w_ang * L / 2)) / R

c1, c2, c3 = st.columns(3)
c1.metric("Right Wheel", f"{vr:.2f} rad/s")
c2.metric("Left Wheel", f"{vl:.2f} rad/s")
c3.metric("L/2 Radius", f"{L/2:.3f} m")

# --- JAVASCRIPT KINEMATIC ENGINE ---
kinematic_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif;">
    <canvas id="kinCanvas"></canvas>
    <script>
        const canvas = document.getElementById('kinCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 600;

        // Params from Streamlit
        const v = {v_lin};
        const w = {w_ang};
        const L = {L};
        
        // Robot State
        let x = 0, y = 0, theta = 0;
        let path = [];
        let lastTime = 0;

        // Koordinat Konversi (Metre to Pixel)
        const scale = 100; // 1 meter = 100 pixels
        const offsetX = canvas.width / 2;
        const offsetY = canvas.height / 2;

        function drawRobot(rx, ry, rth) {{
            const px = offsetX + rx * scale;
            const py = offsetY - ry * scale; // Y inverted in canvas

            // 1. Draw Path
            ctx.strokeStyle = "#00f2ff";
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            path.forEach((p, i) => {{
                let p_px = offsetX + p.x * scale;
                let p_py = offsetY - p.y * scale;
                if(i===0) ctx.moveTo(p_px, p_py); else ctx.lineTo(p_px, p_py);
            }});
            ctx.stroke();
            ctx.setLineDash([]);

            // 2. Draw Robot Body
            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-rth); // Rotate canvas (negative because Y is inverted)
            
            // Body Circle
            ctx.fillStyle = "rgba(0, 242, 255, 0.2)";
            ctx.strokeStyle = "white";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(0, 0, (L/2) * scale, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Heading Arrow
            ctx.strokeStyle = "#ff4444";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(25, 0); // Pointing to the right (local X)
            ctx.stroke();
            
            // Arrow Head
            ctx.fillStyle = "#ff4444";
            ctx.beginPath();
            ctx.moveTo(25, -5); ctx.lineTo(35, 0); ctx.lineTo(25, 5); ctx.fill();

            ctx.restore();
        }}

        function update(timestamp) {{
            const dt = (timestamp - lastTime) / 1000;
            if(!lastTime) {{ lastTime = timestamp; requestAnimationFrame(update); return; }}
            lastTime = timestamp;

            // --- KINEMATIC MODEL ---
            x += v * Math.cos(theta) * dt;
            y += v * Math.sin(theta) * dt;
            theta += w * dt;

            // Simpan jejak
            path.push({{x: x, y: y}});
            if(path.length > 1000) path.shift();

            // Draw everything
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw Grid
            ctx.strokeStyle = "#1e2130";
            ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=50) {{
                ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke();
            }}
            for(let i=0; i<canvas.height; i+=50) {{
                ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke();
            }}

            drawRobot(x, y, theta);
            requestAnimationFrame(update);
        }}

        requestAnimationFrame(update);
    </script>
</body>
</html>
"""

components.html(kinematic_js, height=620)



st.divider()
st.info("""
**User Guide:**
- Robot akan mulai berjalan secara otomatis dari titik **(0,0)**.
- Ubah **v** (Linear) dan **ω** (Angular) di sidebar untuk melihat perubahan arah robot secara langsung.
- Animasi ini berjalan di sisi browser (Client-side) untuk menjamin pergerakan **60 FPS** yang mulus.
""")
st.caption("© 2026 Newbie Engineer Lab | Specialized for AMR TIFA R&D")