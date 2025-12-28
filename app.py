import streamlit as st
import pandas as pd
import requests
import io

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DEL NÚCLEO (ENGINE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Radar Subvenciones AI | NOVA",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. SISTEMA DE SEGURIDAD
# ---------------------------------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
            <style>
            .stApp { background-color: #000000; }
            h1 { color: #00f2ff; text-align: center; font-family: sans-serif; }
            </style>
            <br><br><br>
            <h1>🔐 ACCESO BIOMÉTRICO</h1>
            """, unsafe_allow_html=True)
        st.text_input("CLAVE DE ACCESO", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # ---------------------------------------------------------
    # 3. ESTILOS CSS "NOVA ENGINE" (NUEVO DISEÑO)
    # ---------------------------------------------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
        
        /* --- FONDO GLOBAL --- */
        .stApp {
            background-color: #050505 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        /* --- ARREGLO DE TEXTOS --- */
        p, li, span, div {
            color: #e0e0e0 !important;
        }
        h1, h2, h3 { color: white !important; }

        /* --- LA TARJETA (CONTENEDOR) --- */
        /* Buscamos el contenedor de borde de Streamlit y lo tuneamos */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #11141a !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 24px !important;
            padding: 0px !important; /* CRUCIAL: Sin padding para que la foto toque los bordes */
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            overflow: hidden !important;
        }

        /* --- EFECTO HOVER (EL QUE TE GUSTA) --- */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-8px) scale(1.01) !important;
            border-color: #00f2ff !important; /* CIAN NEÓN */
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.15) !important;
            z-index: 10;
        }

        /* --- HACK PARA LA FOTO FULL WIDTH --- */
        /* Esto hace que la imagen ignore los márgenes de Streamlit */
        .full-width-img {
            width: calc(100% + 2rem);
            margin-left: -1rem;
            margin-top: -1rem;
            margin-right: -1rem;
            height: 240px;
            object-fit: cover;
            border-bottom: 2px solid #00f2ff;
            mask-image: linear-gradient(to bottom, black 80%, transparent 100%);
        }

        /* --- TIPOGRAFÍA Y ETIQUETAS --- */
        .card-title {
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            color: #ffffff !important;
            margin-top: 15px;
            margin-bottom: 15px;
        }

        .tag {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-right: 5px;
            margin-bottom: 5px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* --- METRICAS (PRECIO Y PLAZO) --- */
        .metric-box {
            background: rgba(0, 242, 255, 0.05);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            border: 1px solid rgba(0, 242, 255, 0.1);
            margin-top: 10px;
        }
        .metric-label { font-size: 10px; text-transform: uppercase; color: #888; font-weight: 700; }
        .metric-value { font-size: 18px; color: #00f2ff !important; font-weight: 900; }

        /* --- BOTONES Y EXPANDER --- */
        .stExpander {
            border: none !important;
            background: transparent !important;
        }
        button {
            border-radius: 8px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. LÓGICA DE DATOS E IMÁGENES (CURADAS MANUALMENTE)
    # ---------------------------------------------------------
    @st.cache_data(ttl=60)
    def load_data():
        try:
            sid = st.secrets["sheet_id"]
            url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
            response = requests.get(url, timeout=10)
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # DICCIONARIO DE IMÁGENES QUE FUNCIONAN (ENLACES DIRECTOS)
    def get_img(texto_sector, titulo):
        s = (str(texto_sector) + " " + str(titulo)).lower()
        
        # Enlaces directos a fotos específicas de Unsplash que encajan perfecto
        urls = {
            'dana': 'https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=800&q=80', # Manos unidas
            'univ': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80', # Universidad Auditorio
            'tech': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80', # Chip IA
            'solar': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80', # Panel Solar
            'indus': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80', # Fábrica
            'agri': 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=800&q=80', # Tractor moderno
            'default': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80' # Mundo conectado
        }
        
        if 'dana' in s or 'tercer sector' in s: return urls['dana']
        if any(x in s for x in ['univ', 'maec', 'lector', 'beca']): return urls['univ']
        if any(x in s for x in ['solar', 'placa', 'energ']): return urls['solar']
        if any(x in s for x in ['indus', 'manuf', 'fabrica']): return urls['indus']
        if any(x in s for x in ['agro', 'campo']): return urls['agri']
        if any(x in s for x in ['digit', 'tic', 'soft']): return urls['tech']
        
        return urls['default']

    def get_tag_style(tag):
        t = tag.lower()
        bg = "#333"
        if "next" in t: bg = "#0d47a1" # Azul oscuro
        elif "subvenc" in t: bg = "#1b5e20" # Verde oscuro
        elif "préstamo" in t: bg = "#b71c1c" # Rojo oscuro
        return f'background-color: {bg};'

    # ---------------------------------------------------------
    # 5. INTERFAZ VISUAL (UI)
    # ---------------------------------------------------------
    
    # Header
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<h1 style='text-align: left; margin-bottom: 0px;'>📡 RADAR DE INTELIGENCIA</h1>", unsafe_allow_html=True)
        st.caption("ANALÍTICA ESTRATÉGICA EN TIEMPO REAL")
    with col2:
        search = st.text_input("🔍 FILTRAR", placeholder="Ej: DANA, Digital...")

    df = load_data()

    if df is not None:
        if search:
            df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        # GRID DE TARJETAS
        columnas = st.columns(2) # 2 columnas para que sean grandes
        
        for i, row in df.iterrows():
            if pd.isna(row.iloc[1]): continue
            
            # Usamos el contenedor de Streamlit (que hemos tuneado con CSS arriba)
            with columnas[i % 2]:
                with st.container(border=True):
                    
                    # 1. IMAGEN (Hack CSS para que ocupe todo el ancho)
                    img_src = get_img(row.iloc[5], row.iloc[1])
                    st.markdown(f'<img src="{img_src}" class="full-width-img">', unsafe_allow_html=True)
                    
                    # 2. CONTENIDO (Padding interno)
                    # Probabilidad
                    prob = str(row.iloc[9]).strip()
                    color_prob = "#00f2ff" if "Alta" in prob else "#ffcc00"
                    
                    st.markdown(f"""
                        <div style="padding: 10px 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 10px; color: #888; font-weight: bold;">SECTOR: {str(row.iloc[5]).upper()}</span>
                                <span style="color: {color_prob}; border: 1px solid {color_prob}; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 900;">{prob}</span>
                            </div>
                            <div class="card-title">{row.iloc[1]}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Tags
                    tags = str(row.iloc[2]).split('|')
                    tags_html = ""
                    for t in tags:
                        tags_html += f'<span class="tag" style="{get_tag_style(t)}">{t.strip()}</span>'
                    st.markdown(f'<div style="padding: 0 15px;">{tags_html}</div>', unsafe_allow_html=True)

                    # Metricas
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="metric-box"><div class="metric-label">CUANTÍA</div><div class="metric-value">{row.iloc[3]}</div></div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="metric-box"><div class="metric-label">PLAZO</div><div class="metric-value">{row.iloc[4]}</div></div>', unsafe_allow_html=True)
                    
                    st.write("") # Espaciador
                    
                    # Botonera
                    with st.expander("🚀 ESTRATEGIA Y REQUISITOS"):
                        st.markdown("#### 🧠 Análisis IA")
                        st.write(row.iloc[6])
                        st.info(f"💡 **Oportunidad:** {row.iloc[7]}")
                        st.markdown("#### 📋 Requisitos")
                        st.write(row.iloc[8])
                        st.link_button("🔗 ENLACE AL BOE", str(row.iloc[0]), use_container_width=True)
                    
                    st.write("") # Padding final

    else:
        st.error("Error de conexión con la Base de Datos.")

    st.markdown("<br><br><center style='color: #444;'>NOVA SYSTEM v1.0 | 2025</center>", unsafe_allow_html=True)
