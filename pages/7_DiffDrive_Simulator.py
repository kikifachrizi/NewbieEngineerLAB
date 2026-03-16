import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Kinematics Lab | Newbie Engineer", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #00f2ff33; }
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics")

with st.sidebar:
    st.header("🤖 Robot Geometry")
    # L adalah Wheel Separation (Jarak antar roda)
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01, help="Jarak dari pusat roda kiri ke pusat roda kanan")
    # R adalah Jari-jari roda
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01, help="Jari-jari roda ban")
    
    st.markdown("---")
    st.header("🕹️ 1. Velocity Input")
    v = st.slider("Linear Velocity (v) [m/s]", -1.0, 1.0, 0.4)
    w = st.slider("Angular Velocity (ω) [rad/s]", -2.0, 2.0, 0.5)
    sim_duration = st.slider("Sim Time (s)", 2, 20, 10)
    
    st.markdown("---")
    st.header("📍 2. Position Input")
    tx = st.number_input("Target X", value=1.0)
    ty = st.number_input("Target Y", value=1.0)
    tt = st.number_input("Target Theta (°)", value=45)
    
    st.markdown("---")
    run_sim = st.button("▶️ Start Simulation", use_container_width=True)
    set_pose = st.button("🎯 Set Position Directly", use_container_width=True)

# Kalkulasi Inverse Kinematics
vr = (v + (w * L / 2)) / R
vl = (v - (w * L / 2)) / R

c1, c2, c3 = st.columns(3)
c1.metric("Right Wheel (ω_r)", f"{vr:.2f} rad/s")
c2.metric("Left Wheel (ω_l)", f"{vl:.2f} rad/s")
c3.metric("L / 2", f"{L/2:.3f} m")

plot_holder = st.empty()

def draw_robot_plot(x, y, theta, path_x=None, path_y=None):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_facecolor('#0b0e14')
    ax.set_aspect('equal')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.grid(color='#30363d', linestyle='--', alpha=0.5)
    
    if path_x and path_y:
        ax.plot(path_x, path_y, color='#00f2ff', lw=1.5, linestyle='--', alpha=0.6)
    
    # Body robot lebarnya sesuai L (Wheel Separation)
    robot = plt.Circle((x, y), L/2, color='white', fill=True, zorder=5)
    ax.add_patch(robot)
    
    # Heading line
    ax.arrow(x, y, 0.4*np.cos(theta), 0.4*np.sin(theta), 
             head_width=0.15, color='#ff4444', zorder=6)
    
    ax.set_title(f"Pose: x={x:.2f}, y={y:.2f}, θ={np.degrees(theta):.1f}°", color='#00f2ff')
    return fig

if set_pose:
    fig = draw_robot_plot(tx, ty, np.radians(tt))
    plot_holder.pyplot(fig)

if run_sim:
    state = np.array([0.0, 0.0, 0.0])
    dt = 0.1
    px, py = [0.0], [0.0]
    for t in np.arange(0, sim_duration, dt):
        # Forward Kinematics
        state[0] += v * np.cos(state[2]) * dt
        state[1] += v * np.sin(state[2]) * dt
        state[2] += w * dt
        px.append(state[0]); py.append(state[1])
        fig = draw_robot_plot(state[0], state[1], state[2], px, py)
        plot_holder.pyplot(fig)
        plt.close(fig)
        time.sleep(0.01)

if not run_sim and not set_pose:
    fig = draw_robot_plot(0, 0, 0)
    plot_holder.pyplot(fig)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")