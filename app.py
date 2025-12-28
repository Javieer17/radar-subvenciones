import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones v19.0",
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

    # --- DISEÑO CSS "NEON HOVER & STABLE IMAGES" ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Fondo Global */
        .stApp { background-color: #0b0e14 !important; }
        
        /* ESTILO BASE DE LA TARJETA */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 30px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            padding: 0px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s ease-in-out !important;
            margin-bottom: 30px !important;
            overflow: hidden !important;
        }
        
        /* --- EL EFECTO HOVER AZULADO Y LEVANTADO --- */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #00f2ff !important; /* Borde Cian */
            transform: translateY(-12px) scale(1.01) !important; /* Levantar */
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.25) !important; /* Resplandor */
            background-color: #1a2332 !important; /* Fondo se vuelve ligeramente azulado */
            cursor: pointer;
        }

        /* Cabecera de imagen (Fondo HTML) */
        .header-box {
            width: 100%;
            height: 240px;
            background-size: cover;
            background-position: center;
            border-radius: 30px 30px 0 0;
            margin-top: -1px;
            border-bottom: 1px solid rgba(0, 242, 255, 0.1);
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
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 6px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* Datos centrados */
        .info-pill {
            background: rgba(11, 14, 20, 0.6);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(0, 242, 255, 0.1);
            transition: 0.3s;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover .info-pill {
            border-color: #00f2ff;
            background: rgba(0, 242, 255, 0.05);
        }

        .info-label { color: #8b949e !important; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;}
        .info-value { color: #00f2ff !important; font-size: 20px !important; font-weight: 900; margin: 0; }

        /* Expander */
        .stExpander {
            background-color: transparent !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 20px !important;
            margin-bottom: 20px !important;
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

    # 4. IMÁGENES REPARADAS (Enlaces directos estables)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Enlaces directos a imágenes que NO fallan
        urls = {
            'solar': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'wind': 'https://images.unsplash.com/photo-1466611653911-954ff21b6724?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'industry': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'digital': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'agri': 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'social': 'https://images.unsplash.com/photo-1593113598332-cd288d649433?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80', # Manos unidas
            'education': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80', # Biblioteca
            'car': 'https://images.unsplash.com/photo-1617788138017-80ad40651399?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
            'tech_general': 'https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80'
        }
        
        img = urls['tech_general']
        
        if 'dana' in combined or 'social' in combined: img = urls['social']
        elif any(x in combined for x in ['univ', 'maec', 'beca', 'lector']): img = urls['education']
        elif any(x in combined for x in ['solar', 'placa']): img = urls['solar']
        elif 'eolic' in combined: img = urls['wind']
        elif any(x in combined for x in ['indust', 'fabrica']): img = urls['industry']
        elif any(x in combined for x in ['agro', 'campo']): img = urls['agri']
        elif any(x in combined for x in ['coche', 'vehicul', 'moves']): img = urls['car']
        elif any(x in combined for x in ['digit', 'tic', 'soft']): img = urls['digital']
        
        return img

    df = load_data()

    # --- UI ---
    st.markdown("<h1 style='color: #00f2ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR RESULTADOS", placeholder="Buscar por palabra clave...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container(border=True):
                    # FOTO (Header Box)
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<div class="header-box" style="background-image: url(\'{img_url}\');"></div>', unsafe_allow_html=True)
                    
                    # CONTENIDO
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Probabilidad
                    prob = str(fila.iloc[9]).strip()
                    p_color = "#3fb950" if "Alta" in prob else "#d29922"
                    st.markdown(f'<div style="float: right; color: {p_color}; font-size: 12px; font-weight: 900;">● {prob.upper()}</div>', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 20px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        st.markdown("**Resumen:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 VER BOE", str(fila.iloc[0]), use_container_width=True)
                    
                    # Datos Abajo
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

    st.caption("Radar Terminal v19.0 • Visual Repair • 2025")
