import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="PID Pro Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #3e4251; }
    </style>
""", unsafe_allow_html=True)

st.title("📟 Advanced PID Simulator")
st.caption("Real-Time Control System - Powered by High-Speed JavaScript Engine")

# --- Sidebar (Input Parameters) ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 10.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 2.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("🔄 Mode & Environment")
    mode = st.radio("System Mode", ["Manual Setpoint", "Oscillation Mode"])
    target_val = st.number_input("Target Value", value=100.0) if mode == "Manual Setpoint" else 150.0
    noise_amp = st.slider("Sensor Noise", 0.0, 10.0, 1.5)
    
    st.divider()
    st.header("🛡️ Proteksi")
    max_out = st.slider("Output Saturation", 50, 255, 255)
    st.info("Logika PID dan respons sistem dijalankan 60 FPS di sisi browser.")

# --- JAVASCRIPT PID ENGINE ---
pid_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif;">
    <canvas id="pidCanvas"></canvas>
    <script>
        const canvas = document.getElementById('pidCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 500;

        // PID Parameters from Streamlit
        const Kp = {kp};
        const Ki = {ki};
        const Kd = {kd};
        const noiseAmp = {noise_amp};
        const maxOut = {max_out};
        const mode = "{mode}";
        let target = {target_val};

        // State Variables
        let currV = 0;
        let errSum = 0;
        let lastErr = 0;
        let history = [];
        let time = 0;
        let oscTimer = 0;

        function updatePID() {{
            const dt = 0.05; // 20Hz update internal
            
            // Mode Oscillation Logic
            if (mode === "Oscillation Mode") {{
                oscTimer += dt;
                if (oscTimer >= 3.0) {{
                    target = target > 0 ? -150 : 150;
                    oscTimer = 0;
                }}
            }}

            const error = target - currV;
            errSum += error * dt;
            
            // Anti-Windup simple
            const limitI = maxOut / (Ki > 0 ? Ki : 1);
            if (errSum > limitI) errSum = limitI;
            if (errSum < -limitI) errSum = -limitI;

            const deriv = (error - lastErr) / dt;
            const output = (Kp * error) + (Ki * errSum) + (Kd * deriv);
            const pwm = Math.max(-maxOut, Math.min(maxOut, output));

            // Plant Physics (Simplified DC Motor/System)
            const noise = (Math.random() - 0.5) * noiseAmp;
            const accel = (pwm * 0.5) - (currV * 0.2); 
            currV += (accel * dt) + noise;
            lastErr = error;

            // Save to history
            history.push({{t: time, v: currV, sp: target}});
            if (history.length > 300) history.shift();
            time += dt;
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const padding = 50;
            const chartW = canvas.width - 100;
            const chartH = canvas.height - 100;
            const yScale = chartH / 400; // Range -200 to 200

            // Draw Grid
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            for(let i=0; i<=10; i++) {{
                let y = padding + (chartH/10) * i;
                ctx.beginPath(); ctx.moveTo(padding, y); ctx.lineTo(padding + chartW, y); ctx.stroke();
            }}

            // Draw Setpoint (Target) - RED
            ctx.strokeStyle = '#ff4444';
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 300) * chartW;
                let y = (canvas.height/2) - (d.sp * yScale);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw System Output - CYAN
            ctx.strokeStyle = '#00f2ff';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10; ctx.shadowColor = '#00f2ff';
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 300) * chartW;
                let y = (canvas.height/2) - (d.v * yScale);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Labels
            ctx.fillStyle = "white";
            ctx.font = "14px Arial";
            ctx.fillText("Setpoint", padding + 10, 30);
            ctx.fillStyle = "#00f2ff";
            ctx.fillText("System Output (PV)", padding + 100, 30);
            ctx.fillText(`Current: ${{currV.toFixed(2)}} V`, padding + 10, canvas.height - 20);
        }}

        function loop() {{
            updatePID();
            draw();
            requestAnimationFrame(loop);
        }}
        loop();
    </script>
</body>
</html>
"""

components.html(pid_js, height=520)

st.divider()
st.info("""
**Analisis Grafik:**
- **Steady State Error:** Jika garis biru tidak mencapai garis merah, naikkan **Ki**.
- **Overshoot:** Jika garis biru "bablas" melewati merah, turunkan **Kp** atau naikkan **Kd**.
- **Noise:** Gangguan pada garis biru mensimulasikan ketidaksempurnaan sensor asli.
""")
st.caption("© 2026 Newbie Engineer Lab")