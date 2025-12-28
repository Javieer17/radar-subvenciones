import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Pro)
st.set_page_config(
    page_title="Radar Subvenciones Master v17.0",
    page_icon="⚡",
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
        st.markdown("<h1 style='text-align: center; color: white;'>🔑 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        st.text_input("Introduce Credencial Master", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # --- DISEÑO CSS "NEO-BUNKER" (GLOW & LIFT) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Fondo Global del Búnker */
        .stApp { background-color: #0b0e14 !important; }
        
        /* LA BURBUJA: El efecto neón al pasar el cursor */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 35px !important;
            border: 1px solid rgba(88, 166, 255, 0.1) !important;
            padding: 0px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            margin-bottom: 25px !important;
            overflow: hidden !important;
        }
        
        /* EL EFECTO NEÓN AZUL QUE PEDÍAS */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #00f2ff !important;
            transform: translateY(-12px) scale(1.02) !important;
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.35) !important;
            z-index: 100;
        }

        /* Cabecera de imagen integrada */
        .header-box {
            width: 100%;
            height: 250px;
            background-size: cover;
            background-position: center;
            border-radius: 35px 35px 0 0;
            margin-top: -1px;
            border-bottom: 1px solid rgba(88, 166, 255, 0.2);
        }

        .card-body {
            padding: 25px;
            color: white;
        }

        .sub-title {
            color: #ffffff !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 15px;
            letter-spacing: -0.5px;
        }

        .tag-pill {
            display: inline-block;
            color: white !important;
            padding: 5px 14px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 6px;
            margin-bottom: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        /* Cápsulas de información */
        .info-pill {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 20px;
            padding: 18px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: 0.3s;
        }
        .info-pill:hover {
            background: rgba(0, 242, 255, 0.05);
            border-color: rgba(0, 242, 255, 0.2);
        }
        .info-label { color: #8b949e !important; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;}
        .info-value { color: #00f2ff !important; font-size: 20px !important; font-weight: 900; margin: 0; }

        /* Expander Estilo Premium */
        .stExpander {
            background-color: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 20px !important;
            margin-bottom: 15px !important;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS
    @st.cache_data(ttl=60)
    def load_data():
        try:
            sid = st.secrets["sheet_id"]
            url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
            response = requests.get(url, timeout=15)
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # 3. COLORES DE TAGS
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t: return "#1f6feb" 
        if "subvenc" in t: return "#238636" 
        if "prestamo" in t: return "#da3633" 
        if "estatal" in t: return "#8957e5"
        return "#444c56"

    # 4. FOTOS NUEVAS Y BLINDADAS (IDs de Alta Disponibilidad)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Diccionario con fotos de alta fiabilidad
        ids = {
            'dana': '1593113501539-d91f43f130ac', # Comunidad / Voluntarios
            'univ': '1456518563333-7d13c6179a62', # Educación / Libros
            'solar': '1509391366360-2e959784a276', # Solar
            'eolic': '1466611653911-954ff21b6724', # Viento
            'indus': '1581091226825-a6a2a5aee158', # Industria
            'digital': '1518770660439-4636190af475', # IA
            'global': '1451187580459-43490279c0fa' # Tech General
        }
        
        img = ids['global']
        if 'dana' in combined or 'tercer sector' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'maec', 'curso', 'beca', 'lector']): img = ids['univ']
        elif any(x in combined for x in ['energ', 'foto', 'placa', 'solar']): img = ids['solar']
        elif 'eolic' in combined: img = ids['eolic']
        elif any(x in combined for x in ['indust', 'fabrica', 'manufactura']): img = ids['indus']
        elif any(x in combined for x in ['digital', 'tic', 'software']): img = ids['digital']
        
        return f"https://images.unsplash.com/photo-{img}?q=80&w=1000&auto=format&fit=crop"

    df = load_data()

    # --- UI PRINCIPAL ---
    st.markdown("<h1 style='color: #00f2ff; font-weight: 900; letter-spacing: -1.5px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR SUBSISTEMA", placeholder="Palabra clave...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        # --- GRID DE BURBUJAS NEÓN ---
        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container(border=True):
                    # Foto Blindada inyectada como fondo (Sin fallos)
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<div class="header-box" style="background-image: url(\'{img_url}\');"></div>', unsafe_allow_html=True)
                    
                    # Cuerpo de la tarjeta
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Probabilidad
                    prob = str(fila.iloc[9]).strip()
                    p_color = "#3fb950" if "Alta" in prob else "#d29922"
                    st.markdown(f'<div style="float: right; color: {p_color}; font-size: 12px; font-weight: 900; letter-spacing: 1px;">● {prob.upper()}</div>', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 25px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander Integrado
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        st.markdown("**Reporte de IA:**")
                        st.write(fila.iloc[6])
                        st.info(f"Oportunidad: {fila.iloc[7]}")
                        st.markdown("**Requisitos Técnicos:**")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 VER EXPEDIENTE OFICIAL", str(fila.iloc[0]), use_container_width=True)
                    
                    # --- DATOS ABAJO: Centrados y alineados ---
                    st.write("")
                    c_1, c_2 = st.columns(2)
                    with c_1:
                        st.markdown(f'''
                            <div class="info-pill">
                                <p class="info-label">💰 Cuantía</p>
                                <p class="info-value">{fila.iloc[3]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    with c_2:
                        st.markdown(f'''
                            <div class="info-pill">
                                <p class="info-label">⏳ Plazo</p>
                                <p class="info-value">{fila.iloc[4]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Radar Terminal v17.0 | Master Neo-Bunker Edition | 2025")
