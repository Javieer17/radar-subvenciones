import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v12.5",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- FUNCIÓN DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: white;'>🔒 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        st.text_input("Introduce Credencial Master", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # --- DISEÑO CSS "INTEGRACIÓN TOTAL V2" ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Forzar fondo oscuro */
        .stApp { background-color: #0d1117 !important; }
        
        /* Estilo de la burbuja (Contenedor nativo de Streamlit hackeado) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 30px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            padding: 0px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4) !important;
            transition: all 0.3s ease !important;
            margin-bottom: 25px !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #58a6ff !important;
            transform: translateY(-5px) !important;
        }

        /* Foto del sector ajustada al techo */
        .header-img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-radius: 30px 30px 0 0;
            display: block;
        }

        /* Contenido con padding */
        .content-padding {
            padding: 20px 25px 25px 25px;
        }

        .sub-title {
            color: #ffffff !important;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 10px;
        }

        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }

        .tag {
            color: white !important;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }

        /* Etiquetas de datos abajo */
        .data-label { color: #8b949e !important; font-size: 11px; font-weight: 700; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 0.5px;}
        .data-value { color: #58a6ff !important; font-size: 18px !important; font-weight: 800; margin-top: -5px;}

        .badge-prob {
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 900;
            text-transform: uppercase;
            float: right;
        }
        .prob-alta { color: #3fb950; border: 1px solid #3fb950; background: rgba(63,185,80,0.1); }
        .prob-media { color: #d29922; border: 1px solid #d29922; background: rgba(210,153,34,0.1); }
        
        .stExpander {
            background-color: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 15px !important;
            margin-bottom: 15px !important;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS
    @st.cache_data(ttl=60)
    def load_data():
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        try:
            response = requests.get(url, timeout=15)
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # 3. COLORES DE TAGS
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t or "prtr" in t: return "#1f6feb" 
        if "subvenc" in t: return "#238636" 
        if "prestamo" in t: return "#da3633" 
        if "estatal" in t: return "#8957e5" 
        return "#444c56"

    # 4. IMÁGENES PREMIUM REVISADAS
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        # IDs de fotos de alta calidad que cargan siempre
        img_id = '1451187580459-43490279c0fa' # Default Tech
        
        if 'dana' in combined or 'social' in combined or 'tercer sector' in combined: 
            img_id = '1593113501539-d91f43f130ac' # Ayuda humanitaria / Comunidad
        elif any(x in combined for x in ['univ', 'docen', 'lector', 'curso', 'beca']): 
            img_id = '1541339905120-f579ae5af072' # Universidad / Libros
        elif any(x in combined for x in ['energ', 'foto', 'placa', 'solar']): 
            img_id = '1509391366360-2e959784a276' # Solar
        elif any(x in combined for x in ['eolic', 'viento', 'hidro']): 
            img_id = '1466611653911-954ff21b6724' # Viento / Energía
        elif any(x in combined for x in ['indust', 'manufact', 'fábrica', 'tecnol']): 
            img_id = '1581091226825-a6a2a5aee158' # Industrial
        elif any(x in combined for x in ['digital', 'tic', 'software', 'ia']): 
            img_id = '1518770660439-4636190af475' # Digital
        elif any(x in combined for x in ['transp', 'moves', 'coche', 'electri']): 
            img_id = '1506521781263-d8422e82f27a' # Eléctrico
        
        return f"https://images.unsplash.com/photo-{img_id}?q=80&w=1000&auto=format&fit=crop"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; margin-bottom: 10px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR POR PALABRA CLAVE", placeholder="Ej: Industria, DANA, Energía...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        st.divider()

        # --- GRID DE BURBUJAS ---
        cols_grid = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols_grid[i % 2]:
                with st.container(border=True):
                    # 1. Foto al techo (Sin espacios)
                    st.markdown(f'<img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="header-img">', unsafe_allow_html=True)
                    
                    # 2. Contenido
                    st.markdown('<div class="content-padding">', unsafe_allow_html=True)
                    
                    # Probabilidad y Título
                    prob = str(fila.iloc[9]).strip()
                    p_class = "prob-alta" if "Alta" in prob else "prob-media"
                    st.markdown(f'<span class="badge-prob {p_class}">● {prob}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div class="tag-container">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander de Análisis
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        t1, t2 = st.tabs(["ESTRATEGIA", "REQUISITOS"])
                        with t1:
                            st.write(fila.iloc[6])
                            st.info(f"**Justificación:** {fila.iloc[7]}")
                        with t2:
                            st.write(fila.iloc[8])
                        st.link_button("🔗 VER EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)

                    # --- CAMBIO DE LAYOUT: Cuantía y Plazo en paralelo abajo ---
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown('<p class="data-label">💰 CUANTÍA ESTIMADA</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="data-value">{fila.iloc[3]}</p>', unsafe_allow_html=True)
                    with col_b:
                        st.markdown('<p class="data-label">⏳ PLAZO LÍMITE</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="data-value">{fila.iloc[4]}</p>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True) # Cierre content-padding

    st.caption("Terminal Radar v12.5 • Bunker Edition • 2025")
