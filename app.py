import streamlit as st
import pandas as pd
import requests
import io

# ==============================================================================
# 1. CONFIGURACIÓN DEL MOTOR (TITAN ENGINE)
# ==============================================================================
st.set_page_config(
    page_title="Radar Subvenciones | TITAN EDITION",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. INYECCIÓN CSS (EL ALMA DEL DISEÑO)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTAR FUENTE FUTURISTA */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;600;800&display=swap');

    /* --- RESET GLOBAL --- */
    .stApp {
        background-color: #050505 !important; /* Negro Puro */
        color: white !important;
    }
    
    /* Eliminar márgenes molestos de Streamlit arriba */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* --- ESTILO DE LA TARJETA (TITAN CARD) --- */
    /* Esta clase envuelve todo el bloque visual superior */
    .titan-card {
        background: #111111;
        border: 1px solid #333;
        border-radius: 16px;
        overflow: hidden; /* Esto recorta la imagen en las esquinas */
        position: relative;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 0px; /* Pegado al botón de abajo */
        box-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }

    /* EL HOVER MÁGICO */
    .titan-card:hover {
        transform: translateY(-8px) scale(1.01);
        border-color: #00f2ff; /* CIAN ELÉCTRICO */
        box-shadow: 0 0 40px rgba(0, 242, 255, 0.2);
        z-index: 2;
    }

    /* --- IMAGEN FULL WIDTH --- */
    .titan-img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-bottom: 1px solid #333;
        filter: brightness(0.85);
        transition: 0.3s;
    }
    .titan-card:hover .titan-img {
        filter: brightness(1.1);
    }

    /* --- CONTENIDO DE LA TARJETA --- */
    .titan-body {
        padding: 20px;
        background: linear-gradient(180deg, #111111 0%, #0a0a0a 100%);
    }

    /* TÍTULO */
    .titan-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 18px;
        line-height: 1.4;
        color: #ffffff;
        margin-bottom: 15px;
        min-height: 50px; /* Para alinear alturas */
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* BADGE DE PROBABILIDAD (FLOTANTE) */
    .titan-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0,0,0,0.7);
        backdrop-filter: blur(4px);
        padding: 5px 12px;
        border-radius: 20px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1px;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* TAGS */
    .titan-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 20px;
    }
    .t-tag {
        font-size: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 8px;
        border-radius: 6px;
        color: white;
    }

    /* GRID DE DATOS (PRECIO Y FECHA) */
    .titan-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        border-top: 1px solid #222;
        padding-top: 15px;
    }
    .t-data-box {
        text-align: center;
    }
    .t-label {
        font-size: 10px;
        color: #666;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .t-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #00f2ff; /* CIAN */
    }

    /* --- MODIFICACIÓN DE STREAMLIT ELEMENTS --- */
    /* Hacemos que el expander parezca parte de la tarjeta */
    .stExpander {
        background-color: #0a0a0a !important;
        border: 1px solid #333 !important;
        border-top: none !important;
        border-radius: 0 0 16px 16px !important;
        margin-top: -5px !important; /* Pegarlo visualmente */
    }
    .streamlit-expanderContent p { color: #ccc !important; font-size: 14px; }
    
    /* Inputs */
    .stTextInput input {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        color: white !important;
        border-radius: 10px;
    }
    .stTextInput input:focus { border-color: #00f2ff !important; }

    /* Ocultar menú */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SEGURIDAD (SIMPLE Y ROBUSTA)
# ==============================================================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br><h1 style='text-align: center; color: #00f2ff;'>🛡️ TITAN SECURITY</h1>", unsafe_allow_html=True)
            st.text_input("ACCESS CODE", type="password", on_change=password_entered, key="password")
            st.markdown("<p style='text-align: center; color: #444; font-size: 12px;'>SYSTEM LOCKED • AUTHORIZED PERSONNEL ONLY</p>", unsafe_allow_html=True)
        return False
    return True

# ==============================================================================
# 4. LÓGICA DE DATOS
# ==============================================================================
@st.cache_data(ttl=60)
def load_data():
    try:
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

# Helper para colores de tags
def get_tag_bg(tag):
    t = tag.lower()
    if "next" in t: return "linear-gradient(90deg, #00416A, #002135)" # Azul profundo
    if "subvenc" in t: return "linear-gradient(90deg, #134E5E, #71B280)" # Verde esmeralda
    return "linear-gradient(90deg, #232526, #414345)" # Gris metal

# Helper para imágenes fiables (Picsum con semilla)
def get_img_url(sector, titulo):
    # Generamos una semilla basada en el texto para que la foto sea siempre la misma para la misma fila
    # pero diferente entre filas.
    combined = (str(sector) + str(titulo)).lower()
    keyword = "business"
    if "agro" in combined: keyword = "nature"
    elif "tech" in combined or "digital" in combined: keyword = "computer"
    elif "indus" in combined: keyword = "factory"
    elif "solar" in combined: keyword = "sun"
    elif "coche" in combined: keyword = "car"
    elif "univ" in combined: keyword = "books"
    
    # Usamos picsum con seed para estabilidad total
    seed = hash(combined) % 1000
    return f"https://picsum.photos/id/{seed}/800/400"

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
if check_password():
    
    # --- HEADER ---
    c_logo, c_search = st.columns([2, 3])
    with c_logo:
        st.markdown("<h1 style='margin:0; font-size: 36px;'>💠 RADAR <span style='color:#00f2ff'>TITAN</span></h1>", unsafe_allow_html=True)
        st.caption("DEEP SCANNING SYSTEM v27.0")
    with c_search:
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True) # Spacer
        query = st.text_input("", placeholder="🔍 Buscar oportunidad...", label_visibility="collapsed")

    st.markdown("---")

    df = load_data()

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        # --- GRID RENDER ---
        # Usamos 2 columnas anchas
        cols = st.columns(2)
        
        for i, row in df.iterrows():
            if pd.isna(row.iloc[1]): continue
            
            # Preparar datos para HTML
            titulo = row.iloc[1]
            tags_raw = str(row.iloc[2]).split('|')
            tags_html = "".join([f"<span class='t-tag' style='background: {get_tag_bg(t.strip())}'>{t.strip()}</span>" for t in tags_raw])
            cuantia = row.iloc[3]
            plazo = row.iloc[4]
            img_url = get_img_url(row.iloc[5], titulo)
            
            # Badge probabilidad
            prob = str(row.iloc[9]).strip()
            color_prob = "#00f2ff" if "Alta" in prob else "#ffcc00"
            badge_html = f"<div class='titan-badge' style='color:{color_prob}; border-color:{color_prob};'>● {prob.upper()}</div>"

            # HTML CARD COMPLETA (Esto garantiza el diseño perfecto)
            html_card = f"""
            <div class="titan-card">
                {badge_html}
                <img src="{img_url}" class="titan-img">
                <div class="titan-body">
                    <div class="titan-title">{titulo}</div>
                    <div class="titan-tags">{tags_html}</div>
                    <div class="titan-grid">
                        <div class="t-data-box">
                            <div class="t-label">Cuantía</div>
                            <div class="t-value">{cuantia}</div>
                        </div>
                        <div class="t-data-box">
                            <div class="t-label">Plazo</div>
                            <div class="t-value">{plazo}</div>
                        </div>
                    </div>
                </div>
            </div>
            """

            # Renderizar en columna
            with cols[i % 2]:
                # 1. Pintamos la tarjeta visual (HTML puro, sin márgenes de Streamlit)
                st.markdown(html_card, unsafe_allow_html=True)
                
                # 2. Funcionalidad de Streamlit (Expander) pegada abajo
                # El CSS se encarga de que parezca una sola pieza
                with st.expander("🔻 ESTRATEGIA Y ACCESO"):
                    st.markdown("#### 🧠 Análisis IA")
                    st.write(row.iloc[6])
                    st.markdown("#### 📜 Requisitos")
                    st.write(row.iloc[8])
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.link_button("🔗 ACCEDER AL BOE", str(row.iloc[0]), use_container_width=True)
                
                st.write("") # Espacio entre filas

    else:
        st.error("DATABASE CONNECTION FAILED.")

    # Footer
    st.markdown("<br><br><div style='text-align: center; color: #333; font-size: 10px;'>TITAN ENGINE // SECURE CONNECTION</div>", unsafe_allow_html=True)
