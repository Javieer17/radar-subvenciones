import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v13.0",
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

    # --- DISEÑO CSS "BLUE GLOW & PERFECT ALIGN" ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Forzar fondo oscuro */
        .stApp { background-color: #0d1117 !important; }
        
        /* Estilo de la BURBUJA con EFECTO AZUL al pasar por encima */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 30px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            padding: 0px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            margin-bottom: 25px !important;
            overflow: hidden !important;
        }
        
        /* EL EFECTO QUE QUERÍAS: Brillo azul y escala */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #58a6ff !important;
            transform: translateY(-5px) scale(1.01) !important;
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.4) !important;
        }

        /* Foto del sector ajustada al techo sin bordes internos */
        .header-img {
            width: 100%;
            height: 240px;
            object-fit: cover;
            border-radius: 30px 30px 0 0;
            display: block;
            margin: 0 !important;
        }

        /* Contenido con padding uniforme */
        .content-padding {
            padding: 25px;
        }

        .sub-title {
            color: #ffffff !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 15px;
        }

        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }

        .tag {
            color: white !important;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }

        /* Datos de Cuantía y Plazo alineados */
        .data-container {
            text-align: center;
            padding: 10px;
        }
        .data-label { 
            color: #8b949e !important; 
            font-size: 11px; 
            font-weight: 700; 
            margin-bottom: 2px; 
            text-transform: uppercase; 
            letter-spacing: 1px;
        }
        .data-value { 
            color: #58a6ff !important; 
            font-size: 19px !important; 
            font-weight: 800; 
            margin: 0;
        }

        .badge-prob {
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            float: right;
        }
        .prob-alta { color: #3fb950; border: 1px solid #3fb950; background: rgba(63,185,80,0.1); }
        .prob-media { color: #d29922; border: 1px solid #d29922; background: rgba(210,153,34,0.1); }
        
        .stExpander {
            background-color: rgba(255,255,255,0.03) !important;
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

    # 4. IMÁGENES PREMIUM (Corregidas para que no fallen)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        # Lista de IDs ultra-fiables de Unsplash
        img_id = '1451187580459-43490279c0fa' # Tech por defecto
        
        if any(x in combined for x in ['dana', 'social', 'tercer sector', 'ayuda']): 
            img_id = '1488521787991-ed7bbaae773c' 
        elif any(x in combined for x in ['univ', 'docen', 'lector', 'curso', 'beca']): 
            img_id = '1523240715630-341b21391307' 
        elif any(x in combined for x in ['energ', 'foto', 'placa', 'solar']): 
            img_id = '1509391366360-2e959784a276' 
        elif any(x in combined for x in ['eolic', 'viento', 'hidro']): 
            img_id = '1466611653911-954ff21b6724' 
        elif any(x in combined for x in ['indust', 'manufact', 'fábrica']): 
            img_id = '1581091226825-a6a2a5aee158' 
        elif any(x in combined for x in ['digital', 'tic', 'software', 'ia']): 
            img_id = '1518770660439-4636190af475' 
        elif any(x in combined for x in ['transp', 'moves', 'coche']): 
            img_id = '1506521781263-d8422e82f27a' 
        
        return f"https://images.unsplash.com/photo-{img_id}?q=80&w=800&auto=format&fit=crop"

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
                    # 1. Foto (Sin huecos arriba)
                    st.markdown(f'<img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="header-img">', unsafe_allow_html=True)
                    
                    # 2. Contenido interno
                    st.markdown('<div class="content-padding">', unsafe_allow_html=True)
                    
                    # Cabecera: Probabilidad y Título
                    prob = str(fila.iloc[9]).strip()
                    p_class = "prob-alta" if "Alta" in prob else "prob-media"
                    st.markdown(f'<span class="badge-prob {p_class}">● {prob}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Etiquetas
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div class="tag-container">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        t1, t2 = st.tabs(["ESTRATEGIA", "REQUISITOS"])
                        with t1:
                            st.write(fila.iloc[6])
                            st.info(f"**Justificación:** {fila.iloc[7]}")
                        with t2:
                            st.write(fila.iloc[8])
                        st.link_button("🔗 VER EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)

                    # --- DATOS ABAJO: Centrados y en paralelo ---
                    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
                    c_a, c_b = st.columns(2)
                    with c_a:
                        st.markdown(f'''
                            <div class="data-container">
                                <p class="data-label">💰 Cuantía Estimada</p>
                                <p class="data-value">{fila.iloc[3]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    with c_b:
                        st.markdown(f'''
                            <div class="data-container">
                                <p class="data-label">⏳ Plazo Límite</p>
                                <p class="data-value">{fila.iloc[4]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True) # Cierre content-padding

    st.caption("Terminal Radar v13.0 • Blue Glow Edition • 2025")
