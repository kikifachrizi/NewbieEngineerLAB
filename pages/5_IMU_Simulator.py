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
st.sidebar.header("🕹️ IMU Controls")
roll = st.sidebar.slider("Roll (Φ) - Axis X", -180.0, 180.0, 0.0, step=0.1)
pitch = st.sidebar.slider("Pitch (θ) - Axis Y", -180.0, 180.0, 0.0, step=0.1)
yaw = st.sidebar.slider("Yaw (ψ) - Axis Z", -180.0, 180.0, 0.0, step=0.1)

# --- 3D VISUALIZATION ENGINE (Fragmented for Performance) ---
@st.fragment
def run_imu_telemetry(r, p, y):
    # Baris 1: Data Rotasi (Gyroscope)
    st.markdown("### 🔄 Orientation Data")
    c1, c2, c3 = st.columns(3)
    c1.metric("Roll (X)", f"{r:.2f}°")
    c2.metric("Pitch (Y)", f"{p:.2f}°")
    c3.metric("Yaw (Z)", f"{y:.2f}°")

    # Baris 2: Data Linear (Simulasi Accelerometer)
    st.markdown("### 📏 Linear Components")
    c4, c5, c6 = st.columns(3)
    c4.metric("Linear X", f"{np.sin(np.radians(r)):.3f}")
    c5.metric("Linear Y", f"{np.cos(np.radians(p)):.3f}")
    c6.metric("Linear Z", f"{np.sin(np.radians(p)):.3f}")

    # Fungsi Rotasi Matriks (Optimized)
    def get_rotation_matrix(r, p, y):
        r, p, y = np.radians([r, p, y])
        Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
        Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
        Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx

    rot_mat = get_rotation_matrix(r, p, y)

    # Robot Body Points (Box)
    points = np.array([[-1,-1,-0.2], [1,-1,-0.2], [1,1,-0.2], [-1,1,-0.2],
                       [-1,-1,0.2], [1,-1,0.2], [1,1,0.2], [-1,1,0.2]])
    
    # Vectorized rotation: Rotate all points at once
    rotated_points = points @ rot_mat.T

    fig = go.Figure()

    # Mesh 3D for Robot Body
    fig.add_trace(go.Mesh3d(
        x=rotated_points[:,0], y=rotated_points[:,1], z=rotated_points[:,2],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='#00f2ff', opacity=0.5, name="Robot Body"
    ))

    # --- 6 AXIS LINES ---
    axes_data = {
        'X+': [2, 0, 0, 'red'],
        'Y+': [0, 2, 0, 'green'],
        'Z+': [0, 0, 2, '#58a6ff']
    }

    for label, data in axes_data.items():
        p2 = np.array(data[:3]) @ rot_mat.T
        fig.add_trace(go.Scatter3d(
            x=[0, p2[0]], y=[0, p2[1]], z=[0, p2[2]],
            mode='lines+text', 
            line=dict(color=data[3], width=6),
            text=[None, label], 
            textfont=dict(color='white', size=11),
            name=label
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", showticklabels=False, title=""),
            yaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", showticklabels=False, title=""),
            zaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d", showticklabels=False, title=""),
            aspectmode='cube'
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        template="plotly_dark",
        height=550,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Jalankan Render dalam Fragment
run_imu_telemetry(roll, pitch, yaw)

# Penjelasan Konsep


with st.expander("ℹ️ IMU 6-Axis Data Details"):
    st.write(f"""
    - **Orientation (Gyroscope):** Mengukur kecepatan sudut dan orientasi absolut (Roll, Pitch, Yaw).
    - **Linear (Accelerometer):** Mengukur percepatan linear. Di robotika, data ini digabung (Sensor Fusion) untuk mendapatkan estimasi posisi yang presisi.
    - **Coordinate System:** Mengikuti kaidah tangan kanan (Right-hand rule) standar robotika ROS.
    """)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")