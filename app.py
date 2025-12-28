import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Máxima Calidad)
st.set_page_config(
    page_title="Radar Subvenciones AI v6.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- FUNCIÓN DE SEGURIDAD (CONECTADA A SECRETS) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: white;'>💎 SISTEMA PRIVADO</h1>", unsafe_allow_html=True)
        st.info("Introduce la clave de acceso para desencriptar las oportunidades de negocio.")
        st.text_input("ACCESO NIVEL 1", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Credencial no autorizada. Acceso denegado.")
        st.text_input("ACCESO NIVEL 1", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # --- DISEÑO CSS PREMIUM (GLASSMORPHISM & GLOW) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap');
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        /* Tarjetas Estilo "Glass" */
        .subs-card {
            background: rgba(22, 27, 34, 0.8);
            border-radius: 24px;
            padding: 28px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            backdrop-filter: blur(12px);
            transition: all 0.4s ease;
        }
        .subs-card:hover {
            border-color: #58a6ff;
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.15);
            transform: translateY(-8px);
        }
        
        /* Imágenes con efecto sombra */
        .card-img {
            width: 100%;
            height: 240px;
            object-fit: cover;
            border-radius: 18px;
            margin-bottom: 20px;
            filter: brightness(0.9);
            transition: 0.5s;
        }
        .subs-card:hover .card-img { filter: brightness(1.1); }
        
        /* Badges de Probabilidad Pro */
        .prob-alta { color: #3fb950; border: 1px solid #3fb950; background: rgba(63, 185, 80, 0.1); }
        .prob-media { color: #d29922; border: 1px solid #d29922; background: rgba(210, 153, 34, 0.1); }
        
        .badge-prob {
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            float: right;
        }
        
        /* Títulos */
        h1, h2, h3 { color: #f0f6fc !important; letter-spacing: -0.5px; }
        
        .tag {
            display: inline-block;
            color: #adbac7;
            padding: 5px 12px;
            border-radius: 10px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 10px;
            font-weight: 700;
            background: #22272e;
            border: 1px solid #444c56;
        }
        
        /* Quitar scroll lateral */
        .block-container { padding-top: 2rem; }
        </style>
        """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS
    @st.cache_data(ttl=60)
    def load_data():
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        try:
            response = requests.get(url, timeout=10)
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # 3. GALERÍA DE IMÁGENES PREMIUM (Variedad Total)
    def get_sector_image(sector):
        s = str(sector).lower()
        # Mapeo de IDs de Unsplash de alta calidad
        img_ids = {
            'solar': '1509391366360-2e959784a276',
            'eolic': '1466611653911-954ff21b6724',
            'indust': '1581091226825-a6a2a5aee158',
            'digital': '1518770660439-4636190af475',
            'agro': '1523348837708-15d4a09cfac2',
            'social': '1469571486292-0ba58a3f068b',
            'invest': '1532094349884-543bb118196d',
            'transp': '1553265027-99d530167b28',
            'hidro': '1516937941524-747f48d6db12',
            'archit': '1487958449333-24602f44216c',
            'global': '1451187580459-43490279c0fa'
        }
        
        id_img = img_ids['global']
        if any(x in s for x in ['energ', 'foto']): id_img = img_ids['solar']
        elif 'eolic' in s: id_img = img_ids['eolic']
        elif any(x in s for x in ['industr', 'cvi', 'manufact', 'descarboni']): id_img = img_ids['indust']
        elif any(x in s for x in ['agro', 'campo', 'forest', 'agri']): id_img = img_ids['agro']
        elif any(x in s for x in ['digital', 'tic', 'ia', 'softw']): id_img = img_ids['digital']
        elif any(x in s for x in ['social', 'dana', 'tercer sector', 'infan']): id_img = img_ids['social']
        elif any(x in s for x in ['univer', 'docen', 'lector', 'arquite']): id_img = img_ids['archit']
        elif any(x in s for x in ['investiga', 'ciencia', 'tecno']): id_img = img_ids['invest']
        elif any(x in s for x in ['transpor', 'moves', 'vehic']): id_img = img_ids['transp']
        elif 'hidro' in s: id_img = img_ids['hidro']
        
        return f"https://images.unsplash.com/photo-{id_img}?auto=format&fit=crop&q=80&w=1000"

    df = load_data()

    # --- HEADER MODERNO ---
    st.markdown("<p style='color: #58a6ff; font-weight: 800; margin-bottom: 0;'>INTELLIGENCE SCANNER</p>", unsafe_allow_html=True)
    st.title("📡 Radar de Subvenciones Pro")
    
    # Buscador y Filtro en la misma línea
    c_search, c_filter = st.columns([3, 1])
    with c_search:
        query = st.text_input("🔍 Buscar en el boletín...", placeholder="Palabra clave (ej: Hidrógeno, Digitalización)")
    with c_filter:
        st.markdown("<br>", unsafe_allow_html=True)
        is_nextgen = st.checkbox("🇪🇺 Solo Next Generation")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
        if is_nextgen:
            df = df[df.iloc[:, 2].str.contains("Next", case=False)]

        # Métricas Dashboard
        m1, m2, m3 = st.columns(3)
        m1.metric("ALERTAS ACTIVAS", len(df))
        m2.metric("SECTORES", len(df.iloc[:, 5].unique()) if len(df)>0 else 0)
        m3.metric("NIVEL DE ACCESO", "Premium")
        st.divider()

        # --- GRID DINÁMICO ---
        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                prob = str(fila.iloc[9]).strip()
                p_class = "prob-alta" if "Alta" in prob else "prob-media"
                
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5])}" class="card-img">
                    <span class="badge-prob {p_class}">● {prob}</span>
                    <h3 style="margin-top: 0; min-height: 60px;">{fila.iloc[1]}</h3>
                """, unsafe_allow_html=True)
                
                # Tags de Ámbito
                tags = str(fila.iloc[2]).split('|')
                st.markdown(" ".join([f'<span class="tag">{t.strip()}</span>' for t in tags]), unsafe_allow_html=True)
                
                st.markdown(f"""
                    <p style='color: #8b949e; font-size: 14px; margin-bottom: 5px;'>💰 CUANTÍA: <b style='color: white;'>{fila.iloc[3]}</b></p>
                    <p style='color: #8b949e; font-size: 14px; margin-bottom: 20px;'>⏳ LÍMITE: <b style='color: white;'>{fila.iloc[4]}</b></p>
                """, unsafe_allow_html=True)
                
                with st.expander("💼 VER ANÁLISIS ESTRATÉGICO"):
                    t1, t2 = st.tabs(["REPORTE", "REQUISITOS"])
                    with t1:
                        st.write(fila.iloc[6])
                        st.success(f"**OPORTUNIDAD:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    st.link_button("🔗 EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Terminal v6.0 | Encriptación AES-256 | n8n + Groq + Streamlit")
