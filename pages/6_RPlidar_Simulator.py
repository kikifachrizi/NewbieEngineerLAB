import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RPLiDAR 2D | Newbie Engineer", layout="wide")

st.title("📡 RPLiDAR 2D: Interactive Lab")
st.write("Klik Kiri: Tambah Rintangan | **Klik Kanan: Hapus Rintangan** | Panah: Gerakkan Robot")

# --- SIDEBAR ---
st.sidebar.header("🛠️ Lidar Settings")
laser_intensity = st.sidebar.slider("Laser Intensity", 0.1, 1.0, 0.4)

lidar_js = f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; background-color: #0b0e14; overflow: hidden;">
    <canvas id="lidarCanvas"></canvas>
    <script>
        const canvas = document.getElementById('lidarCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = 650;

        let robot = {{ x: canvas.width/2, y: canvas.height/2, angle: 0, radius: 15 }};
        let obstacles = [];
        let keys = {{}};

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);
        
        // Tambah Balok (Klik Kiri)
        canvas.addEventListener('mousedown', e => {{
            if (e.button === 0) {{
                obstacles.push({{ x: e.offsetX - 25, y: e.offsetY - 25, w: 50, h: 50 }});
            }}
        }});

        // Hapus Balok (Klik Kanan)
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

        function getDistance(x1, y1, angle) {{
            let maxRange = 300;
            for (let d = 0; d < maxRange; d += 2) {{
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
            if(keys['ArrowUp']) {{ nx += Math.cos(robot.angle) * 3; ny += Math.sin(robot.angle) * 3; }}
            if(keys['ArrowDown']) {{ nx -= Math.cos(robot.angle) * 3; ny -= Math.sin(robot.angle) * 3; }}
            
            if (!isColliding(nx, ny)) {{
                robot.x = nx; robot.y = ny;
            }}
            if(keys['ArrowLeft']) robot.angle -= 0.05;
            if(keys['ArrowRight']) robot.angle += 0.05;
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff4444';
            obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));

            for (let i = 0; i < 360; i += 3) {{
                let a = robot.angle + (i * Math.PI / 180);
                let d = getDistance(robot.x, robot.y, a);
                ctx.strokeStyle = `rgba(0, 242, 255, ${{d < 300 ? {laser_intensity} : 0.1}})`;
                ctx.beginPath(); ctx.moveTo(robot.x, robot.y);
                ctx.lineTo(robot.x + Math.cos(a) * d, robot.y + Math.sin(a) * d); ctx.stroke();
            }}

            ctx.fillStyle = 'white';
            ctx.beginPath(); ctx.arc(robot.x, robot.y, robot.radius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#00f2ff'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(robot.x, robot.y);
            ctx.lineTo(robot.x + Math.cos(robot.angle) * 20, robot.y + Math.sin(robot.angle) * 20); ctx.stroke();
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    </script>
</body>
</html>
"""

components.html(lidar_js, height=670)
st.divider()
st.caption("© 2026 Newbie Engineer Lab")