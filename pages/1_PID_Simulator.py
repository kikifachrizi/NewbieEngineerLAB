import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="PID Pro Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #3e4251; background-color: #0b0e14; }
        [data-testid="stSidebar"] { background-color: #161b22; }
    </style>
""", unsafe_allow_html=True)

st.title("📟 Advanced PID Simulator v3.0")
st.caption("High-Fidelity Control System - Precision Metrics & Auto-Scaling Enabled")

# --- Sidebar (Input Parameters) ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 10.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 2.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("🔄 Mode & Environment")
    mode = st.radio("System Mode", ["Manual Setpoint", "Oscillation Mode"])
    target_val = st.number_input("Target Value", value=100.0)
    noise_amp = st.slider("Sensor Noise", 0.0, 10.0, 1.5)
    
    st.divider()
    st.header("🛡️ Proteksi")
    max_out = st.slider("Output Saturation", 50, 255, 255)
    st.info("Logika PID berjalan 60 FPS. Engine secara otomatis menghitung karakteristik sistem.")

# --- JAVASCRIPT PID ENGINE ---
pid_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: white;">
    <div id="metrics" style="position: absolute; top: 10px; right: 20px; display: flex; gap: 20px; background: rgba(30, 33, 48, 0.8); padding: 10px 20px; border-radius: 10px; border: 1px solid #3e4251; z-index: 100;">
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 10px; text-transform: uppercase;">Peak</div><div id="m_peak" style="color: #00f2ff; font-weight: bold; font-size: 18px;">0.0</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 10px; text-transform: uppercase;">Rise Time</div><div id="m_rise" style="color: #00f2ff; font-weight: bold; font-size: 18px;">0.0s</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 10px; text-transform: uppercase;">Settling</div><div id="m_settle" style="color: #00f2ff; font-weight: bold; font-size: 18px;">0.0s</div></div>
    </div>

    <canvas id="pidCanvas"></canvas>

    <script>
        const canvas = document.getElementById('pidCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 550;

        // Params from Streamlit
        const Kp = {kp}, Ki = {ki}, Kd = {kd};
        const noiseAmp = {noise_amp}, maxOut = {max_out}, mode = "{mode}";
        let target = {target_val};

        // States
        let currV = 0, errSum = 0, lastErr = 0;
        let history = [], time = 0, oscTimer = 0;
        
        // Karakteristik Sistem
        let startTime = 0, peakVal = 0, riseTime = 0, settlingTime = 0;

        function updatePID() {{
            const dt = 0.016; // 60Hz
            
            if (mode === "Oscillation Mode") {{
                oscTimer += dt;
                if (oscTimer >= 3.0) {{
                    target = target > 0 ? -{target_val} : {target_val};
                    oscTimer = 0;
                    peakVal = 0; riseTime = 0; settlingTime = 0; // Reset metrics on toggle
                }}
            }}

            const error = target - currV;
            errSum += error * dt;
            
            // Anti-Windup
            const limitI = maxOut / (Ki > 0 ? Ki : 1);
            errSum = Math.max(-limitI, Math.min(limitI, errSum));

            const deriv = (error - lastErr) / dt;
            const output = (Kp * error) + (Ki * errSum) + (Kd * deriv);
            const pwm = Math.max(-maxOut, Math.min(maxOut, output));

            // Plant Physics
            const noise = (Math.random() - 0.5) * noiseAmp;
            const accel = (pwm * 0.8) - (currV * 0.4); 
            currV += (accel * dt) + noise;
            lastErr = error;

            // Metrics Calculation
            if(Math.abs(currV) > Math.abs(peakVal)) peakVal = currV;
            if(!riseTime && Math.abs(currV) >= Math.abs(target * 0.9)) riseTime = time;
            if(Math.abs(error) > Math.abs(target * 0.05)) settlingTime = time;

            history.push({{t: time, v: currV, sp: target}});
            if (history.length > 400) history.shift();
            time += dt;

            // Update DOM Metrics
            document.getElementById('m_peak').innerText = peakVal.toFixed(1);
            document.getElementById('m_rise').innerText = riseTime ? riseTime.toFixed(2) + "s" : "---";
            document.getElementById('m_settle').innerText = settlingTime > 0.5 ? settlingTime.toFixed(2) + "s" : "---";
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const padding = 60;
            const chartW = canvas.width - 120;
            const chartH = canvas.height - 120;
            
            // AUTO-SCALING LOGIC
            // Mencari nilai max di history untuk scale yang pas
            const maxHist = Math.max(...history.map(d => Math.abs(d.v)), Math.abs(target), 10);
            const yScale = (chartH / 2.2) / maxHist; 

            // Draw Grid & Axes
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for(let i=-2; i<=2; i++) {{
                let y = (canvas.height/2) - (i * (maxHist/2) * yScale);
                ctx.moveTo(padding, y); ctx.lineTo(padding + chartW, y);
                ctx.fillStyle = "#4a4f5d";
                ctx.fillText((i * maxHist/2).toFixed(0), padding - 40, y + 5);
            }}
            ctx.stroke();

            // Draw Setpoint (Target) - Neon Red
            ctx.strokeStyle = '#ff4444';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 8]);
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 400) * chartW;
                let y = (canvas.height/2) - (d.sp * yScale);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw System Output - Hyper Cyan Glow
            ctx.strokeStyle = '#00f2ff';
            ctx.lineWidth = 4;
            ctx.shadowBlur = 15; ctx.shadowColor = '#00f2ff';
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 400) * chartW;
                let y = (canvas.height/2) - (d.v * yScale);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Legend
            ctx.fillStyle = "white";
            ctx.font = "bold 14px sans-serif";
            ctx.fillText("LIVE TELEMETRY", padding, 30);
            ctx.fillStyle = "#ff4444"; ctx.fillText("■ Target", padding + 150, 30);
            ctx.fillStyle = "#00f2ff"; ctx.fillText("■ System Output", padding + 230, 30);
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

components.html(pid_js, height=580)

st.divider()
st.info("""
**Karakteristik Respon:**
- **Auto-Scaling:** Grafik secara dinamis menyesuaikan zoom berdasarkan nilai target agar fluktuasi sekecil apapun terlihat jelas.
- **Precision Metrics:** Peak, Rise Time, dan Settling Time dihitung secara real-time di sisi client.
""")
st.caption("© 2026 Newbie Engineer Lab")