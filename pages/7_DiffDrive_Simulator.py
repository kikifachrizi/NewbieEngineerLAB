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

st.title("⚙️ Differential Drive Kinematics v3.2")
st.caption("High-Speed Kinetic Engine - Manual Target & Auto-Path Enabled")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01)
    
    st.divider()
    st.header("🕹️ Real-Time Velocity")
    v_lin = st.slider("Linear Velocity (v) [m/s]", -1.0, 1.0, 0.4)
    w_ang = st.slider("Angular Velocity (ω) [rad/s]", -2.0, 2.0, 0.5)
    
    st.divider()
    st.header("📍 Target Position")
    tx = st.number_input("Target X", value=1.5)
    ty = st.number_input("Target Y", value=1.5)
    t_theta = st.slider("Target Heading (°)", -180, 180, 45)
    
    st.divider()
    if st.button("🚀 Deploy to Target", use_container_width=True):
        st.session_state.deploy_trigger = True
        st.rerun()
    if st.button("🔄 Reset to Origin", use_container_width=True):
        st.session_state.deploy_trigger = False
        st.rerun()

# --- Metrics ---
vr = (v_lin + (w_ang * L / 2)) / R
vl = (v_lin - (w_ang * L / 2)) / R
c1, c2, c3 = st.columns(3)
c1.metric("Right Wheel", f"{vr:.2f} rad/s")
c2.metric("Left Wheel", f"{vl:.2f} rad/s")
c3.metric("Target", f"({tx}, {ty})")

# Logic trigger
is_deploy = "true" if st.session_state.get('deploy_trigger', False) else "false"

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

        const v = {v_lin}, w = {w_ang}, L = {L};
        const targetX = {tx}, targetY = {ty}, targetTh = {t_theta * (Math.PI/180)};
        const isDeploy = {is_deploy};
        
        let x = 0, y = 0, theta = 0;
        let path = [];
        let lastTime = 0;
        const scale = 80; // Scale 1m = 80px
        const offsetX = canvas.width / 2;
        const offsetY = canvas.height / 2;

        function drawGrid() {{
            ctx.strokeStyle = "#1e2130"; ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=scale/2) {{ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }}
            for(let i=0; i<canvas.height; i+=scale/2) {{ ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke(); }}
        }}

        function drawGhost(gx, gy, gth) {{
            const px = offsetX + gx * scale;
            const py = offsetY - gy * scale;
            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-gth);
            ctx.strokeStyle = "rgba(255, 68, 68, 0.4)";
            ctx.setLineDash([5, 5]);
            ctx.beginPath(); ctx.arc(0, 0, (L/2) * scale, 0, Math.PI * 2); ctx.stroke();
            // Arrow
            ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(20,0); ctx.stroke();
            ctx.restore();
            ctx.setLineDash([]);
        }}

        function drawRobot(rx, ry, rth) {{
            const px = offsetX + rx * scale;
            const py = offsetY - ry * scale;

            // Draw Path Trace
            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 2;
            ctx.beginPath();
            path.forEach((p, i) => {{
                let p_px = offsetX + p.x * scale;
                let p_py = offsetY - p.y * scale;
                if(i===0) ctx.moveTo(p_px, p_py); else ctx.lineTo(p_px, p_py);
            }});
            ctx.stroke();

            // Draw Robot
            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-rth);
            ctx.fillStyle = "rgba(0, 242, 255, 0.2)";
            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(0, 0, (L/2) * scale, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            // Heading
            ctx.strokeStyle = "#ff4444"; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(30, 0); ctx.stroke();
            ctx.restore();
        }}

        function update(timestamp) {{
            const dt = (timestamp - lastTime) / 1000;
            if(!lastTime) {{ lastTime = timestamp; requestAnimationFrame(update); return; }}
            lastTime = timestamp;

            // Update Logic
            if (isDeploy) {{
                // Jika Deploy, robot bergerak otomatis
                x += v * Math.cos(theta) * dt;
                y += v * Math.sin(theta) * dt;
                theta += w * dt;
                path.push({{x: x, y: y}});
            }} else {{
                // Jika tidak deploy, robot snap ke origin (atau tetap di 0)
                x = 0; y = 0; theta = 0; path = [];
            }}

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            drawGhost(targetX, targetY, targetTh);
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
**Karakteristik v3.2:**
- **Ghost Target:** Bayangan merah menunjukkan posisi target $(X, Y, \theta)$ yang lo atur di sidebar.
- **🚀 Deploy to Target:** Robot akan mulai bergerak dari origin mengikuti input kecepatan $v$ dan $\omega$ lo.
- **🔄 Reset:** Mengembalikan robot ke titik $(0,0)$ dan menghapus jejak path.
""")
st.caption("© 2026 Newbie Engineer Lab")