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
        /* Style Metric agar lebih techy */
        [data-testid="stMetricValue"] { font-family: 'Courier New', monospace; color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Differential Drive Kinematics")
st.caption("Live Interactive Simulation - Predict & Execute")

# --- SIDEBAR (INPUT) ---
with st.sidebar:
    st.header("🤖 Robot Geometry")
    L = st.number_input("Wheel Separation (L) [m]", value=0.30, step=0.01)
    R = st.number_input("Wheel Radius (R) [m]", value=0.05, step=0.01)
    
    st.divider()
    st.header("🕹️ Real-Time Control")
    v_lin = st.slider("Linear Velocity (v) [m/s]", -1.0, 1.0, 0.4)
    w_ang = st.slider("Angular Velocity (ω) [rad/s]", -2.0, 2.0, 0.5)
    sim_time = st.slider("Prediction Time (s)", 1, 10, 5)
    
    st.divider()
    # Tombol Reset
    if st.button("🔄 Reset to Origin", use_container_width=True):
        st.rerun()

# --- Kalkulasi Inverse Kinematics (Langsung Update) ---
vr = (v_lin + (w_ang * L / 2)) / R
vl = (v_lin - (w_ang * L / 2)) / R

c1, c2, c3 = st.columns(3)
c1.metric("Right Wheel (ω_r)", f"{vr:.2f} rad/s")
c2.metric("Left Wheel (ω_l)", f"{vl:.2f} rad/s")
c3.metric("ICR Radius", f"{(v_lin/w_ang):.2f} m" if w_ang != 0 else "∞")

# --- SIMULATION ENGINE (LIVE PREVIEW) ---
@st.fragment
def show_interactive_sim():
    # 1. Hitung Path secara Real-time
    dt = 0.05
    t_steps = np.arange(0, sim_time, dt)
    x_path, y_path, th_path = [0.0], [0.0], [0.0]
    curr_x, curr_y, curr_th = 0.0, 0.0, 0.0

    for _ in t_steps:
        curr_x += v_lin * np.cos(curr_th) * dt
        curr_y += v_lin * np.sin(curr_th) * dt
        curr_th += w_ang * dt
        x_path.append(curr_x)
        y_path.append(curr_y)
        th_path.append(curr_th)

    # 2. Plotting (Plotly)
    fig = go.Figure()

    # Prediksi Jalur (Neon Cyan)
    fig.add_trace(go.Scatter(
        x=x_path, y=y_path, mode="lines",
        line=dict(color="#00f2ff", width=3, dash="solid"),
        name="Predicted Path",
        hovertemplate="x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>"
    ))

    # Robot di Titik Awal (0,0)
    ang = np.linspace(0, 2*np.pi, 30)
    fig.add_trace(go.Scatter(
        x=0 + (L/2) * np.cos(ang), y=0 + (L/2) * np.sin(ang),
        fill="toself", fillcolor="rgba(255, 255, 255, 0.1)",
        line=dict(color="gray", width=1),
        name="Start Pos"
    ))

    # Robot di Titik Akhir Prediksi (Current Pose)
    end_x, end_y, end_th = x_path[-1], y_path[-1], th_path[-1]
    
    # Body
    fig.add_trace(go.Scatter(
        x=end_x + (L/2) * np.cos(ang), y=end_y + (L/2) * np.sin(ang),
        fill="toself", fillcolor="rgba(0, 242, 255, 0.6)",
        line=dict(color="white", width=2),
        name="Robot Pose"
    ))

    # Heading Arrow (Penanda Arah Robot)
    arrow_len = 0.4
    fig.add_trace(go.Scatter(
        x=[end_x, end_x + arrow_len * np.cos(end_th)],
        y=[end_y, end_y + arrow_len * np.sin(end_th)],
        mode="lines+markers",
        line=dict(color="#ff4444", width=4),
        marker=dict(size=[0, 10], symbol="arrow-bar-up", angleref="previous"),
        name="Heading"
    ))

    fig.update_layout(
        template="plotly_dark", height=700,
        xaxis=dict(title="X Position (m)", range=[-3, 3], gridcolor="#1e2130", zeroline=True, zerolinecolor="#4a4f5d"),
        yaxis=dict(title="Y Position (m)", range=[-3, 3], gridcolor="#1e2130", zeroline=True, zerolinecolor="#4a4f5d", scaleanchor="x", scaleratio=1),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        plot_bgcolor="#0b0e14", paper_bgcolor="#0b0e14"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

show_interactive_sim()



st.divider()
st.info("""
**User Guide:**
- Geser slider **v** dan **ω** di sidebar. Grafik akan langsung menampilkan prediksi pergerakan robot secara real-time.
- **Garis Cyan:** Jalur yang akan ditempuh robot selama durasi waktu prediksi.
- **Panah Merah:** Orientasi (*heading*) robot di akhir jalur.
- Simulator ini menggunakan model **Forward Kinematics** untuk menghitung odometri.
""")
st.caption("© 2026 Newbie Engineer Lab")