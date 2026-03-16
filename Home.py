import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

st.set_page_config(page_title="Newbie Engineer Hub", layout="wide")

# --- KONEKSI GOOGLE SHEETS (OPTIMIZED WITH CACHE) ---
def get_gspread_client():
    creds_info = None
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = json.loads(st.secrets["gcp_service_account"])
    except:
        pass

    if creds_info is None:
        try:
            with open("credentials.json") as f:
                creds_info = json.load(f)
        except FileNotFoundError:
            return None

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    return gspread.authorize(creds)

# --- FUNGSI AMBIL DATA (INI YANG BIKIN RINGAN) ---
@st.cache_data(ttl=3600)  # Data disimpan di memori selama 1 jam
def load_dynamic_content():
    try:
        client = get_gspread_client()
        if client:
            spreadsheet = client.open("Newbie_Engineer_Database")
            gallery_sheet = spreadsheet.worksheet("Gallery_Content").get_all_records()
            product_sheet = spreadsheet.worksheet("Products").get_all_records()
            return gallery_sheet, product_sheet
    except Exception as e:
        st.error(f"Gagal narik data Sheets: {e}")
    return [], []

# Jalankan fungsi ambil data
gallery_data, product_data = load_dynamic_content()

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Base */
    .stApp { background-color: #0b0e14; overflow-x: hidden; }
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 800px;
        background: linear-gradient(180deg, rgba(0, 242, 255, 0.08) 0%, rgba(11, 14, 20, 0) 100%);
        pointer-events: none; z-index: -1;
    }
    
    /* Hero */
    .hero-wrapper { padding: 140px 40px 60px 40px; position: relative; }
    .hero-badge { background: rgba(0, 242, 255, 0.1); color: #00f2ff; padding: 8px 24px; border-radius: 50px; font-size: 0.85rem; font-weight: 800; letter-spacing: 4px; border: 1px solid rgba(0, 242, 255, 0.3); margin-bottom: 30px; text-transform: uppercase; }
    .hero-main-title { font-family: 'Inter', sans-serif; font-weight: 900; color: #ffffff; font-size: 6.5rem; line-height: 0.9; margin-bottom: 35px; letter-spacing: 0px; }
    .hero-highlight { color: #00f2ff; text-shadow: 0 0 40px rgba(0, 242, 255, 0.4); }
    .hero-p { color: #9ea4b0; font-size: 1.5rem; max-width: 750px; line-height: 1.7; margin-bottom: 40px; border-left: 6px solid #00f2ff; padding-left: 35px; background: linear-gradient(90deg, rgba(0,242,255,0.05), transparent); }

    /* SOCIAL MEDIA */
    .social-container { display: flex; gap: 20px; padding: 0 40px 60px 40px; }
    .social-item {
        font-size: 24px; display: flex; align-items: center; justify-content: center;
        width: 55px; height: 55px; background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 16px;
        color: #9ea4b0; text-decoration: none; transition: 0.4s;
    }
    .social-item:hover { transform: translateY(-10px); color: #00f2ff; border-color: #00f2ff; box-shadow: 0 10px 30px rgba(0, 242, 255, 0.3); }

    /* Cards */
    .section-header { font-size: 1.5rem; text-transform: uppercase; letter-spacing: 6px; color: #58a6ff; margin: 100px 0 50px 0; text-align: center; }
    .video-title-main { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin-top: 15px; border-left: 4px solid #00f2ff; padding-left: 15px; }
    .video-title-sub { color: #00f2ff; font-size: 1.1rem; font-weight: 700; margin-top: 10px; margin-bottom: 5px; text-transform: uppercase; }
    .product-card { background: #12161d; border-radius: 24px; border: 1px solid #21262d; overflow: hidden; transition: 0.4s; height: 100%; }
    .product-card:hover { border-color: #00f2ff; transform: translateY(-12px); }
    .product-img { width: 100%; height: 200px; object-fit: cover; }
    </style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-badge">The Newbie Lab v2.9</div>
        <h1 class="hero-main-title">Build <span class="hero-highlight">Intelligence.</span><br>Beyond The Steel.</h1>
        <p class="hero-p">
            Selamat datang di <span class="hero-highlight">Newbie Engineer</span>. Lab ini adalah wadah gue berbagi ilmu dan simulasi teknologi robotika. 
            Jangan cuma baca teori—eksplorasi <b>control logic</b> dan <b>autonomous system</b> lewat simulator interaktif di sini.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SOCIAL MEDIA SECTION ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <div class="social-container">
        <a href="https://www.instagram.com/kiki_fachrizi/" target="_blank" class="social-item"><i class="fab fa-instagram"></i></a>
        <a href="https://www.tiktok.com/@newbieenjinir" target="_blank" class="social-item"><i class="fab fa-tiktok"></i></a>
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=fachrizirifqy123@gmail.com" target="_blank" class="social-item"><i class="fas fa-envelope"></i></a>
        <a href="https://www.linkedin.com/in/rifqyfachrizi/" target="_blank" class="social-item"><i class="fab fa-linkedin-in"></i></a>
        <a href="https://lynk.id/kikifachrizi" target="_blank" class="social-item"><i class="fas fa-store"></i></a>
        <a href="https://www.youtube.com/@kikienjinirnewbie" target="_blank" class="social-item"><i class="fab fa-youtube"></i></a>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- GALLERY SECTION ---
st.markdown('<div class="section-header">📽️ Masterclass Gallery</div>', unsafe_allow_html=True)

def format_yt_url(url):
    if not url: return None
    if "/shorts/" in url: return url.replace("/shorts/", "/watch?v=")
    return url

if gallery_data:
    c_v_main, c_v_list = st.columns([1.8, 1])
    main_vid = gallery_data[0]
    
    with c_v_main:
        v_url = format_yt_url(main_vid.get('URL', ''))
        if v_url:
            st.video(v_url) 
            st.markdown(f'<p class="video-title-main">{main_vid.get("Judul", "Untitled")}</p>', unsafe_allow_html=True)
            st.caption(main_vid.get('Deskripsi', 'Tutorial Eksklusif.'))

    with c_v_list:
        st.write("📂 **More Lessons**")
        with st.container(height=550): 
            for vid in gallery_data[1:]:
                v_url = format_yt_url(vid.get('URL', ''))
                if v_url:
                    with st.container(border=True):
                        st.video(v_url)
                        st.markdown(f'<p class="video-title-sub">{vid.get("Judul", "Untitled")}</p>', unsafe_allow_html=True)
                        if vid.get('Deskripsi'): st.caption(vid.get('Deskripsi'))

# --- PRODUCT SECTION ---
st.markdown('<div class="section-header">🛍️ Engineering Resources</div>', unsafe_allow_html=True)
if product_data:
    p_cols = st.columns(len(product_data))
    for i, p in enumerate(product_data):
        with p_cols[i]:
            st.markdown(f"""
                <div class="product-card">
                    <img src="{p.get('Link_Gambar', '')}" class="product-img">
                    <div class="product-info">
                        <div class="product-title">{p.get('Nama', 'Product')}</div>
                        <div class="product-desc">{p.get('Deskripsi', '')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("View Details", p.get('Link_Lynkid', '#'), use_container_width=True)

# --- COMMUNITY SECTION ---
st.markdown('<div class="section-header">📩 Join The Community</div>', unsafe_allow_html=True)

with st.form("community_form", clear_on_submit=True):
    st.write("### Daftar Untuk Update Materi Terbaru")
    c1, c2 = st.columns(2)
    v_name = c1.text_input("Full Name")
    v_email = c2.text_input("Email")
    v_submit = st.form_submit_button("Register")
    
    if v_submit and v_name and v_email:
        # Re-init client khusus submit form agar tidak cache data lama
        try:
            client_submit = get_gspread_client()
            spreadsheet_submit = client_submit.open("Newbie_Engineer_Database")
            sheet = spreadsheet_submit.worksheet("Customer_Data")
            sheet.append_row([v_name, v_email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            st.success(f"Selamat bergabung {v_name}!")
            st.cache_data.clear() # Clear cache biar data baru masuk radar
        except:
            st.error("Gagal daftar, coba lagi bro.")

st.divider()
st.caption("© 2026 Newbie Engineer. Created by Kiki Fachrizi.")