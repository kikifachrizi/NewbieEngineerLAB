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

st.title("⚙️ Hybrid Diff-Drive Kinematics")
st.caption("Manual Teleop & Autonomous Go-to-Goal Simulator")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    
    st.divider()
    st.header("🕹️ Operation Mode")
    op_mode = st.radio("Select Mode", ["Manual Command", "Autonomous Go-to-Goal"])
    
    if op_mode == "Manual Command":
        st.subheader("Manual Controls")
        v_lin = st.slider("Linear Velocity (v)", -1.0, 1.0, 0.4)
        w_ang = st.slider("Angular Velocity (ω)", -2.0, 2.0, 0.5)
        # Dummy values for JS compatibility
        tx, ty, tt, kv, kw = 0, 0, 0, 0, 0
    else:
        st.subheader("Target & Gains")
        tx = st.number_input("Target X", value=2.0)
        ty = st.number_input("Target Y", value=1.5)
        tt = st.slider("Target Heading (°)", -180, 180, 0)
        kv = st.slider("Linear Gain (Kp-v)", 0.1, 2.0, 0.8)
        kw = st.slider("Angular Gain (Kp-w)", 0.5, 5.0, 2.5)
        # Dummy values for JS compatibility
        v_lin, w_ang = 0, 0

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 DEPLOY", use_container_width=True):
            st.session_state.active = True
    with col2:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.active = False
            st.rerun()

# --- Metrics ---
c1, c2, c3 = st.columns(3)
c1.metric("Mode", op_mode)
c2.metric("Control Status", "RUNNING" if st.session_state.get('active') else "STANDBY")
c3.metric("L/2 Offset", f"{L/2:.3f} m")

is_active = "true" if st.session_state.get('active', False) else "false"

# --- JAVASCRIPT KINEMATIC ENGINE (HYBRID) ---
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

        // Configuration
        const mode = "{op_mode}";
        const L = {L}, isActive = {is_active};
        
        // Manual Params
        const vManual = {v_lin}, wManual = {w_ang};
        
        // Auto Params
        const targetX = {tx}, targetY = {ty}, kv = {kv}, kw = {kw};
        const targetTh = {np.radians(tt)};

        // State
        let x = 0, y = 0, theta = 0;
        let v_out = 0, w_out = 0;
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

        function drawRobot(rx, ry, rth) {{
            const px = offsetX + rx * scale;
            const py = offsetY - ry * scale;

            // Path
            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 2;
            ctx.beginPath();
            path.forEach((p, i) => {{
                let pX = offsetX + p.x * scale; let pY = offsetY - p.y * scale;
                if(i===0) ctx.moveTo(pX, pY); else ctx.lineTo(pX, pY);
            }});
            ctx.stroke();

            // Target Ghost (Only in Auto Mode)
            if(mode === "Autonomous Go-to-Goal") {{
                ctx.save();
                ctx.translate(offsetX + targetX * scale, offsetY - targetY * scale);
                ctx.rotate(-targetTh);
                ctx.strokeStyle = "rgba(255, 68, 68, 0.4)"; ctx.setLineDash([5, 5]);
                ctx.beginPath(); ctx.arc(0, 0, (L/2)*scale, 0, Math.PI*2); ctx.stroke();
                ctx.restore();
            }}

            // Body
            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-rth);
            ctx.fillStyle = "rgba(0, 242, 255, 0.2)"; ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(0, 0, (L/2)*scale, 0, Math.PI*2); ctx.fill(); ctx.stroke();
            // Heading
            ctx.strokeStyle = "#ff4444"; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(35, 0); ctx.stroke();
            ctx.restore();
        }}

        function update(timestamp) {{
            const dt = (timestamp - lastTime) / 1000;
            if(!lastTime) {{ lastTime = timestamp; requestAnimationFrame(update); return; }}
            lastTime = timestamp;

            if (isActive) {{
                if (mode === "Manual Command") {{
                    v_out = vManual;
                    w_out = wManual;
                }} else {{
                    // Autonomous Logic
                    let dx = targetX - x;
                    let dy = targetY - y;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    let angleToTarget = Math.atan2(dy, dx);
                    let alpha = angleToTarget - theta;
                    while (alpha > Math.PI) alpha -= 2 * Math.PI;
                    while (alpha < -Math.PI) alpha += 2 * Math.PI;

                    if (dist > 0.05) {{
                        v_out = kv * dist;
                        w_out = kw * alpha;
                        v_out = Math.min(v_out, 1.0);
                        w_out = Math.max(-2.5, Math.min(w_out, 2.5));
                    }} else {{
                        v_out = 0; w_out = 0; reached = true;
                    }}
                }}

                x += v_out * Math.cos(theta) * dt;
                y += v_out * Math.sin(theta) * dt;
                theta += w_out * dt;
                path.push({{x: x, y: y}});
            }}

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            drawRobot(x, y, theta);
            
            // HUD
            ctx.fillStyle = "white"; ctx.font = "13px monospace";
            ctx.fillText("V: " + v_out.toFixed(2) + " m/s", 20, 30);
            ctx.fillText("W: " + w_out.toFixed(2) + " rad/s", 20, 50);
            ctx.fillText("Pose: [" + x.toFixed(2) + ", " + y.toFixed(2) + "]", 20, 70);
            if(reached && mode.includes("Auto")) {{ ctx.fillStyle = "#00ff00"; ctx.fillText("GOAL REACHED!", 20, 100); }}

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
**Hybrid Mode v3.5:**
- **Manual Mode**: Robot bergerak murni berdasarkan input $v$ dan $\omega$ lo secara terus-menerus.
- **Auto Mode**: Robot menggunakan *control law* untuk navigasi menuju titik target. 
- Klik **DEPLOY** untuk memulai pergerakan dan **RESET** untuk kembali ke titik nol.
""")
st.caption("© 2026 Newbie Engineer Lab")