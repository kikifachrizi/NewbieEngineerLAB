import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Konfigurasi Page ---
st.set_page_config(page_title="Forgix Encoding Simulator", layout="wide")

st.title("📇 Quadrature Encoding (X1, X2, X4)")
st.caption("Konsep pembacaan posisi melalui pulsa Channel A & B - Optimized with Plotly")

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

# --- Simulator Logic (Fragmented) ---
@st.fragment
def run_encoder():
    dt = 0.1
    deg_per_sec = (rpm * 360) / 60
    st.session_state.enc_angle += deg_per_sec * dt
    
    t_now = st.session_state.enc_angle
    t_range = np.linspace(t_now - 90, t_now, 400) 
    period_m = 360 / ppr

    # Vectorized Signal Calculation (Dihitung massal pake Numpy, jauh lebih ringan)
    def get_signals_array(angles, period):
        a = np.where((angles % period) < (period / 2), 1, 0)
        b = np.where(((angles + period/4) % period) < (period / 2), 1, 0)
        return a, b

    sig_a, sig_b = get_signals_array(t_range, period_m)
    current_a, current_b = np.where((t_now % period_m) < (period_m / 2), 1, 0), np.where(((t_now + period_m/4) % period_m) < (period_m / 2), 1, 0)

    # Logic Counting
    if mode == "X1": pulses = int((st.session_state.enc_angle / 360) * ppr)
    elif mode == "X2": pulses = int((st.session_state.enc_angle / 360) * ppr * 2)
    elif mode == "X4": pulses = int((st.session_state.enc_angle / 360) * ppr * 4)

    # Metrics Layout
    c1, c2, c3 = st.columns(3)
    c1.metric("Mechanical Angle", f"{int(st.session_state.enc_angle % 360)}°")
    c2.metric(f"Total Counts ({mode})", pulses)
    c3.metric("Current State (A, B)", f"({int(current_a)}, {int(current_b)})")

    # --- Plotting with Plotly ---
    fig = go.Figure()
    
    # Channel A
    fig.add_trace(go.Scatter(
        x=t_range, y=sig_a, 
        name="Channel A", 
        line_shape='hv', 
        line=dict(color='#00f2ff', width=2)
    ))
    
    # Channel B (Offset y axis for visibility)
    fig.add_trace(go.Scatter(
        x=t_range, y=sig_b - 1.5, 
        name="Channel B", 
        line_shape='hv', 
        line=dict(color='#ff00ff', width=2)
    ))
    
    # Vertikal Sampling Markers
    mid_t = t_now - 45 
    fig.add_vline(x=mid_t, line_width=2, line_dash="dash", line_color="white") 
    
    if mode in ["X2", "X4"]:
        fig.add_vline(x=mid_t + period_m/2, line_width=1.5, line_dash="dot", line_color="rgba(255,255,255,0.5)")
        
    if mode == "X4":
        fig.add_vline(x=mid_t + period_m/4, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.3)")
        fig.add_vline(x=mid_t + 3*period_m/4, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.3)")

    fig.update_layout(
        template="plotly_dark", 
        height=400, 
        showlegend=True,
        xaxis=dict(title="Encoder Angle Position", range=[t_now-90, t_now], showgrid=False),
        yaxis=dict(visible=False), 
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_encoder()
st.divider()
st.caption("© 2026 Newbie Engineer Lab")