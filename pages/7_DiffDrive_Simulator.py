import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# --- Konfigurasi Page ---
st.set_page_config(page_title="Kinematics Lab | Newbie Engineer", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #00f2ff33; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; background-color: #0b0e14; }
        [data-testid="stMetricValue"] { font-family: 'Courier New', monospace; color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics v3.4")
st.caption("Autonomous Go-to-Goal Controller - Path Planning & Execution")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01)
    
    st.divider()
    st.header("📍 Target Position")
    tx = st.number_input("Target X", value=2.0)
    ty = st.number_input("Target Y", value=1.5)
    tt = st.slider("Target Heading (°)", -180, 180, 0)
    
    st.divider()
    st.header("⚙️ Controller Gain")
    k_v = st.slider("Linear Gain (Kp-v)", 0.1, 2.0, 0.5, help="Kecepatan maju robot")
    k_w = st.slider("Angular Gain (Kp-w)", 0.5, 5.0, 2.0, help="Kecepatan belok robot")
    
    st.divider()
    if st.button("🚀 DEPLOY TO TARGET", use_container_width=True):
        st.session_state.deploy_trigger = True
        st.rerun()
    if st.button("🔄 RESET POSITION", use_container_width=True):
        st.session_state.deploy_trigger = False
        st.rerun()

# --- Metrics ---
c1, c2, c3 = st.columns(3)
c1.metric("Status", "AUTONOMOUS" if st.session_state.get('deploy_trigger') else "IDLE")
c2.metric("Target Coordinate", f"({tx}, {ty})")
c3.metric("Goal Threshold", "0.05 m")

is_deploy = "true" if st.session_state.get('deploy_trigger', False) else "false"

# --- JAVASCRIPT KINEMATIC ENGINE (WITH GO-TO-GOAL LOGIC) ---
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

        // Controller Params
        const kv = {k_v}, kw = {k_w}, L = {L};
        const targetX = {tx}, targetY = {ty};
        const targetTh = {np.radians(tt)};
        const isDeploy = {is_deploy};
        
        let x = 0, y = 0, theta = 0;
        let v = 0, w = 0;
        let path = [];
        let lastTime = 0;
        let reached = false;

        const scale = 80; 
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
            ctx.restore();
        }}

        function drawRobot(rx, ry, rth) {{
            const px = offsetX + rx * scale;
            const py = offsetY - ry * scale;

            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 2;
            ctx.beginPath();
            path.forEach((p, i) => {{
                let p_px = offsetX + p.x * scale;
                let p_py = offsetY - p.y * scale;
                if(i===0) ctx.moveTo(p_px, p_py); else ctx.lineTo(p_px, p_py);
            }});
            ctx.stroke();

            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-rth);
            ctx.fillStyle = "rgba(0, 242, 255, 0.2)";
            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(0, 0, (L/2) * scale, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            ctx.strokeStyle = "#ff4444"; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(35, 0); ctx.stroke();
            ctx.restore();
        }}

        function update(timestamp) {{
            const dt = (timestamp - lastTime) / 1000;
            if(!lastTime) {{ lastTime = timestamp; requestAnimationFrame(update); return; }}
            lastTime = timestamp;

            if (isDeploy && !reached) {{
                // --- GO TO GOAL LOGIC ---
                let dx = targetX - x;
                let dy = targetY - y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                let angleToTarget = Math.atan2(dy, dx);
                let alpha = angleToTarget - theta;

                // Normalisasi sudut (-PI to PI)
                while (alpha > Math.PI) alpha -= 2 * Math.PI;
                while (alpha < -Math.PI) alpha += 2 * Math.PI;

                if (dist > 0.05) {{
                    v = kv * dist;
                    w = kw * alpha;
                    
                    // Limit kecepatan biar gak gila
                    v = Math.min(v, 1.0);
                    w = Math.max(-2.0, Math.min(w, 2.0));
                }} else {{
                    v = 0; w = 0; reached = true;
                }}

                x += v * Math.cos(theta) * dt;
                y += v * Math.sin(theta) * dt;
                theta += w * dt;
                path.push({{x: x, y: y}});
            }}

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            drawGhost(targetX, targetY, targetTh);
            drawRobot(x, y, theta);
            
            // HUD Status
            ctx.fillStyle = "white";
            ctx.font = "14px monospace";
            ctx.fillText("Linear Vel: " + v.toFixed(2) + " m/s", 20, 30);
            ctx.fillText("Angular Vel: " + w.toFixed(2) + " rad/s", 20, 50);
            if(reached) {{
                ctx.fillStyle = "#00ff00";
                ctx.fillText("STATUS: TARGET REACHED!", 20, 80);
            }}

            requestAnimationFrame(update);
        }}
        requestAnimationFrame(update);
    </script>
</body>
</html>
"""

components.html(kinematic_js, height=620)



st.divider()
st.info("**Update v3.4:** Implementasi Controller Go-to-Goal. Robot sekarang secara cerdas menghitung $v$ dan $\omega$ untuk mencapai target koordinat.")
st.caption("© 2026 Newbie Engineer Lab")