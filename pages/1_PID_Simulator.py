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

st.title("📟 Advanced PID Simulator v3.2")
st.caption("Precision Auto-Scaling Engine - High Visibility Mode")

# --- Sidebar ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 10.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 2.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("🔄 Environment")
    mode = st.radio("System Mode", ["Manual Setpoint", "Oscillation Mode"])
    target_val = st.number_input("Target Value", value=100.0)
    noise_amp = st.slider("Sensor Noise", 0.0, 10.0, 1.5)
    
    st.divider()
    max_out = st.slider("Output Saturation", 50, 255, 255)

# --- JAVASCRIPT PID ENGINE ---
pid_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif; color: white;">
    <div id="metrics" style="position: absolute; top: 15px; right: 25px; display: flex; gap: 20px; background: rgba(20, 23, 33, 0.9); padding: 12px 25px; border-radius: 12px; border: 1px solid #00f2ff33; z-index: 100; box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);">
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Peak</div><div id="m_peak" style="color: #00f2ff; font-weight: bold; font-size: 20px; font-family: monospace;">0.0</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Rise Time</div><div id="m_rise" style="color: #00f2ff; font-weight: bold; font-size: 20px; font-family: monospace;">0.0s</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Settling</div><div id="m_settle" style="color: #00f2ff; font-weight: bold; font-size: 20px; font-family: monospace;">0.0s</div></div>
    </div>

    <canvas id="pidCanvas"></canvas>

    <script>
        const canvas = document.getElementById('pidCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 550;

        const Kp = {kp}, Ki = {ki}, Kd = {kd};
        const noiseAmp = {noise_amp}, maxOut = {max_out}, mode = "{mode}";
        let target = {target_val};

        let currV = 0, errSum = 0, lastErr = 0;
        let history = [], time = 0, oscTimer = 0;
        let peakVal = 0, riseTime = 0, settlingTime = 0;

        function updatePID() {{
            const dt = 0.016;
            if (mode === "Oscillation Mode") {{
                oscTimer += dt;
                if (oscTimer >= 4.0) {{
                    target = target > 0 ? -{target_val} : {target_val};
                    oscTimer = 0;
                    peakVal = 0; riseTime = 0; settlingTime = 0;
                }}
            }}

            const error = target - currV;
            errSum += error * dt;
            const limitI = maxOut / (Ki > 0 ? Ki : 1);
            errSum = Math.max(-limitI, Math.min(limitI, errSum));

            const deriv = (error - lastErr) / dt;
            const output = (Kp * error) + (Ki * errSum) + (Kd * deriv);
            const pwm = Math.max(-maxOut, Math.min(maxOut, output));

            const noise = (Math.random() - 0.5) * noiseAmp;
            const accel = (pwm * 0.8) - (currV * 0.4); 
            currV += (accel * dt) + noise;
            lastErr = error;

            if(Math.abs(currV) > Math.abs(peakVal)) peakVal = currV;
            if(!riseTime && Math.abs(currV) >= Math.abs(target * 0.9)) riseTime = time;
            if(Math.abs(error) > Math.abs(target * 0.05)) settlingTime = time;

            history.push({{t: time, v: currV, sp: target}});
            if (history.length > 400) history.shift();
            time += dt;

            document.getElementById('m_peak').innerText = peakVal.toFixed(1);
            document.getElementById('m_rise').innerText = riseTime ? riseTime.toFixed(2) + "s" : "---";
            document.getElementById('m_settle').innerText = settlingTime > 0.5 ? settlingTime.toFixed(2) + "s" : "---";
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const padding = 70;
            const chartW = canvas.width - 120;
            const chartH = canvas.height - 140;

            // --- SMART SCALING ENGINE ---
            const allValues = history.map(d => d.v).concat([target]);
            const minVal = Math.min(...allValues);
            const maxVal = Math.max(...allValues);
            const range = Math.max(Math.abs(maxVal - minVal), 20); // Minimal range 20 unit
            
            const yMin = minVal - (range * 0.2); // Kasih nafas 20% di bawah
            const yMax = maxVal + (range * 0.2); // Kasih nafas 20% di atas
            const yRange = yMax - yMin;

            function getY(val) {{
                return (padding + chartH) - ((val - yMin) / yRange) * chartH;
            }}

            // Draw Grid & Labels
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            ctx.font = "12px monospace";
            ctx.fillStyle = "#4a4f5d";
            for(let i=0; i<=5; i++) {{
                let val = yMin + (yRange / 5) * i;
                let y = getY(val);
                ctx.beginPath(); ctx.moveTo(padding, y); ctx.lineTo(padding + chartW, y); ctx.stroke();
                ctx.fillText(val.toFixed(0), padding - 45, y + 4);
            }}

            // Setpoint Line
            ctx.strokeStyle = '#ff4444';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 400) * chartW;
                let y = getY(d.sp);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.setLineDash([]);

            // System Output Line (Glow Cyan)
            ctx.strokeStyle = '#00f2ff';
            ctx.lineWidth = 4;
            ctx.shadowBlur = 15; ctx.shadowColor = '#00f2ff';
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 400) * chartW;
                let y = getY(d.v);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Legend
            ctx.fillStyle = "white"; ctx.font = "bold 15px sans-serif";
            ctx.fillText("LIVE TELEMETRY", padding, 35);
            ctx.fillStyle = "#ff4444"; ctx.fillText("● Target", padding + 160, 35);
            ctx.fillStyle = "#00f2ff"; ctx.fillText("● Output", padding + 240, 35);
        }}

        function loop() {{ updatePID(); draw(); requestAnimationFrame(loop); }}
        loop();
    </script>
</body>
</html>
"""

components.html(pid_js, height=580)


st.divider()
st.info("""
**Update v3.2:**
- **Smart Zoom:** Skala Y sekarang menyesuaikan diri secara real-time terhadap `Min` dan `Max` data yang ada.
- **Y-Axis Center:** Garis nol tidak lagi dipaksa di tengah jika tidak diperlukan, memberikan visibilitas maksimal pada respons transien.
""")
st.caption("© 2026 Newbie Engineer Lab")