import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Konfigurasi Page ---
st.set_page_config(page_title="PWM Simulator", layout="wide")

st.title("⚡ PWM Modulation (Pulse Width Modulation)")
st.caption("Bagaimana sinyal digital mengontrol power analog - Optimized with Plotly")

# --- Sidebar ---
with st.sidebar:
    st.header("PWM Settings")
    duty_cycle = st.slider("Duty Cycle (%)", 0, 100, 50)
    freq_hz = st.slider("Frequency (Hz)", 1, 50, 10)
    v_max = st.number_input("Source Voltage (V)", value=12.0)

if 'pwm_t' not in st.session_state:
    st.session_state.pwm_t = 0.0

# --- Simulator Logic (Fragmented for Speed) ---
@st.fragment(run_every=0.1)
def run_pwm():
    st.session_state.pwm_t += 0.1
    t_now = st.session_state.pwm_t
    
    # Window waktu yang ditampilkan (0.5 detik)
    t_axis = np.linspace(t_now - 0.5, t_now, 500)
    
    # Perhitungan Perioda
    period = 1 / freq_hz
    v_avg = (duty_cycle/100) * v_max
    
    # Vectorized Calculation (Jauh lebih ringan dibanding looping manual)
    # Menghitung sisa bagi untuk menentukan posisi dalam satu perioda
    t_relative = t_axis % period
    pwm_values = np.where(t_relative < (duty_cycle/100 * period), v_max, 0)

    # --- Tampilkan Informasi di Dashboard ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Duty Cycle", f"{duty_cycle}%", f"{int(duty_cycle * 2.55)} / 255 (8-bit)")
    c2.metric("Period (T)", f"{period*1000:.1f} ms")
    c3.metric("Frequency", f"{freq_hz} Hz")
    c4.metric("Voltage Output (V_avg)", f"{v_avg:.2f} V")

    # --- Plotting with Plotly ---
    fig = go.Figure()
    
    # Sinyal PWM (Kotak)
    fig.add_trace(go.Scatter(
        x=t_axis, y=pwm_values, 
        name="PWM Signal", 
        line_shape='hv', 
        fill='tozeroy', 
        line=dict(color='#00f2ff', width=2),
        fillcolor='rgba(0, 242, 255, 0.1)'
    ))
    
    # Garis Tegangan Rata-rata
    fig.add_trace(go.Scatter(
        x=t_axis, y=[v_avg]*len(t_axis), 
        name="V Average", 
        line=dict(color='orange', dash='dash', width=2)
    ))

    fig.update_layout(
        template="plotly_dark", 
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Time (s)", range=[t_now-0.5, t_now], showgrid=False),
        yaxis=dict(title="Voltage (V)", range=[-1, v_max+2], showgrid=True, gridcolor="#2e323d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

run_pwm()

# Informasi Tambahan
with st.expander("ℹ️ PWM Details"):
    st.write(f"""
    - **High Frequency:** Siklus makin cepat (kerapatan gelombang tinggi). Bikin motor lebih halus tapi driver lebih panas.
    - **Duty Cycle:** Mengatur lebar pulsa ON. Semakin lebar, semakin besar energi (V_avg) yang dikirim ke beban.
    - **8-bit Mapping:** Di Arduino (0-255), nilai {duty_cycle}% setara dengan **{int(duty_cycle * 2.55)}**.
    """)

st.divider()
st.caption("© 2026 Newbie Engineer Lab")