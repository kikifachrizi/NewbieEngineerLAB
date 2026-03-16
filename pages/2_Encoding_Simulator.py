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
    st.info("""
    **Prinsip Kerja:**
    - **X1:** Hitung saat Channel A naik (Rising Edge).
    - **X2:** Hitung saat Channel A naik & turun.
    - **X4:** Hitung setiap perubahan di A & B.
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

            // Update Angle
            angle += (rpm * 360 / 60) * dt;
            
            // Clear Canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const period = 360 / ppr;
            const viewWidth = 180; // Derajat yang tampil di layar
            const scale = canvas.width / viewWidth;

            // Draw Grid
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=50) {{
                ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
            }}

            // Calculate pulses
            let totalPulses = 0;
            if (mode === "X1") totalPulses = Math.floor((angle / 360) * ppr);
            else if (mode === "X2") totalPulses = Math.floor((angle / 360) * ppr * 2);
            else if (mode === "X4") totalPulses = Math.floor((angle / 360) * ppr * 4);

            // Draw Channel A & B
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.strokeStyle = '#00f2ff'; // Channel A (Cyan)
            
            for (let x = 0; x < canvas.width; x++) {{
                const worldAngle = angle - (canvas.width - x) / scale;
                const val = (worldAngle % period + period) % period < period / 2 ? 1 : 0;
                const y = 150 - val * 60;
                if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }}
            ctx.stroke();

            ctx.beginPath();
            ctx.strokeStyle = '#ff00ff'; // Channel B (Magenta)
            for (let x = 0; x < canvas.width; x++) {{
                const worldAngle = angle - (canvas.width - x) / scale;
                const val = ((worldAngle + period/4) % period + period) % period < period / 2 ? 1 : 0;
                const y = 300 - val * 60;
                if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }}
            ctx.stroke();

            // Draw Sampling Markers (Vertical Line)
            ctx.setLineDash([5, 5]);
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            const markerX = canvas.width - 20; // Garis di ujung kanan
            ctx.beginPath(); ctx.moveTo(markerX, 50); ctx.lineTo(markerX, 350); ctx.stroke();
            ctx.setLineDash([]);

            // Text Info
            ctx.fillStyle = "white";
            ctx.font = "bold 20px sans-serif";
            ctx.fillText("Channel A", 20, 80);
            ctx.fillText("Channel B", 20, 230);
            
            ctx.fillStyle = "#00f2ff";
            ctx.font = "30px monospace";
            ctx.fillText(`Counts: ${{totalPulses}}`, 20, 400);
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
st.caption("© 2026 Newbie Engineer Lab | High-Speed JS Encoder Engine")