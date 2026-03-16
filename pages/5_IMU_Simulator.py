import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Konfigurasi Page ---
st.set_page_config(page_title="IMU Simulator | Newbie Engineer", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; }
        .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
        [data-testid="stMetricValue"] { font-family: 'Courier New', monospace; color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 IMU 6-Axis Telemetry Simulator")

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.header("🕹️ IMU Controls")
    roll = st.slider("Roll (Φ) - Axis X", -180.0, 180.0, 0.0, step=0.1)
    pitch = st.slider("Pitch (θ) - Axis Y", -180.0, 180.0, 0.0, step=0.1)
    yaw = st.slider("Yaw (ψ) - Axis Z", -180.0, 180.0, 0.0, step=0.1)
    st.divider()
    st.info("Visualisasi ini menggunakan sistem koordinat tangan kanan (Right-Hand Rule).")

# --- 3D VISUALIZATION ENGINE ---
@st.fragment
def run_imu_telemetry(r, p, y):
    # Baris 1: Data Rotasi
    st.markdown("### 🔄 Orientation Data")
    c1, c2, c3 = st.columns(3)
    c1.metric("Roll (X)", f"{r:.2f}°")
    c2.metric("Pitch (Y)", f"{p:.2f}°")
    c3.metric("Yaw (Z)", f"{y:.2f}°")

    # Baris 2: Data Linear (Simulasi Gravitasi/Accel)
    st.markdown("### 📏 Linear Components (G)")
    c4, c5, c6 = st.columns(3)
    # Simulasi pembacaan gravitasi saat miring
    ax = np.sin(np.radians(p))
    ay = -np.sin(np.radians(r)) * np.cos(np.radians(p))
    az = np.cos(np.radians(r)) * np.cos(np.radians(p))
    c4.metric("Accel X", f"{ax:.3f}")
    c5.metric("Accel Y", f"{ay:.3f}")
    c6.metric("Accel Z", f"{az:.3f}")

    # Fungsi Rotasi Matriks (Standard Robotics Order: ZYX)
    def get_rotation_matrix(roll_deg, pitch_deg, yaw_deg):
        r_rad, p_rad, y_rad = np.radians([roll_deg, pitch_deg, yaw_deg])
        
        # Matrix X (Roll)
        Rx = np.array([[1, 0, 0], [0, np.cos(r_rad), -np.sin(r_rad)], [0, np.sin(r_rad), np.cos(r_rad)]])
        # Matrix Y (Pitch)
        Ry = np.array([[np.cos(p_rad), 0, np.sin(p_rad)], [0, 1, 0], [-np.sin(p_rad), 0, np.cos(p_rad)]])
        # Matrix Z (Yaw)
        Rz = np.array([[np.cos(y_rad), -np.sin(y_rad), 0], [np.sin(y_rad), np.cos(y_rad), 0], [0, 0, 1]])
        
        return Rz @ Ry @ Rx

    rot_mat = get_rotation_matrix(r, p, y)

    # Robot Body Points (Box 3D)
    points = np.array([[-1,-1,-0.2], [1,-1,-0.2], [1,1,-0.2], [-1,1,-0.2],
                       [-1,-1,0.2], [1,-1,0.2], [1,1,0.2], [-1,1,0.2]])
    
    rotated_points = points @ rot_mat.T

    fig = go.Figure()

    # Mesh 3D for Robot Body
    fig.add_trace(go.Mesh3d(
        x=rotated_points[:,0], y=rotated_points[:,1], z=rotated_points[:,2],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='#00f2ff', opacity=0.4, name="Robot Body"
    ))

    # --- 6 AXIS LINES (Positive & Negative) ---
    # Kita gambar sumbu yang ikut berputar
    axes_conf = [
        ([0, 2], [0, 0], [0, 0], 'red', 'X+'),
        ([0, 0], [0, 2], [0, 0], 'green', 'Y+'),
        ([0, 0], [0, 0], [0, 2], '#58a6ff', 'Z+'),
        ([0, -1.5], [0, 0], [0, 0], 'red', ''), # X- dash
        ([0, 0], [0, -1.5], [0, 0], 'green', ''), # Y- dash
    ]

    for start_end in axes_conf:
        p_start = np.array([0,0,0])
        p_end = np.array([start_end[0][1], start_end[1][1], start_end[2][1]]) @ rot_mat.T
        
        fig.add_trace(go.Scatter3d(
            x=[0, p_end[0]], y=[0, p_end[1]], z=[0, p_end[2]],
            mode='lines+text',
            line=dict(color=start_end[3], width=5, dash='solid' if start_end[4] else 'dash'),
            text=[None, start_end[4]],
            textfont=dict(color='white', size=12),
            showlegend=False
        ))

    # Fix Layout & Axis Visibility
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", zeroline=False),
            yaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", zeroline=False),
            zaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", zeroline=False),
            aspectmode='cube', # Mengunci rasio 1:1:1 biar nggak gepeng
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)) # Angle kamera default
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        template="plotly_dark",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_imu_telemetry(roll, pitch, yaw)



with st.expander("ℹ️ IMU 6-Axis Data Details"):
    st.write("""
    - **Roll, Pitch, Yaw:** Sudut rotasi pada sumbu X, Y, dan Z.
    - **Accelerometer:** Dalam simulator ini, nilai linear dihitung berdasarkan proyeksi vektor gravitasi terhadap kemiringan body robot.
    - **Coordinate:** Merah (X), Hijau (Y), Biru (Z).
    """)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")