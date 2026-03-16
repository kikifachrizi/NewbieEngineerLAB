import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="IMU Simulator | Newbie Engineer", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #ecf0f1; }
        [data-testid="stSidebar"] { background-color: #161b22; }
        /* Memperkecil padding container utama */
        .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
        /* Styling khusus buat Metric agar lebih techy */
        [data-testid="stMetricValue"] { font-family: 'Courier New', monospace; color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 IMU 6-Axis Telemetry Simulator")

# --- SIDEBAR CONTROL ---
st.sidebar.header("🕹️ IMU Controls")
roll = st.sidebar.slider("Roll (Φ) - Axis X", -180.0, 180.0, 0.0, step=0.1)
pitch = st.sidebar.slider("Pitch (θ) - Axis Y", -180.0, 180.0, 0.0, step=0.1)
yaw = st.sidebar.slider("Yaw (ψ) - Axis Z", -180.0, 180.0, 0.0, step=0.1)

# --- 6-AXIS TELEMETRY DISPLAY ---
# Baris 1: Data Rotasi (Gyroscope)
st.markdown("### 🔄 Orientation Data")
c1, c2, c3 = st.columns(3)
c1.metric("Roll (X)", f"{roll:.2f}°")
c2.metric("Pitch (Y)", f"{pitch:.2f}°")
c3.metric("Yaw (Z)", f"{yaw:.2f}°")

# Baris 2: Data Linear (Accelerometer/Position)
# Kita hitung nilai komponen vektor berdasarkan rotasi untuk simulasi sensor
st.markdown("### 📏 Linear Components")
c4, c5, c6 = st.columns(3)
c4.metric("Linear X", f"{np.sin(np.radians(roll)):.3f}")
c5.metric("Linear Y", f"{np.cos(np.radians(pitch)):.3f}")
c6.metric("Linear Z", f"{np.sin(np.radians(pitch)):.3f}")

# Fungsi Rotasi Matriks
def rotate_point(p, r, p_angle, y):
    r, p_a, y = np.radians([r, p_angle, y])
    Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
    Ry = np.array([[np.cos(p_a), 0, np.sin(p_a)], [0, 1, 0], [-np.sin(p_a), 0, np.cos(p_a)]])
    Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx @ p

# --- 3D VISUALIZATION ENGINE ---
def render_imu_plot(r, p, y):
    fig = go.Figure()

    # Robot Body Points (Box)
    points = np.array([[-1,-1,-0.2], [1,-1,-0.2], [1,1,-0.2], [-1,1,-0.2],
                       [-1,-1,0.2], [1,-1,0.2], [1,1,0.2], [-1,1,0.2]])

    rotated_points = np.array([rotate_point(pt, r, p, y) for pt in points])

    # Plotting the box
    fig.add_trace(go.Mesh3d(
        x=rotated_points[:,0], y=rotated_points[:,1], z=rotated_points[:,2],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='#00f2ff', opacity=0.6, name="Robot Body"
    ))

    # --- 6 AXIS LINES ---
    axes = {
        'X+': ([0, 2], [0, 0], [0, 0], 'red'),
        'X-': ([0, -2], [0, 0], [0, 0], '#ffcccb'),
        'Y+': ([0, 0], [0, 2], [0, 0], 'green'),
        'Y-': ([0, 0], [0, -2], [0, 0], '#90ee90'),
        'Z+': ([0, 0], [0, 0], [0, 2], 'blue'),
        'Z-': ([0, 0], [0, 0], [0, -2], '#add8e6')
    }

    for label, (ax_x, ax_y, ax_z, color) in axes.items():
        p2 = rotate_point(np.array([ax_x[1], ax_y[1], ax_z[1]]), r, p, y)
        fig.add_trace(go.Scatter3d(
            x=[0, p2[0]], y=[0, p2[1]], z=[0, p2[2]],
            mode='lines+text', 
            line=dict(color=color, width=5),
            text=[None, label], 
            textfont=dict(color='white', size=10),
            name=label
        ))

    # --- PENYESUAIAN UKURAN (COMPACT) ---
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d"),
            yaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d"),
            zaxis=dict(range=[-2.5,2.5], backgroundcolor="#0b0e14", gridcolor="#30363d"),
            aspectmode='cube'
        ),
        margin=dict(r=10, l=10, b=10, t=10),
        template="plotly_dark",
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Jalankan render
render_imu_plot(roll, pitch, yaw)

# Informasi Tambahan di bawah
with st.expander("ℹ️ IMU 6-Axis Data Details"):
    st.write(f"""
    - **Orientation (3-Axis):** Menampilkan sudut Roll, Pitch, dan Yaw dalam derajat.
    - **Linear (3-Axis):** Menampilkan magnitudo komponen vektor X, Y, dan Z berdasarkan posisi orientasi saat ini.
    - **Coordinate System:** Right-hand rule (Standard Robotics).
    """)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")