import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="PWM Simulator", layout="wide")

st.title("⚡ PWM Modulation (Pulse Width Modulation)")
st.caption("Bagaimana sinyal digital mengontrol power analog")

# --- Sidebar ---
with st.sidebar:
    st.header("PWM Settings")
    duty_cycle = st.slider("Duty Cycle (%)", 0, 100, 50)
    freq_hz = st.slider("Frequency (Hz)", 1, 50, 10)
    v_max = st.number_input("Source Voltage (V)", value=12.0)

if 'pwm_t' not in st.session_state:
    st.session_state.pwm_t = 0.0

# --- Simulator Logic ---
@st.fragment(run_every=0.1)
def run_pwm():
    st.session_state.pwm_t += 0.1
    t_now = st.session_state.pwm_t
    
    # Window waktu yang ditampilkan (0.5 detik)
    t_axis = np.linspace(t_now - 0.5, t_now, 500)
    
    def get_pwm_val(t_val):
        period = 1 / freq_hz
        if (t_val % period) < (duty_cycle/100 * period):
            return v_max
        return 0

    pwm_values = [get_pwm_val(t) for t in t_axis]
    v_avg = (duty_cycle/100) * v_max

    # --- Tambahan Kalkulasi ---
    period = 1 / freq_hz  # T = 1/f
    t_on = period * (duty_cycle / 100)
    t_off = period - t_on

    # --- Tampilkan Informasi di Dashboard ---
    c1, c2, c3 ,c4= st.columns(4)
    c1.metric("Duty Cycle", f"{duty_cycle}%", f"{int(duty_cycle * 2.55)} / 255 (8-bit)")
    c2.metric("Period (T)", f"{period*1000:.1f} ms")
    c3.metric("Frequency", f"{freq_hz} Hz")
    c4.metric("Voltage Output (V_avg)", f"{v_avg:.2f} V")

    # Plotting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_axis, y=pwm_values, name="PWM Signal", 
                             line_shape='hv', fill='tozeroy', line=dict(color='#00f2ff')))
    fig.add_trace(go.Scatter(x=t_axis, y=[v_avg]*len(t_axis), name="V Average", 
                             line=dict(color='orange', dash='dash')))

    fig.update_layout(template="plotly_dark", height=450,
                      xaxis=dict(title="Time (s)", range=[t_now-0.5, t_now]),
                      yaxis=dict(title="Voltage (V)", range=[-1, v_max+2]))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_pwm()

# Informasi Tambahan di bawah
with st.expander("ℹ️ PWM Details"):
    st.write(f"""
    - **High Frequency:** Garis-garis vertikal di grafik bakal makin rapat (siklus makin cepet).
    - **Low Frequency:** Garis-garis vertikal bakal renggang.
    - **Duty Cycle:** Ngatur lebar "bukit" (area biru) di dalam satu siklus tersebut.
    """)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")

 

 

 