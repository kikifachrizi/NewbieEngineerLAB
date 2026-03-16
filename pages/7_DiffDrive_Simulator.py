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
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics")

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
    st.header("📍 2. Position Input")
    tx = st.number_input("Target X", value=1.0)
    ty = st.number_input("Target Y", value=1.0)
    tt = st.number_input("Target Theta (°)", value=45)
    
    st.divider()
    run_sim = st.button("▶️ Start Simulation", use_container_width=True)
    set_pose = st.button("🎯 Set Position Directly", use_container_width=True)

# --- Inverse Kinematics Calculation ---
vr = (v_lin + (w_ang * L / 2)) / R
vl = (v_lin - (w_ang * L / 2)) / R

c1, c2, c3 = st.columns(3)
c1.metric("Right Wheel (ω_r)", f"{vr:.2f} rad/s")
c2.metric("Left Wheel (ω_l)", f"{vl:.2f} rad/s")
c3.metric("L / 2", f"{L/2:.3f} m")

# --- Animation Engine ---
def run_kinematics_animation():
    # Pre-calculate all frames
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
    fig = go.Figure(
        data=[
            # Path Trace
            go.Scatter(x=x_path, y=y_path, mode="lines", line=dict(color="#00f2ff", width=2, dash="dot"), name="Path"),
            # Robot Body (Initial)
            go.Scatter(x=[], y=[], fill="toself", fillcolor="rgba(255,255,255,0.8)", line=dict(color="cyan"), name="Robot")
        ],
        layout=go.Layout(
            template="plotly_dark",
            xaxis=dict(range=[-4, 4], autorange=False, gridcolor="#30363d"),
            yaxis=dict(range=[-4, 4], autorange=False, gridcolor="#30363d", scaleanchor="x", scaleratio=1),
            updatemenus=[dict(type="buttons", buttons=[dict(label="Play Animation", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}])])],
        ),
        frames=[
            go.Frame(
                data=[
                    go.Scatter(x=x_path[:i], y=y_path[:i]), # Update Path
                    go.Scatter( # Update Robot Circle
                        x=x_path[i] + (L/2) * np.cos(np.linspace(0, 2*np.pi, 30)),
                        y=y_path[i] + (L/2) * np.sin(np.linspace(0, 2*np.pi, 30))
                    )
                ]
            ) for i in range(len(x_path))
        ]
    )
    
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600)
    st.plotly_chart(fig, use_container_width=True)

# --- Logic Control ---
if run_sim:
    run_kinematics_animation()
elif set_pose:
    # Static Pose logic
    ang = np.linspace(0, 2*np.pi, 30)
    fig = go.Figure(data=[
        go.Scatter(x=tx + (L/2) * np.cos(ang), y=ty + (L/2) * np.sin(ang), fill="toself", fillcolor="white"),
        # Heading Arrow
        go.Scatter(x=[tx, tx + 0.4*np.cos(np.radians(tt))], y=[ty, ty + 0.4*np.sin(np.radians(tt))], mode="lines+markers", line=dict(color="red", width=4))
    ])
    fig.update_layout(template="plotly_dark", xaxis=dict(range=[-4,4]), yaxis=dict(range=[-4,4], scaleanchor="x"), height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Atur parameter di sidebar lalu klik Start Simulation untuk melihat pergerakan robot.")



st.divider()
st.caption("© 2026 Newbie Engineer Lab")