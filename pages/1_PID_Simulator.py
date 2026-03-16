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

st.title("📟 Advanced PID Simulator v3.3")
st.caption("Precision Control System - Dynamic Time-Scale Engine")

# --- Sidebar ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 10.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 2.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("⏱️ Time Control")
    # Fitur Baru: Mengatur kecepatan simulasi
    sim_speed = st.select_slider(
        "Simulation Speed",
        options=["0.25x", "0.5x", "1x", "2x", "4x"],
        value="1x",
        help="0.25x untuk analisa slow-motion, 4x untuk testing stabilitas cepat."
    )
    # Konversi string ke multiplier numerik
    speed_map = {"0.25x": 0.004, "0.5x": 0.008, "1x": 0.016, "2x": 0.032, "4x": 0.064}
    dt_val = speed_map[sim_speed]

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
        const dt = {dt_val}; // Kecepatan simulasi dari Streamlit
        let target = {target_val};

        let currV = 0, errSum = 0, lastErr = 0;
        let history = [], time = 0, oscTimer = 0;
        let peakVal = 0, riseTime = 0, settlingTime = 0;

        function updatePID() {{
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
            if (history.length > 500) history.shift();
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

            const allValues = history.map(d => d.v).concat([target]);
            const minVal = Math.min(...allValues);
            const maxVal = Math.max(...allValues);
            const range = Math.max(Math.abs(maxVal - minVal), 20);
            const yMin = minVal - (range * 0.2);
            const yMax = maxVal + (range * 0.2);
            const yRange = yMax - yMin;

            function getY(val) {{
                return (padding + chartH) - ((val - yMin) / yRange) * chartH;
            }}

            // Grid
            ctx.strokeStyle = '#1e2130'; ctx.lineWidth = 1;
            ctx.font = "12px monospace"; ctx.fillStyle = "#4a4f5d";
            for(let i=0; i<=5; i++) {{
                let val = yMin + (yRange / 5) * i;
                let y = getY(val);
                ctx.beginPath(); ctx.moveTo(padding, y); ctx.lineTo(padding + chartW, y); ctx.stroke();
                ctx.fillText(val.toFixed(0), padding - 45, y + 4);
            }}

            // Target Line
            ctx.strokeStyle = '#ff4444'; ctx.lineWidth = 2; ctx.setLineDash([10, 10]);
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 500) * chartW;
                let y = getY(d.sp);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke(); ctx.setLineDash([]);

            // Output Line
            ctx.strokeStyle = '#00f2ff'; ctx.lineWidth = 4;
            ctx.shadowBlur = 15; ctx.shadowColor = '#00f2ff';
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 500) * chartW;
                let y = getY(d.v);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke(); ctx.shadowBlur = 0;

            // Labels
            ctx.fillStyle = "white"; ctx.font = "bold 15px sans-serif";
            ctx.fillText("LIVE TELEMETRY (" + "{sim_speed}" + ")", padding, 35);
            ctx.fillStyle = "#ff4444"; ctx.fillText("● Target", padding + 220, 35);
            ctx.fillStyle = "#00f2ff"; ctx.fillText("● Output", padding + 300, 35);
        }}

        function loop() {{ updatePID(); draw(); requestAnimationFrame(loop); }}
        loop();
    </script>
</body>
</html>
"""

components.html(pid_js, height=580)

st.divider()
st.info(f"""
**Info Simulasi:**
- **Kecepatan:** Saat ini berjalan pada **{sim_speed}**. 
- **Analisis:** Gunakan **0.25x** untuk melihat osilasi mikro atau **4x** untuk melihat respon sistem terhadap gangguan (*noise*) dalam jangka panjang secara cepat.
""")
st.caption("© 2026 Newbie Engineer Lab")