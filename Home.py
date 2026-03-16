import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

st.set_page_config(page_title="Newbie Engineer Hub", layout="wide")

# --- KONEKSI GOOGLE SHEETS (HYBRID MODE) ---
def get_gspread_client():
    creds_info = None
    
    # 1. Coba cari di Streamlit Secrets (Cloud)
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = json.loads(st.secrets["gcp_service_account"])
    except:
        pass

    # 2. Kalau ga ada, cari file fisik (Lokal)
    if creds_info is None:
        try:
            with open("credentials.json") as f:
                creds_info = json.load(f)
        except FileNotFoundError:
            st.error("Waduh! File 'credentials.json' ga ketemu di folder project lo bro.")
            return None

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    return gspread.authorize(creds)

# Initialize Sheets
try:
    client = get_gspread_client()
    spreadsheet = client.open("Newbie_Engineer_Database")
except Exception as e:
    st.error(f"Koneksi Database Gagal: {e}")

# --- AMBIL DATA KONTEN ---
def load_dynamic_content():
    gallery_sheet = spreadsheet.worksheet("Gallery_Content").get_all_records()
    product_sheet = spreadsheet.worksheet("Products").get_all_records()
    return gallery_sheet, product_sheet

try:
    gallery_data, product_data = load_dynamic_content()
except:
    gallery_data, product_data = [], []

# --- CUSTOM CSS (Clean, Social Bar, & Hover Animations) ---
st.markdown("""
    <style>
    /* Global Base */
    .stApp { background-color: #0b0e14; overflow-x: hidden; }
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 800px;
        background: linear-gradient(180deg, rgba(0, 242, 255, 0.08) 0%, rgba(11, 14, 20, 0) 100%);
        pointer-events: none; z-index: -1;
    }
    
    /* Hero Styling */
    .hero-wrapper { padding: 140px 40px 60px 40px; position: relative; display: flex; flex-direction: column; align-items: flex-start; }
    
    @keyframes spark-drift {
        0% { transform: translateY(0) scale(1.5); opacity: 0; }
        20% { opacity: 1; }
        100% { transform: translateY(-250px) scale(0); opacity: 0; }
    }
    .sparkle { position: absolute; width: 3px; height: 45px; background: linear-gradient(to top, transparent, #00f2ff, #ffffff); box-shadow: 0 0 20px #00f2ff; animation: spark-drift 5s infinite linear; pointer-events: none; }

    .hero-badge { background: rgba(0, 242, 255, 0.1); color: #00f2ff; padding: 8px 24px; border-radius: 50px; font-size: 0.85rem; font-weight: 800; letter-spacing: 4px; border: 1px solid rgba(0, 242, 255, 0.3); margin-bottom: 30px; text-transform: uppercase; }
    .hero-main-title { font-family: 'Inter', sans-serif; font-weight: 900; color: #ffffff; font-size: 6.5rem; line-height: 0.9; margin-bottom: 35px; letter-spacing: 0px; }
    .hero-highlight { color: #00f2ff; text-shadow: 0 0 40px rgba(0, 242, 255, 0.4); }
    .hero-p { color: #9ea4b0; font-size: 1.5rem; max-width: 750px; line-height: 1.7; margin-bottom: 40px; border-left: 6px solid #00f2ff; padding-left: 35px; background: linear-gradient(90deg, rgba(0,242,255,0.05), transparent); }

    /* SOCIAL MEDIA SECTION */
    .social-container { display: flex; gap: 20px; padding: 0 40px 60px 40px; }
    .social-item {
        font-size: 24px; 
        display: flex; align-items: center; justify-content: center;
        width: 55px; height: 55px; background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 16px;
        color: #9ea4b0; text-decoration: none; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .social-item:hover {
        transform: translateY(-10px); color: #00f2ff; border-color: #00f2ff;
        background: rgba(0, 242, 255, 0.1); box-shadow: 0 10px 30px rgba(0, 242, 255, 0.3);
    }

    /* Video & Product Cards */
    .video-title-main { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin-top: 15px; border-left: 4px solid #00f2ff; padding-left: 15px; }
    .video-title-sub { color: #00f2ff; font-size: 1.1rem; font-weight: 700; margin-top: 10px; margin-bottom: 25px; text-transform: uppercase; line-height: 1.3; }
    .product-card { background: #12161d; border-radius: 24px; border: 1px solid #21262d; overflow: hidden; transition: 0.4s; height: 100%; }
    .product-card:hover { border-color: #00f2ff; transform: translateY(-12px); box-shadow: 0 25px 50px rgba(0,0,0,0.6); }
    .product-img { width: 100%; height: 200px; object-fit: cover; }
    .product-info { padding: 25px; }
    .product-title { color: #fff; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; }
    .product-desc { color: #8b949e; font-size: 0.9rem; line-height: 1.5; }

    .section-header { font-size: 1.5rem; text-transform: uppercase; letter-spacing: 6px; color: #58a6ff; margin: 100px 0 50px 0; text-align: center; }
    [data-testid="stForm"] { background: #12161d; border-radius: 24px; border: 1px solid #30363d; padding: 50px; }
    </style>

    <div class="sparkle" style="left: 10%; animation-delay: 0s;"></div>
    <div class="sparkle" style="left: 30%; animation-delay: 2s;"></div>
    <div class="sparkle" style="left: 55%; animation-delay: 1s;"></div>
    <div class="sparkle" style="left: 80%; animation-delay: 3s;"></div>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-badge">The Newbie Lab v2.5</div>
        <h1 class="hero-main-title">Build <span class="hero-highlight">Intelligence.</span><br>Beyond The Steel.</h1>
        <p class="hero-p">
            Selamat datang di <span class="hero-highlight">Newbie Engineer</span>. Lab ini adalah wadah gue berbagi ilmu dan simulasi teknologi robotika. 
            Jangan cuma baca teori—eksplorasi <b>control logic</b> dan <b>autonomous system</b> lewat simulator interaktif yang udah gue siapin.
            Lu juga bisa eksplore <span class="hero-highlight">video course</span> dan <span class="hero-highlight">E-book</span> yang udah gue siapin dibawah....
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SOCIAL MEDIA SECTION (Bungkus pake st.markdown) ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <div class="social-container">
        <a href="https://www.instagram.com/kiki_fachrizi/" target="_blank" class="social-item" title="Instagram">
            <i class="fab fa-instagram"></i>
        </a>
        <a href="https://www.tiktok.com/@newbieenjinir" target="_blank" class="social-item" title="TikTok">
            <i class="fab fa-tiktok"></i>
        </a>
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=fachrizirifqy123@gmail.com" target="_blank" class="social-item" title="Gmail">
            <i class="fas fa-envelope"></i>
        </a>
        <a href="https://www.linkedin.com/in/rifqyfachrizi/" target="_blank" class="social-item" title="LinkedIn">
            <i class="fab fa-linkedin-in"></i>
        </a>
        <a href="https://lynk.id/kikifachrizi" target="_blank" class="social-item" title="Lynk.id">
            <i class="fas fa-store"></i>
        </a>
        <a href="https://www.youtube.com/@kikienjinirnewbie" target="_blank" class="social-item" title="YouTube">
            <i class="fab fa-youtube"></i>
        </a>
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
                    v_title = vid.get('Judul', 'Untitled Lesson')
                    # Ambil data deskripsi dari sheet
                    v_desc = vid.get('Deskripsi', '') 
                    
                    if v_url:
                        with st.container(border=True):
                            st.video(v_url)
                            # Tampilkan Judul
                            st.markdown(f'<p class="video-title-sub">{v_title}</p>', unsafe_allow_html=True)
                            # Tampilkan Deskripsi (pake st.caption atau font kecil)
                            if v_desc:
                                st.caption(v_desc)

st.divider()

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

def save_to_sheets(name, email):
    try:
        sheet = spreadsheet.worksheet("Customer_Data")
        sheet.append_row([name, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except: return False

with st.form("community_form", clear_on_submit=True):
    st.write("### Daftar Untuk Update Materi Terbaru")
    c1, c2 = st.columns(2)
    v_name = c1.text_input("Full Name", placeholder="Jhon Doe")
    v_email = c2.text_input("Email", placeholder="nama@email.com")
    v_submit = st.form_submit_button("Register")
    if v_submit and v_name and v_email:
        if save_to_sheets(v_name, v_email):
            st.success(f"Selamat bergabung {v_name}! Senang bisa terhubung dengan sesama antusias robotika. Akses materi dan update lab akan segera kami informasikan melalui email.")

st.divider()
st.caption("© 2026 Newbie Engineer. Created by Kiki Fachrizi.")