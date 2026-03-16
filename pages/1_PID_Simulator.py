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

st.title("📟 Advanced PID Simulator v3.5")
st.caption("Full Control Features: Low Pass Filter, Saturation, & Dynamic Scaling")

# --- Sidebar (Full Parameters) ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 10.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 2.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("🛡️ Signal Conditioning")
    use_filter = st.toggle("Enable Low Pass Filter", value=True)
    alpha = st.slider("Filter Alpha (Smoothing)", 0.0, 0.95, 0.3, help="Semakin tinggi, sinyal semakin halus tapi respon melambat.")
    
    use_saturation = st.toggle("Enable Output Saturation", value=True)
    max_out = st.slider("Max Output (PWM/Volt)", 50, 255, 255)

    st.divider()
    st.header("⏱️ Time Control")
    sim_speed = st.select_slider("Simulation Speed", options=["0.25x", "0.5x", "1x", "2x", "4x"], value="1x")
    speed_map = {"0.25x": 0.004, "0.5x": 0.008, "1x": 0.016, "2x": 0.032, "4x": 0.064}
    dt_val = speed_map[sim_speed]

    st.divider()
    st.header("🔄 Mode & Environment")
    mode = st.radio("System Mode", ["Manual Setpoint", "Oscillation Mode"])
    target_val = st.number_input("Target Value", value=100.0)
    noise_amp = st.slider("Sensor Noise", 0.0, 10.0, 1.5)

# --- JAVASCRIPT PID ENGINE ---
pid_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif; color: white;">
    <div id="metrics" style="position: absolute; top: 15px; right: 25px; display: flex; gap: 20px; background: rgba(20, 23, 33, 0.9); padding: 12px 25px; border-radius: 12px; border: 1px solid #00f2ff33; z-index: 100; box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);">
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase;">Peak</div><div id="m_peak" style="color: #00f2ff; font-weight: bold; font-size: 18px; font-family: monospace;">0.0</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase;">Rise Time</div><div id="m_rise" style="color: #00f2ff; font-weight: bold; font-size: 18px; font-family: monospace;">0.0s</div></div>
        <div style="text-align: center;"><div style="color: #9ea4b0; font-size: 11px; text-transform: uppercase;">Settling</div><div id="m_settle" style="color: #00f2ff; font-weight: bold; font-size: 18px; font-family: monospace;">0.0s</div></div>
    </div>

    <canvas id="pidCanvas"></canvas>

    <script>
        const canvas = document.getElementById('pidCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 550;

        // Params from Streamlit
        const Kp = {kp}, Ki = {ki}, Kd = {kd};
        const noiseAmp = {noise_amp}, mode = "{mode}";
        const useFilter = {str(use_filter).lower()}, alpha = {alpha};
        const useSat = {str(use_saturation).lower()}, maxOut = {max_out};
        const dt = {dt_val};
        let target = {target_val};

        // States
        let currV = 0, filteredV = 0, errSum = 0, lastErr = 0;
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
            
            // Anti-Windup (Hanya aktif jika Saturasi aktif)
            if (useSat) {{
                const limitI = maxOut / (Ki > 0 ? Ki : 1);
                errSum = Math.max(-limitI, Math.min(limitI, errSum));
            }}

            const deriv = (error - lastErr) / dt;
            let output = (Kp * error) + (Ki * errSum) + (Kd * deriv);
            
            // Saturation Logic
            if (useSat) {{
                output = Math.max(-maxOut, Math.min(maxOut, output));
            }}
            const pwm = output;

            // Plant Physics
            const noise = (Math.random() - 0.5) * noiseAmp;
            const accel = (pwm * 0.8) - (currV * 0.4); 
            currV += (accel * dt) + noise;
            lastErr = error;

            // Low Pass Filter Logic
            if (useFilter) {{
                filteredV = (alpha * filteredV) + ((1 - alpha) * currV);
            }} else {{
                filteredV = currV;
            }}

            // Metrics Calculation (Based on Filtered Signal)
            if(Math.abs(filteredV) > Math.abs(peakVal)) peakVal = filteredV;
            if(!riseTime && Math.abs(filteredV) >= Math.abs(target * 0.9)) riseTime = time;
            if(Math.abs(target - filteredV) > Math.abs(target * 0.05)) settlingTime = time;

            history.push({{t: time, raw: currV, f: filteredV, sp: target}});
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

            const allValues = history.map(d => d.f).concat([target]);
            const minVal = Math.min(...allValues);
            const maxVal = Math.max(...allValues);
            const range = Math.max(Math.abs(maxVal - minVal), 20);
            const yMin = minVal - (range * 0.2);
            const yMax = maxVal + (range * 0.2);
            const yRange = yMax - yMin;

            function getY(val) {{
                return (padding + chartH) - ((val - yMin) / yRange) * chartH;
            }}

            // Grid Lines
            ctx.strokeStyle = '#1e2130'; ctx.lineWidth = 1;
            ctx.font = "12px monospace"; ctx.fillStyle = "#4a4f5d";
            for(let i=0; i<=5; i++) {{
                let val = yMin + (yRange / 5) * i;
                let y = getY(val);
                ctx.beginPath(); ctx.moveTo(padding, y); ctx.lineTo(padding + chartW, y); ctx.stroke();
                ctx.fillText(val.toFixed(0), padding - 45, y + 4);
            }}

            // Setpoint (Red)
            ctx.strokeStyle = '#ff4444'; ctx.lineWidth = 2; ctx.setLineDash([8, 8]);
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 500) * chartW;
                let y = getY(d.sp);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke(); ctx.setLineDash([]);

            // Raw Signal (Faint Cyan) - Hanya tampil jika filter aktif
            if (useFilter) {{
                ctx.strokeStyle = 'rgba(0, 242, 255, 0.1)'; ctx.lineWidth = 1;
                ctx.beginPath();
                history.forEach((d, i) => {{
                    let x = padding + (i / 500) * chartW;
                    let y = getY(d.raw);
                    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                }});
                ctx.stroke();
            }}

            // Filtered Output (Solid Neon Cyan)
            ctx.strokeStyle = '#00f2ff'; ctx.lineWidth = 4;
            ctx.shadowBlur = 15; ctx.shadowColor = '#00f2ff';
            ctx.beginPath();
            history.forEach((d, i) => {{
                let x = padding + (i / 500) * chartW;
                let y = getY(d.f);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke(); ctx.shadowBlur = 0;

            // Legend & Status
            ctx.fillStyle = "white"; ctx.font = "bold 14px sans-serif";
            ctx.fillText("PID TELEMETRY | " + (useFilter ? "FILTER ON" : "FILTER OFF"), padding, 35);
            ctx.fillStyle = "#ff4444"; ctx.fillText("● Target", padding + 220, 35);
            ctx.fillStyle = "#00f2ff"; ctx.fillText("● System Output", padding + 300, 35);
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
**Kombinasi Fitur Baru:**
- **Low Pass Filter:** Menghilangkan *jitter* akibat sensor noise. Cobalah naikkan noise dan lihat perbedaan antara sinyal tipis (raw) dan sinyal tebal (filtered).
- **Anti-Windup:** Mencegah akumulasi error integral saat output sudah mencapai batas maksimal (Saturation).
""")
st.caption("© 2026 Newbie Engineer Lab")