import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

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

# --- Visualization Function (Plotly Based) ---
def create_robot_plot(x, y, theta, path_x=None, path_y=None):
    fig = go.Figure()

    # Draw Path
    if path_x and len(path_x) > 1:
        fig.add_trace(go.Scatter(x=path_x, y=path_y, mode='lines', 
                                line=dict(color='#00f2ff', width=2, dash='dot'), 
                                name="Path Trace"))

    # Draw Robot Body (Circle)
    # Kita buat koordinat lingkaran manual untuk Plotly Scatter
    angles = np.linspace(0, 2*np.pi, 50)
    circle_x = x + (L/2) * np.cos(angles)
    circle_y = y + (L/2) * np.sin(angles)
    
    fig.add_trace(go.Scatter(x=circle_x, y=circle_y, fill="toself", 
                            fillcolor="white", line=dict(color="#9ea4b0"), 
                            name="Robot Body", hoverinfo='skip'))

    # Draw Heading Arrow
    arrow_len = 0.4
    fig.add_annotation(
        x=x + arrow_len * np.cos(theta), y=y + arrow_len * np.sin(theta),
        ax=x, ay=y, xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=3, arrowcolor="#ff4444"
    )

    fig.update_layout(
        template="plotly_dark", height=600, width=700,
        xaxis=dict(range=[-4, 4], showgrid=True, gridcolor="#30363d", zeroline=False),
        yaxis=dict(range=[-4, 4], showgrid=True, gridcolor="#30363d", zeroline=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(text=f"Pose: x={x:.2f}, y={y:.2f}, θ={np.degrees(theta):.1f}°", font=dict(color="#00f2ff")),
        showlegend=False,
        plot_bgcolor="#0b0e14", paper_bgcolor="#0b0e14"
    )
    return fig

# --- Control Logic ---
plot_holder = st.empty()

if set_pose:
    fig = create_robot_plot(tx, ty, np.radians(tt))
    plot_holder.plotly_chart(fig, use_container_width=True)

elif run_sim:
    curr_x, curr_y, curr_theta = 0.0, 0.0, 0.0
    dt = 0.2 # Ditambah sedikit biar ga terlalu banyak render
    px, py = [0.0], [0.0]
    
    for t in np.arange(0, sim_duration, dt):
        # Forward Kinematics (Odometry)
        curr_x += v_lin * np.cos(curr_theta) * dt
        curr_y += v_lin * np.sin(curr_theta) * dt
        curr_theta += w_ang * dt
        
        px.append(curr_x)
        py.append(curr_y)
        
        fig = create_robot_plot(curr_x, curr_y, curr_theta, px, py)
        plot_holder.plotly_chart(fig, use_container_width=True)
        # Menghapus time.sleep karena rendering cloud sudah memberikan delay alami

else:
    # Tampilan awal (Idle)
    fig = create_robot_plot(0, 0, 0)
    plot_holder.plotly_chart(fig, use_container_width=True)



st.divider()
st.caption("© 2026 Newbie Engineer Lab | Specialized for AMR TIFA R&D")