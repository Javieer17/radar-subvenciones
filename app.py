import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v15.0",
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

    # --- DISEÑO CSS "EL BÚNKER DEFINITIVO" ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* Fondo General */
        .stApp { background-color: #0d1117 !important; }
        
        /* LA BURBUJA: Forzamos el diseño en todos los contenedores con borde */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22 !important;
            border-radius: 25px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 0px !important; /* Cero margen interno para la foto */
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s ease-in-out !important;
            margin-bottom: 25px !important;
        }
        
        /* EFECTO AZUL NEÓN AL PASAR EL RATÓN */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #58a6ff !important;
            box-shadow: 0 0 30px rgba(88, 166, 255, 0.4) !important;
            transform: translateY(-5px) !important;
        }

        /* Cabecera de imagen (HTML Puro para que no falle) */
        .header-box {
            width: 100%;
            height: 220px;
            background-size: cover;
            background-position: center;
            border-radius: 25px 25px 0 0;
            margin-top: -1px; /* Ajuste para que no se vea línea blanca */
        }

        /* Contenedor de texto con el padding real */
        .card-body {
            padding: 25px;
            color: white;
        }

        .sub-title {
            color: #ffffff !important;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 12px;
        }

        .tag-pill {
            display: inline-block;
            color: white !important;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 6px;
            margin-bottom: 8px;
        }

        /* Cuantía y Plazo alineados en cajas modernas */
        .info-pill {
            background: rgba(255,255,255,0.04);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .info-label { color: #8b949e !important; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
        .info-value { color: #58a6ff !important; font-size: 18px !important; font-weight: 900; margin: 0; }

        /* Estilo del Expander */
        .stExpander {
            background-color: rgba(255,255,255,0.02) !important;
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

    # 4. IMÁGENES (IDs Blindados)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Diccionario de fotos que cargan sí o sí
        ids = {
            'dana': '1554123165-c84614e6092d',
            'univ': '1541339905120-f579ae5af072',
            'tech': '1451187580459-43490279c0fa',
            'solar': '1509391366360-2e959784a276',
            'indus': '1581091226825-a6a2a5aee158',
            'digital': '1518770660439-4636190af475'
        }
        
        img = ids['tech']
        if 'dana' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'lector', 'beca', 'curso', 'maec']): img = ids['univ']
        elif any(x in combined for x in ['solar', 'placa', 'energ']): img = ids['solar']
        elif any(x in combined for x in ['indus', 'fabrica']): img = ids['indus']
        elif any(x in combined for x in ['digital', 'tic', 'software']): img = ids['digital']
        
        return f"https://images.unsplash.com/photo-{img}?q=80&w=800&auto=format&fit=crop"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 Filtrar subvenciones...", placeholder="Ej: Industria, DANA, Energía...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                # LA BURBUJA REAL
                with st.container(border=True):
                    # Foto inyectada como fondo HTML (sin márgenes)
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<div class="header-box" style="background-image: url(\'{img_url}\');"></div>', unsafe_allow_html=True)
                    
                    # Cuerpo de la tarjeta
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Probabilidad
                    prob = str(fila.iloc[9]).strip()
                    p_color = "#3fb950" if "Alta" in prob else "#d29922"
                    st.markdown(f'<div style="float: right; color: {p_color}; font-size: 11px; font-weight: 900;">● {prob.upper()}</div>', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 20px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander Integrado
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        t1, t2 = st.tabs(["Estrategia", "Requisitos"])
                        with t1:
                            st.write(fila.iloc[6])
                            st.info(f"Oportunidad: {fila.iloc[7]}")
                        with t2:
                            st.write(fila.iloc[8])
                        st.link_button("🔗 VER EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)
                    
                    # Datos Económicos (Alineados Horizontalmente)
                    st.write("")
                    c_1, c_2 = st.columns(2)
                    with c_1:
                        st.markdown(f'''
                            <div class="info-pill">
                                <p class="info-label">💰 CUANTÍA</p>
                                <p class="info-value">{fila.iloc[3]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    with c_2:
                        st.markdown(f'''
                            <div class="info-pill">
                                <p class="info-label">⏳ PLAZO</p>
                                <p class="info-value">{fila.iloc[4]}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Radar Terminal v15.0 • 2025")
