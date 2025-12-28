import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v14.0",
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

    # --- DISEÑO CSS "BUNKER TOTAL" (ESTO ARREGLA LA BURBUJA) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Fondo General */
        .stApp { background-color: #0d1117 !important; }
        
        /* ESTA ES LA BURBUJA - Selector universal para cajas con borde */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 25px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 0px !important; /* IMPORTANTE: 0 para que la foto pegue arriba */
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s ease-in-out !important;
            margin-bottom: 20px !important;
            overflow: hidden !important;
        }
        
        /* EFECTO AZUL AL PASAR EL RATÓN */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #58a6ff !important;
            transform: translateY(-5px) !important;
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.3) !important;
        }

        /* Foto del sector (Ajuste al milímetro) */
        .header-img {
            width: 100%;
            height: 230px;
            object-fit: cover;
            border-radius: 25px 25px 0 0;
            display: block;
            margin: 0 !important;
        }

        /* Contenido de texto con padding */
        .card-body {
            padding: 25px;
        }

        .sub-title {
            color: #ffffff !important;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 12px;
        }

        .tag {
            display: inline-block;
            color: white !important;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 5px;
            margin-bottom: 5px;
        }

        /* Cuantía y Plazo alineados */
        .data-box {
            text-align: center;
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            padding: 10px;
        }
        .data-label { color: #8b949e !important; font-size: 11px; font-weight: 700; margin-bottom: 2px; }
        .data-value { color: #58a6ff !important; font-size: 18px !important; font-weight: 800; margin: 0; }

        /* Expander de Streamlit */
        .stExpander {
            background-color: transparent !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 15px !important;
        }
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
        return "#444c56"

    # 4. IMÁGENES (Con sistema de recuperación por si fallan)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Diccionario de fotos estables
        ids = {
            'dana': '1593113501539-d91f43f130ac',
            'univ': '1523240715630-341b21391307',
            'tech': '1451187580459-43490279c0fa',
            'solar': '1509391366360-2e959784a276',
            'indus': '1581091226825-a6a2a5aee158'
        }
        
        img = ids['tech'] # Por defecto
        if 'dana' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'lector', 'beca', 'curso']): img = ids['univ']
        elif any(x in combined for x in ['solar', 'placa', 'energ']): img = ids['solar']
        elif any(x in combined for x in ['indus', 'fabrica']): img = ids['indus']
        
        return f"https://images.unsplash.com/photo-{img}?q=80&w=800&auto=format&fit=crop"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900;'>📡 Radar Inteligente</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 Filtrar...", placeholder="Ej: Industria, Energía...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                # LA BURBUJA (st.container con border=True)
                with st.container(border=True):
                    # Foto
                    st.markdown(f'<img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="header-img">', unsafe_allow_html=True)
                    
                    # Cuerpo de la tarjeta
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div>{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        t1, t2 = st.tabs(["Estrategia", "Requisitos"])
                        with t1:
                            st.write(fila.iloc[6])
                            st.info(f"Oportunidad: {fila.iloc[7]}")
                        with t2:
                            st.write(fila.iloc[8])
                        st.link_button("🔗 VER BOE", str(fila.iloc[0]), use_container_width=True)
                    
                    # Métricas finales centradas
                    st.write("")
                    c_1, c_2 = st.columns(2)
                    with c_1:
                        st.markdown(f'<div class="data-box"><p class="data-label">💰 CUANTÍA</p><p class="data-value">{fila.iloc[3]}</p></div>', unsafe_allow_html=True)
                    with c_2:
                        st.markdown(f'<div class="data-box"><p class="data-label">⏳ PLAZO</p><p class="data-value">{fila.iloc[4]}</p></div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Terminal Radar v14.0 • 2025")
