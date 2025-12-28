import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v11.0",
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
        st.markdown("<h1 style='text-align: center; color: white;'>🔒 ACCESO PRIVADO</h1>", unsafe_allow_html=True)
        st.text_input("Introduce Credencial Master", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # --- DISEÑO CSS "FORCE DARK" & INTEGRACIÓN TOTAL ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        /* FORZAR MODO OSCURO GLOBAL */
        .stApp {
            background-color: #0d1117 !important;
            color: #ffffff !important;
        }
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        /* Contenedor de la Burbuja */
        .subs-card {
            background: #161b22;
            border-radius: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            transition: all 0.4s ease;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .subs-card:hover {
            border-color: #58a6ff;
            box-shadow: 0 10px 40px rgba(88, 166, 255, 0.15);
        }
        
        /* Foto Ajustada */
        .card-img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .card-content {
            padding: 20px 25px;
        }
        
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        
        .tag {
            color: white !important;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }
        
        .sub-title {
            color: #ffffff !important;
            font-size: 20px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-top: 10px;
        }
        
        .data-value {
            color: #58a6ff !important;
            font-size: 19px !important;
            font-weight: 800;
        }
        
        .data-label {
            color: #8b949e !important;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: -5px;
        }

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
        
        /* Ajuste para los Expanders dentro de la burbuja */
        .stExpander {
            background-color: transparent !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 15px !important;
            margin-top: 10px !important;
        }
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

    # 4. GALERÍA DE IMÁGENES (IDs Limpios)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        images = {
            'solar': '1509391366360-2e959784a276',
            'eolica': '1466611653911-954ff21b6724',
            'hidro': '1516937941524-747f48d6db12',
            'industria': '1581091226825-a6a2a5aee158',
            'digital': '1518770660439-4636190af475',
            'social': '1469571486292-0ba58a3f068b',
            'dana': '1554123165-c84614e6092d',
            'transporte': '1506521781263-d8422e82f27a',
            'educacion': '1523050853173-ee040a84139b',
            'vivienda': '1486408736691-c99932400491',
            'global': '1451187580459-43490279c0fa'
        }
        
        img_id = images['global']
        if 'dana' in combined: img_id = images['dana']
        elif any(x in combined for x in ['univ', 'docen', 'lector']): img_id = images['educacion']
        elif any(x in combined for x in ['energ', 'foto', 'placa']): img_id = images['solar']
        elif any(x in combined for x in ['indust', 'manufact']): img_id = images['industria']
        elif any(x in combined for x in ['digital', 'tic', 'softw']): img_id = images['digital']
        elif any(x in combined for x in ['social', 'infan', 'tercer']): img_id = images['social']
        elif any(x in combined for x in ['transp', 'moves', 'vehic']): img_id = images['transporte']
        elif any(x in combined for x in ['edific', 'vivienda']): img_id = images['vivienda']
        
        return f"https://images.unsplash.com/photo-{img_id}?auto=format&fit=crop&w=800&q=80"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; margin-bottom:0;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR POR PALABRA CLAVE", placeholder="Buscar por sector, CCAA, tipo...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        st.divider()

        # --- GRID DE TARJETAS ---
        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                prob = str(fila.iloc[9]).strip()
                p_class = "prob-alta" if "Alta" in prob else "prob-media"
                
                # Preparamos las etiquetas
                tags = str(fila.iloc[2]).split('|')
                tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                
                # INICIO DE LA BURBUJA
                with st.container():
                    # Parte superior: Imagen + Título + Tags
                    st.markdown(f"""
                    <div class="subs-card">
                        <img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="card-img">
                        <div class="card-content">
                            <span class="badge-prob {p_class}">● {prob}</span>
                            <div class="sub-title">{fila.iloc[1]}</div>
                            <div class="tag-container">{tags_html}</div>
                    """, unsafe_allow_html=True)
                    
                    # EL EXPANDER (AHORA INTEGRADO DENTRO)
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        st.markdown("**Resumen IA:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.markdown("**Requisitos:**")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)
                    
                    # Parte inferior: Datos de cuantía y plazo
                    st.markdown(f"""
                            <div style="margin-top:15px;">
                                <p class="data-label">💰 CUANTÍA ESTIMADA</p>
                                <p class="data-value">{fila.iloc[3]}</p>
                                <p class="data-label">⏳ PLAZO LÍMITE</p>
                                <p class="data-value">{fila.iloc[4]}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("") # Espaciador

    st.caption("Radar Terminal v11.0 • Ultimate Vision • 2025")
