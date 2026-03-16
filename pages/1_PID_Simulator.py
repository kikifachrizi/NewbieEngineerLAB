import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json

# --- Konfigurasi Page ---
st.set_page_config(page_title="PID Pro Dashboard", layout="wide")

st.markdown("""
    <style>
    div[data-testid="column"] {
        padding: 15px; border: 1px solid #3e4251; border-radius: 12px; background-color: #1e2130;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #00f2ff; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; color: #9ea4b0; }
    </style>
""", unsafe_allow_html=True)

# --- State Management ---
def reset_values():
    st.session_state.t = [0.0]
    st.session_state.y = [0.0]
    st.session_state.y_f = [0.0]
    st.session_state.err_sum = 0.0
    st.session_state.l_err = 0.0
    st.session_state.curr_v = 0.0
    st.session_state.osc_timer = 0.0
    st.session_state.target = 100.0

if 't' not in st.session_state:
    reset_values()

# --- Header ---
st.title("📟 Advanced PID Sim")
st.caption("Mastering Control System - Optimized with Plotly")

# --- Sidebar ---
with st.sidebar:
    st.header("🎛️ Tuning Parameters")
    kp = st.slider("Proportional (Kp)", 0.0, 50.0, 5.0)
    ki = st.slider("Integral (Ki)", 0.0, 20.0, 1.0)
    kd = st.slider("Derivative (Kd)", 0.0, 10.0, 0.5)
    
    st.divider()
    st.header("🛡️ Proteksi & Filtering")
    use_anti_windup = st.toggle("Enable Anti-Windup", value=True)
    max_out = st.slider("Output Saturation", 50, 255, 255)
    
    st.divider()
    use_filter = st.toggle("Enable Filter", value=True)
    alpha = st.slider("Filter Alpha", 0.0, 0.95, 0.3)
    
    st.divider()
    st.header("🔄 Mode Control")
    mode = st.radio("System Mode", ["Manual Setpoint", "Oscillation Mode"])
    
    if mode == "Manual Setpoint":
        st.session_state.target = st.number_input("Target Value", value=100.0)
    else:
        osc_amp = st.slider("Oscillation Amplitude", -200, 200, 100)
        osc_freq = st.slider("Freq / Period (s)", 2.0, 10.0, 5.0)
        if st.session_state.osc_timer == 0:
            st.session_state.target = float(osc_amp)
    
    noise_amp = st.slider("Sensor Noise", 0.0, 10.0, 1.5)
    
    if st.button("Reset Simulation", use_container_width=True):
        reset_values()
        st.rerun()

# --- Helper: Metrics ---
def calculate_metrics(time_arr, res_arr, sp):
    res_arr = np.array(res_arr)
    if len(res_arr) < 5 or sp == 0: return 0, 0, 0, 0
    pk = np.max(np.abs(res_arr)) if sp > 0 else np.min(res_arr)
    try:
        idx90 = np.where(np.abs(res_arr) >= 0.9 * np.abs(sp))[0][0]
        rt = time_arr[idx90] - time_arr[0]
    except: rt = 0
    try:
        tol = 0.02 * np.abs(sp)
        out = np.where(np.abs(res_arr - sp) > tol)[0]
        st_t = time_arr[out[-1]] if len(out) > 0 else 0
    except: st_t = 0
    err = sp - res_arr[-1]
    return pk, rt, st_t, err

# --- Main Simulation (Fragmented for Speed) ---
@st.fragment(run_every=0.1)
def run_tuner_dashboard():
    dt = 0.1
    
    if mode == "Oscillation Mode":
        st.session_state.osc_timer += dt
        if st.session_state.osc_timer >= osc_freq:
            st.session_state.target = float(osc_amp) if st.session_state.target <= 0 else -float(osc_amp)
            st.session_state.osc_timer = 0
    
    current_sp = st.session_state.target
    error = current_sp - st.session_state.curr_v
    
    st.session_state.err_sum += error * dt
    if use_anti_windup:
        limit_i = max_out / (ki if ki > 0 else 1)
        st.session_state.err_sum = np.clip(st.session_state.err_sum, -limit_i, limit_i)
    
    deriv = (error - st.session_state.l_err) / dt
    raw_out = (kp * error) + (ki * st.session_state.err_sum) + (kd * deriv)
    pwm = np.clip(raw_out, -max_out, max_out)
    
    noise = np.random.normal(0, noise_amp)
    accel = (pwm * 0.6) - (st.session_state.curr_v * 0.3) 
    st.session_state.curr_v += (accel * dt) + noise
    st.session_state.l_err = error
    
    if use_filter:
        f_val = (alpha * st.session_state.y_f[-1]) + ((1 - alpha) * st.session_state.curr_v)
    else:
        f_val = st.session_state.curr_v
    
    st.session_state.t.append(st.session_state.t[-1] + dt)
    st.session_state.y.append(st.session_state.curr_v)
    st.session_state.y_f.append(f_val)
    
    if len(st.session_state.t) > 150:
        st.session_state.t.pop(0)
        st.session_state.y.pop(0)
        st.session_state.y_f.pop(0)

    pk, rt, st_t, err = calculate_metrics(st.session_state.t, st.session_state.y_f, current_sp)

    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
    m_col1.metric("Current", f"{f_val:.1f} V")
    m_col2.metric("Setpoint", f"{current_sp:.1f} V")
    m_col3.metric("Peak", f"{pk:.1f} V")
    m_col4.metric("RiseTime", f"{rt:.2f} s")
    m_col5.metric("Settling", f"{st_t:.2f} s")
    m_col6.metric("Error", f"{err:.1f} %")

    # --- Plotly Visualization (No Matplotlib) ---
    fig = go.Figure()
    
    if use_filter:
        fig.add_trace(go.Scatter(
            x=st.session_state.t, y=st.session_state.y, 
            name="Raw Signal", 
            line=dict(color='rgba(0,242,255,0.15)', width=1)
        ))
    
    fig.add_trace(go.Scatter(
        x=st.session_state.t, y=st.session_state.y_f, 
        name="System Output", 
        line=dict(color='#00f2ff', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=st.session_state.t, y=[current_sp]*len(st.session_state.t), 
        name="Target", 
        line=dict(color='red', dash='dot', width=2),
        line_shape='hv'
    ))
    
    fig.update_layout(
        template="plotly_dark", height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Time (s)", showgrid=False, zeroline=False),
        yaxis=dict(title="Voltage (V)", showgrid=True, gridcolor="#2e323d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_tuner_dashboard()
st.divider()
st.caption("© 2026 Newbie Engineer Lab")