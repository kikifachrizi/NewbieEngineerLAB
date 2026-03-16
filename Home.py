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

st.title("⚙️ Diff-Drive Kinematics v3.6")
st.caption("Manual Timer & Autonomous Target - Precision Engineering Mode")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.005, format="%.3f")
    
    st.divider()
    st.header("🕹️ Operation Mode")
    op_mode = st.radio("Select Mode", ["Manual Command", "Autonomous Go-to-Goal"])
    
    if op_mode == "Manual Command":
        st.subheader("Manual Controls")
        v_lin = st.slider("Linear Velocity (v)", -1.0, 1.0, 0.4)
        w_ang = st.slider("Angular Velocity (ω)", -2.0, 2.0, 0.5)
        sim_limit = st.slider("Movement Duration (s)", 1.0, 20.0, 5.0, step=0.5)
        # Placeholder for JS
        tx, ty, tt, kv, kw = 0, 0, 0, 0, 0
    else:
        st.subheader("Target & Gains")
        tx = st.number_input("Target X", value=2.0)
        ty = st.number_input("Target Y", value=1.5)
        tt = st.slider("Target Heading (°)", -180, 180, 0)
        kv = st.slider("Linear Gain (Kp-v)", 0.1, 2.0, 0.8)
        kw = st.slider("Angular Gain (Kp-w)", 0.5, 5.0, 2.5)
        # Placeholder for JS
        v_lin, w_ang, sim_limit = 0, 0, 0

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 DEPLOY", use_container_width=True):
            st.session_state.active = True
    with col2:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.active = False
            st.rerun()

# --- Metrics (Inverse Kinematics) ---
# Kita tampilkan kecepatan sudut roda (rad/s) yang dibutuhkan
if op_mode == "Manual Command":
    vr_rads = (v_lin + (w_ang * L / 2)) / R
    vl_rads = (v_lin - (w_ang * L / 2)) / R
else:
    vr_rads, vl_rads = 0, 0 # Dinamis di JS kalau Auto

c1, c2, c3 = st.columns(3)
c1.metric("Mode", op_mode)
if op_mode == "Manual Command":
    c2.metric("Wheel Speed (R/L)", f"{vr_rads:.1f} | {vl_rads:.1f} rad/s")
else:
    c2.metric("Status", "GO-TO-GOAL")
c3.metric("Wheel Circum", f"{2 * np.pi * R:.3f} m")

is_active = "true" if st.session_state.get('active', False) else "false"

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

        // Config
        const mode = "{op_mode}";
        const L = {L}, R = {R}, isActive = {is_active};
        
        // Manual Params
        const vManual = {v_lin}, wManual = {w_ang}, simLimit = {sim_limit};
        
        // Auto Params
        const targetX = {tx}, targetY = {ty}, kv = {kv}, kw = {kw}, targetTh = {np.radians(tt)};

        // State
        let x = 0, y = 0, theta = 0, timeElapsed = 0;
        let v_out = 0, w_out = 0, path = [];
        let lastTime = 0, reached = false;

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

            // Trace
            ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 2;
            ctx.beginPath();
            path.forEach((p, i) => {{
                let pX = offsetX + p.x * scale; let pY = offsetY - p.y * scale;
                if(i===0) ctx.moveTo(pX, pY); else ctx.lineTo(pX, pY);
            }});
            ctx.stroke();

            // Target (Auto only)
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
            ctx.fillStyle = "rgba(0, 242, 255, 0.1)"; ctx.strokeStyle = "#00f2ff"; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(0, 0, (L/2)*scale, 0, Math.PI*2); ctx.fill(); ctx.stroke();
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
                    if (timeElapsed < simLimit) {{
                        v_out = vManual;
                        w_out = wManual;
                        timeElapsed += dt;
                    }} else {{
                        v_out = 0; w_out = 0; reached = true;
                    }}
                }} else {{
                    let dx = targetX - x; let dy = targetY - y;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    let angleToTarget = Math.atan2(dy, dx);
                    let alpha = angleToTarget - theta;
                    while (alpha > Math.PI) alpha -= 2 * Math.PI;
                    while (alpha < -Math.PI) alpha += 2 * Math.PI;

                    if (dist > 0.05) {{
                        v_out = kv * dist;
                        w_out = kw * alpha;
                        v_out = Math.min(v_out, 1.2);
                        w_out = Math.max(-3, Math.min(w_out, 3));
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
            ctx.fillStyle = "white"; ctx.font = "14px monospace";
            ctx.fillText("Time: " + (mode.includes("Manual") ? timeElapsed.toFixed(1) + " / " + simLimit + "s" : "Live"), 20, 30);
            ctx.fillText("V: " + v_out.toFixed(2) + " m/s", 20, 55);
            ctx.fillText("W: " + w_out.toFixed(2) + " rad/s", 20, 75);
            
            // Calc Wheel Speed Live for UI
            let vr = (v_out + (w_out * L / 2)) / R;
            let vl = (v_out - (w_out * L / 2)) / R;
            ctx.fillText("ω_R: " + vr.toFixed(1) + " rad/s", 20, 105);
            ctx.fillText("ω_L: " + vl.toFixed(1) + " rad/s", 20, 125);

            if(reached) {{ ctx.fillStyle = "#00ff00"; ctx.fillText("STATUS: FINISHED", 20, 155); }}

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
**Update v3.6:**
- **Wheel Radius ($R$):** Mempengaruhi kalkulasi kecepatan sudut roda ($\omega_R, \omega_L$).
- **Manual Timer:** Robot akan berhenti otomatis setelah durasi yang ditentukan habis.
- **Live HUD:** Memperlihatkan kecepatan roda secara real-time saat robot bergerak.
""")
st.caption("© 2026 Newbie Engineer Lab")