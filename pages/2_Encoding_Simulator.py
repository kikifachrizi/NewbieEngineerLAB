import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="Encoding Simulator", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; }
    </style>
""", unsafe_allow_html=True)

st.title("📇 Quadrature Encoding (X1, X2, X4)")
st.caption("High-Speed Interactive Encoder Simulator - Powered by JavaScript Engine")

# --- Sidebar Control ---
with st.sidebar:
    st.header("Encoder Config")
    ppr = st.slider("Pulses Per Revolution (PPR)", 5, 50, 20)
    mode = st.radio("Encoding Mode", ["X1", "X2", "X4"])
    rpm = st.slider("Motor Speed (RPM)", -200, 200, 60)
    st.divider()
    st.info(f"""
    **Mode Terpilih: {mode}**
    - **X1:** Sampling dilakukan hanya pada **Rising Edge Channel A**.
    - **X2:** Sampling pada **Rising & Falling Edge Channel A**.
    - **X4:** Sampling pada **Semua Edge (Rising/Falling)** di A & B.
    """)

# --- JAVASCRIPT ENGINE (HTML5 CANVAS) ---
encoder_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; color: white; font-family: sans-serif;">
    <canvas id="encCanvas"></canvas>
    <script>
        const canvas = document.getElementById('encCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 500;

        let angle = 0;
        let lastTime = 0;
        const ppr = {ppr};
        const mode = "{mode}";
        let rpm = {rpm};

        function draw(timestamp) {{
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;
            if (!dt) {{ requestAnimationFrame(draw); return; }}

            angle += (rpm * 360 / 60) * dt;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const period = 360 / ppr;
            const viewWidth = 180; 
            const scale = canvas.width / viewWidth;

            // Draw Grid
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=50) {{
                ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
            }}

            // Logic Counter
            let totalPulses = 0;
            if (mode === "X1") totalPulses = Math.floor((angle / 360) * ppr);
            else if (mode === "X2") totalPulses = Math.floor((angle / 360) * ppr * 2);
            else if (mode === "X4") totalPulses = Math.floor((angle / 360) * ppr * 4);

            // 1. Draw Channel A & B
            ctx.lineWidth = 3;
            
            // Channel A
            ctx.beginPath();
            ctx.strokeStyle = '#00f2ff';
            for (let x = 0; x < canvas.width; x++) {{
                const worldAngle = angle - (canvas.width - x) / scale;
                const val = (worldAngle % period + period) % period < period / 2 ? 1 : 0;
                const y = 150 - val * 60;
                if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }}
            ctx.stroke();

            // Channel B
            ctx.beginPath();
            ctx.strokeStyle = '#ff00ff';
            for (let x = 0; x < canvas.width; x++) {{
                const worldAngle = angle - (canvas.width - x) / scale;
                const val = ((worldAngle + period/4) % period + period) % period < period / 2 ? 1 : 0;
                const y = 300 - val * 60;
                if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }}
            ctx.stroke();

            // 2. Draw Dynamic Sampling Markers (Vertical Dashed Lines)
            // Kita cari posisi 'edge' di jendela tampilan saat ini
            ctx.setLineDash([5, 5]);
            ctx.lineWidth = 1;
            
            const startAngle = angle - viewWidth;
            for (let a = Math.floor(startAngle/period)*period; a <= angle; a += (period/4)) {{
                let x = canvas.width - (angle - a) * scale;
                if (x < 0) continue;

                let isRisingA = Math.abs(a % period) < 0.01;
                let isFallingA = Math.abs((a - period/2) % period) < 0.01;
                let isEdgeB = Math.abs((a - period/4) % period) < 0.01 || Math.abs((a - 3*period/4) % period) < 0.01;

                let drawMarker = false;
                if (mode === "X1" && isRisingA) drawMarker = true;
                if (mode === "X2" && (isRisingA || isFallingA)) drawMarker = true;
                if (mode === "X4") drawMarker = true; // X4 sampling di setiap 1/4 perioda

                if (drawMarker) {{
                    ctx.strokeStyle = (a === Math.floor(angle/ (period/ (mode==="X4"?4:mode==="X2"?2:1))) * (period/ (mode==="X4"?4:mode==="X2"?2:1))) ? 'white' : 'rgba(255,255,255,0.2)';
                    ctx.beginPath(); ctx.moveTo(x, 50); ctx.lineTo(x, 350); ctx.stroke();
                }}
            }}
            ctx.setLineDash([]);

            // 3. Current Reader Pointer (Garis putih tebal di titik baca sekarang)
            ctx.strokeStyle = "white";
            ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(canvas.width-2, 50); ctx.lineTo(canvas.width-2, 350); ctx.stroke();

            // Text Info
            ctx.fillStyle = "white";
            ctx.font = "bold 16px sans-serif";
            ctx.fillText("Channel A", 20, 80);
            ctx.fillText("Channel B", 20, 230);
            
            ctx.fillStyle = "#00f2ff";
            ctx.font = "bold 28px monospace";
            ctx.fillText(`Counts: ${{totalPulses}}`, 20, 400);
            ctx.font = "20px monospace";
            ctx.fillText(`Angle: ${{Math.floor(angle % 360)}}°`, 20, 440);

            requestAnimationFrame(draw);
        }}
        requestAnimationFrame(draw);
    </script>
</body>
</html>
"""

components.html(encoder_js, height=520)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")