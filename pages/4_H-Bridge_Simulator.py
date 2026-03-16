import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Forgix H-Bridge Simulator", layout="wide")

st.title("🕹️ H-Bridge & Rotation Control")
st.caption("Visualisasi rotasi poros motor (Analog Style) dengan Skala Presisi")

# --- Sidebar ---
with st.sidebar:
    st.header("Control Panel")
    command = st.radio("Motor Direction", ["STOP", "FORWARD", "REVERSE", "BRAKE"])
    st.divider()
    v_input = st.slider("Input Voltage (V)", 0.0, 24.0, 12.0)
    st.info("Voltage memengaruhi kecepatan rotasi jarum penanda.")

# State for Animation
if 'm_rot' not in st.session_state:
    st.session_state.m_rot = 0.0

# Logic Sakelar & Speed
s1, s2, s3, s4 = 0, 0, 0, 0
motor_status = "Idle"
speed_val = (v_input / 24.0) * 45 

if command == "FORWARD":
    s1, s4, motor_status, speed = 1, 1, "Clockwise ↻", speed_val
elif command == "REVERSE":
    s2, s3, motor_status, speed = 1, 1, "Counter-Clockwise ↺", -speed_val
elif command == "BRAKE":
    s3, s4, motor_status, speed = 1, 1, "Braking (Locked)", 0
else:
    motor_status = "Coast / Idle"
    speed = 0

# --- Fragment for Animation ---
@st.fragment(run_every=0.1)
def motor_animation():
    # Update derajat rotasi
    st.session_state.m_rot = (st.session_state.m_rot - speed) % 360
    
    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("Motor Status", motor_status)
    m2.metric("Effective Power", f"{(v_input/24*100):.0f} %")
    
    fig = go.Figure()
    
    # --- 1. DRAW ROTATING MOTOR ---
    # Lingkaran Stator (Body)
    fig.add_trace(go.Scatter(x=[2], y=[2], mode="markers", 
                             marker=dict(size=95, color="#1e2130", line=dict(color="cyan", width=4)),
                             hoverinfo='skip'))
    
    # Garis Jarum (Jarum Jam)
    rad = np.radians(st.session_state.m_rot + 90)
    x_end = 2 + 0.4 * np.cos(rad)
    y_end = 2 + 0.4 * np.sin(rad)
    
    fig.add_trace(go.Scatter(x=[2, x_end], y=[2, y_end], mode="lines+markers", 
                             line=dict(color="white", width=5),
                             marker=dict(size=[0, 12], color="white"),
                             hoverinfo='skip'))

    # --- 2. DRAW SWITCHES ---
    def draw_sw(fig, x, y, state, label):
        color = "#00f2ff" if state else "#ff4b4b"
        fig.add_trace(go.Scatter(x=[x, x], y=[y, y-0.25], mode="lines", line=dict(color="gray", width=2), hoverinfo='skip'))
        if state: 
            sw_x, sw_y = [x, x], [y-0.25, y-0.55]
        else: 
            sw_x, sw_y = [x, x+0.2], [y-0.25, y-0.45]
            
        fig.add_trace(go.Scatter(x=sw_x, y=sw_y, mode="lines+text",
                                 line=dict(color=color, width=5), text=[label, ""], 
                                 textposition="top left", hoverinfo='skip'))

    draw_sw(fig, 1.2, 3.5, s1, "S1")
    draw_sw(fig, 2.8, 3.5, s2, "S2")
    draw_sw(fig, 1.2, 1.3, s3, "S3")
    draw_sw(fig, 2.8, 1.3, s4, "S4")

    # Jalur Kabel
    fig.add_trace(go.Scatter(x=[1.2, 2.8], y=[3.7, 3.7], mode="lines", line=dict(color="orange", width=3), hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[1.2, 2.8], y=[0.5, 0.5], mode="lines", line=dict(color="white", width=3), hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[1.2, 2, 2.8], y=[2, 2, 2], mode="lines", line=dict(color="gray", width=1), hoverinfo='skip'))

    fig.update_layout(
        template="plotly_dark", 
        showlegend=False, 
        height=450,
        # FIX: Memaksa aspek rasio 1:1 agar jarum tidak berubah panjang (distorsi)
        yaxis=dict(visible=False, range=[0, 4], scaleanchor="x", scaleratio=1),
        xaxis=dict(visible=False, range=[0.5, 3.5]),
        margin=dict(l=0, r=0, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

motor_animation()
st.divider()
st.caption("© 2026 Newbie Engineer Lab")