import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Konfigurasi Page ---
st.set_page_config(page_title="Kinematics Lab | Newbie Engineer", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #00f2ff33; }
        .block-container { padding-top: 1rem; }
        /* Style untuk button agar lebih stand out */
        .stButton button { width: 100%; border-radius: 10px; height: 3em; background-color: #00f2ff11; border: 1px solid #00f2ff33; color: #00f2ff; }
        .stButton button:hover { background-color: #00f2ff33; border: 1px solid #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01)
    
    st.divider()
    st.header("🕹️ 1. Velocity Input")
    v_lin = st.slider("Linear Velocity (v) [m/s]", -1.0, 1.0, 0.4)
    w_ang = st.slider("Angular Velocity (ω) [rad/s]", -2.0, 2.0, 0.5)
    sim_duration = st.slider("Sim Time (s)", 2, 20, 10)
    
    st.divider()
    st.header("📍 2. Target Pose")
    tx = st.number_input("Target X", value=1.5)
    ty = st.number_input("Target Y", value=1.5)
    tt = st.slider("Target Heading (°)", -180, 180, 45)
    
    st.divider()
    # Tombol aksi
    run_sim = st.button("🚀 RUN SIMULATION")
    set_pose = st.button("🎯 SNAP TO TARGET")

# --- Inverse Kinematics Display ---
vr = (v_lin + (w_ang * L / 2)) / R
vl = (v_lin - (w_ang * L / 2)) / R

c1, c2, c3 = st.columns(3)
with c1: st.metric("Right Wheel", f"{vr:.2f} rad/s")
with c2: st.metric("Left Wheel", f"{vl:.2f} rad/s")
with c3: st.metric("System Status", "Live" if not run_sim else "Animating")

# --- SIMULATION ENGINE ---
def generate_viz():
    # Pre-calculate path
    dt = 0.1
    t_steps = np.arange(0, sim_duration, dt)
    x_path, y_path, th_path = [0.0], [0.0], [0.0]
    curr_x, curr_y, curr_th = 0.0, 0.0, 0.0

    for _ in t_steps:
        curr_x += v_lin * np.cos(curr_th) * dt
        curr_y += v_lin * np.sin(curr_th) * dt
        curr_th += w_ang * dt
        x_path.append(curr_x)
        y_path.append(curr_y)
        th_path.append(curr_th)

    # Base Figure
    fig = go.Figure()

    # 1. Plot Target (Ghost Robot) - Always visible if not running
    ang = np.linspace(0, 2*np.pi, 30)
    fig.add_trace(go.Scatter(
        x=tx + (L/2) * np.cos(ang), y=ty + (L/2) * np.sin(ang),
        fill="toself", fillcolor="rgba(255, 68, 68, 0.1)", 
        line=dict(color="rgba(255, 68, 68, 0.3)", dash="dot"),
        name="Target Pose"
    ))

    # 2. Path Trace (Blue)
    fig.add_trace(go.Scatter(
        x=x_path, y=y_path, mode="lines", 
        line=dict(color="#00f2ff", width=2, dash="dot"), 
        name="Predicted Path"
    ))

    # 3. Robot Body (Dynamic Scatter)
    fig.add_trace(go.Scatter(
        x=[], y=[], fill="toself", 
        fillcolor="rgba(0, 242, 255, 0.8)", 
        line=dict(color="white", width=1), 
        name="Robot"
    ))

    # Layout Setup
    fig.update_layout(
        template="plotly_dark", height=700,
        xaxis=dict(range=[-4, 4], gridcolor="#1e2130", zeroline=False),
        yaxis=dict(range=[-4, 4], gridcolor="#1e2130", zeroline=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        # Auto-animate configuration
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]
            }]
        }]
    )

    # If SNAP TO TARGET
    if set_pose:
        fig.data[2].x = tx + (L/2) * np.cos(ang)
        fig.data[2].y = ty + (L/2) * np.sin(ang)
        st.plotly_chart(fig, use_container_width=True)
    
    # If RUN SIMULATION (With Frames)
    elif run_sim:
        frames = [
            go.Frame(
                data=[
                    go.Scatter(x=x_path[:i], y=y_path[:i]), # Path
                    go.Scatter( # Robot
                        x=x_path[i] + (L/2) * np.cos(ang),
                        y=y_path[i] + (L/2) * np.sin(ang)
                    )
                ],
                name=f"frame{i}"
            ) for i in range(len(x_path))
        ]
        fig.frames = frames
        
        # Trik: Langsung jalankan animasi saat load menggunakan JS trigger
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 Tip: Jika animasi tidak jalan otomatis, klik tombol 'Play' di pojok kiri bawah grafik.")

    # Default View (Idle at Home)
    else:
        fig.data[2].x = 0 + (L/2) * np.cos(ang)
        fig.data[2].y = 0 + (L/2) * np.sin(ang)
        st.plotly_chart(fig, use_container_width=True)

generate_viz()



st.divider()
st.caption("© 2026 Newbie Engineer Lab | Kinematics Engine v3.1")