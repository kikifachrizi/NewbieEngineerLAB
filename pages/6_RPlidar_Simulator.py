import streamlit as st
import streamlit.components.v1 as components

# --- Konfigurasi Page ---
st.set_page_config(page_title="RPLiDAR 2D | Newbie Engineer", layout="wide")

# Custom CSS buat nyesuain Streamlit Theme
st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; }
        iframe { border-radius: 15px; border: 1px solid #1e2130; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 RPLiDAR 2D: Interactive Lab")
st.write("🎮 **Kontrol:** Klik Kiri (Tambah) | Klik Kanan (Hapus) | Tombol Panah (Gerak Robot)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Lidar Settings")
    laser_intensity = st.slider("Laser Intensity", 0.1, 1.0, 0.4)
    st.info("Simulasi ini menggunakan algoritma **Raycasting** sederhana untuk mendeteksi tabrakan laser dengan objek.")

# --- JAVASCRIPT ENGINE (HTML5 CANVAS) ---
lidar_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden; font-family: sans-serif;">
    <canvas id="lidarCanvas"></canvas>
    <script>
        const canvas = document.getElementById('lidarCanvas');
        const ctx = canvas.getContext('2d');
        
        // Responsivitas Canvas
        canvas.width = window.innerWidth;
        canvas.height = 650;

        let robot = {{ x: canvas.width/2, y: canvas.height/2, angle: 0, radius: 15 }};
        let obstacles = [
            {{ x: 100, y: 100, w: 80, h: 80 }}, // Rintangan bawaan
            {{ x: 500, y: 300, w: 100, h: 20 }}
        ];
        let keys = {{}};

        // Event Listeners
        window.addEventListener('keydown', e => {{ 
            keys[e.code] = true; 
            // Cegah scroll halaman saat main
            if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.code)) e.preventDefault();
        }});
        window.addEventListener('keyup', e => keys[e.code] = false);
        
        canvas.addEventListener('mousedown', e => {{
            if (e.button === 0) {{
                obstacles.push({{ x: e.offsetX - 25, y: e.offsetY - 25, w: 50, h: 50 }});
            }}
        }});

        canvas.addEventListener('contextmenu', e => {{
            e.preventDefault();
            const mx = e.offsetX;
            const my = e.offsetY;
            obstacles = obstacles.filter(o => !(mx > o.x && mx < o.x + o.w && my > o.y && my < o.y + o.h));
        }});

        function isColliding(nx, ny) {{
            for (let o of obstacles) {{
                if (nx + robot.radius > o.x && nx - robot.radius < o.x + o.w && 
                    ny + robot.radius > o.y && ny - robot.radius < o.y + o.h) return true;
            }}
            return false;
        }}

        // Raycasting Logic
        function getDistance(x1, y1, angle) {{
            let maxRange = 400;
            for (let d = 0; d < maxRange; d += 4) {{ // Step 4px biar lebih enteng
                let px = x1 + Math.cos(angle) * d;
                let py = y1 + Math.sin(angle) * d;
                for (let o of obstacles) {{
                    if (px > o.x && px < o.x + o.w && py > o.y && py < o.y + o.h) return d;
                }}
            }}
            return maxRange;
        }}

        function update() {{
            let nx = robot.x, ny = robot.y;
            let speed = 4;
            if(keys['ArrowUp']) {{ nx += Math.cos(robot.angle) * speed; ny += Math.sin(robot.angle) * speed; }}
            if(keys['ArrowDown']) {{ nx -= Math.cos(robot.angle) * speed; ny -= Math.sin(robot.angle) * speed; }}
            
            if (!isColliding(nx, ny)) {{
                robot.x = nx; robot.y = ny;
            }}
            if(keys['ArrowLeft']) robot.angle -= 0.06;
            if(keys['ArrowRight']) robot.angle += 0.06;
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Grid Background
            ctx.strokeStyle = '#1e2130';
            ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=50) {{ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }}
            for(let i=0; i<canvas.height; i+=50) {{ ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke(); }}

            // Draw Obstacles
            ctx.fillStyle = '#ff4b4b';
            obstacles.forEach(o => {{
                ctx.fillRect(o.x, o.y, o.w, o.h);
                ctx.strokeStyle = '#ffffff';
                ctx.strokeRect(o.x, o.y, o.w, o.h);
            }});

            // Draw Lidar Rays
            for (let i = 0; i < 360; i += 2) {{ // Resolusi 2 derajat
                let a = robot.angle + (i * Math.PI / 180);
                let d = getDistance(robot.x, robot.y, a);
                ctx.strokeStyle = d < 400 ? `rgba(0, 242, 255, ${laser_intensity * 1.5})` : 'rgba(0, 242, 255, 0.15)';
                ctx.lineWidth = 2;
                ctx.beginPath(); 
                ctx.moveTo(robot.x, robot.y);
                ctx.lineTo(robot.x + Math.cos(a) * d, robot.y + Math.sin(a) * d); 
                ctx.stroke();
            }}

            // Draw Robot
            ctx.fillStyle = 'white';
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00f2ff';
            ctx.beginPath(); ctx.arc(robot.x, robot.y, robot.radius, 0, Math.PI*2); ctx.fill();
            
            // Direction Marker
            ctx.shadowBlur = 0;
            ctx.strokeStyle = '#00f2ff'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(robot.x, robot.y);
            ctx.lineTo(robot.x + Math.cos(robot.angle) * 22, robot.y + Math.sin(robot.angle) * 22); ctx.stroke();
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    </script>
</body>
</html>
"""

components.html(lidar_js, height=670)



st.divider()
st.caption("© 2026 Newbie Engineer Lab | Built with HTML5 Canvas & Raycasting Engine")