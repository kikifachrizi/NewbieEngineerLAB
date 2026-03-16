import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Forgix Encoding Simulator", layout="wide")

st.title("📇 Quadrature Encoding (X1, X2, X4)")
st.caption("Konsep pembacaan posisi melalui pulsa Channel A & B")

# --- Sidebar Control ---
with st.sidebar:
    st.header("Encoder Config")
    ppr = st.slider("Pulses Per Revolution (PPR)", 5, 50, 20)
    mode = st.radio("Encoding Mode", ["X1", "X2", "X4"])
    rpm = st.slider("Motor Speed (RPM)", -100, 100, 30)
    st.info("Garis vertikal menunjukkan 'sampling' titik baca sesuai mode.")

# --- State Management ---
if 'enc_angle' not in st.session_state:
    st.session_state.enc_angle = 0.0

# --- Simulator Logic ---
@st.fragment(run_every=0.1)
def run_encoder():
    dt = 0.1
    deg_per_sec = (rpm * 360) / 60
    st.session_state.enc_angle += deg_per_sec * dt
    
    t_now = st.session_state.enc_angle
    t_range = np.linspace(t_now - 90, t_now, 400) 
    
    def get_signal(angle):
        period = 360 / ppr
        a = 1 if (angle % period) < (period / 2) else 0
        b = 1 if ((angle + period/4) % period) < (period / 2) else 0
        return a, b

    # Logic Counting
    if mode == "X1": pulses = int((st.session_state.enc_angle / 360) * ppr)
    elif mode == "X2": pulses = int((st.session_state.enc_angle / 360) * ppr * 2)
    elif mode == "X4": pulses = int((st.session_state.enc_angle / 360) * ppr * 4)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Mechanical Angle", f"{int(st.session_state.enc_angle % 360)}°")
    c2.metric(f"Total Counts ({mode})", pulses)
    c3.metric("Current State (A, B)", f"{get_signal(t_now)}")

    # Plotting
    sig_a = [get_signal(t)[0] for t in t_range]
    sig_b = [get_signal(t)[1] for t in t_range]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_range, y=sig_a, name="Channel A", line_shape='hv', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=t_range, y=[s-1.5 for s in sig_b], name="Channel B", line_shape='hv', line=dict(color='magenta')))
    
    # --- PENAMBAHAN GARIS PEMBACAAN (REVISI 1) ---
    mid_t = t_now - 45 # Fokus di tengah window
    period_m = 360 / ppr
    
    # Kondisi garis berdasarkan mode
    # Garis Putih = Utama, Garis Abu = Sub-sampling
    fig.add_vline(x=mid_t, line_width=2, line_dash="dash", line_color="white") # X1 (Base)
    
    if mode in ["X2", "X4"]:
        fig.add_vline(x=mid_t + period_m/2, line_width=2, line_dash="dot", line_color="rgba(255,255,255,0.5)")
        
    if mode == "X4":
        fig.add_vline(x=mid_t + period_m/4, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.3)")
        fig.add_vline(x=mid_t + 3*period_m/4, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.3)")

    fig.update_layout(template="plotly_dark", height=450, 
                      xaxis=dict(title="Time/Angle Window", range=[t_now-90, t_now]),
                      yaxis=dict(visible=False), margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_encoder()
st.divider()
st.caption("© 2026 Newbie Engineer Lab")