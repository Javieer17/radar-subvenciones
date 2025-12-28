import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v10.0",
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

    # --- DISEÑO CSS "PERFECT FIT" (MÁXIMA VARIEDAD Y AJUSTE) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        /* Contenedor de la Burbuja */
        .subs-card {
            background: #161b22;
            border-radius: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            overflow: hidden; /* Esto hace que la foto se corte con la forma de la burbuja */
        }
        
        .subs-card:hover {
            transform: translateY(-10px) scale(1.01);
            border-color: #58a6ff;
            box-shadow: 0 20px 40px rgba(88, 166, 255, 0.2);
        }
        
        /* Foto de Cabecera Ajustada al 100% */
        .card-img {
            width: 100%;
            height: 230px;
            object-fit: cover;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Contenido interno con padding */
        .card-content {
            padding: 25px;
        }
        
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        
        .tag {
            color: white;
            padding: 5px 12px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }
        
        .sub-title {
            color: #ffffff;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            min-height: 55px;
        }
        
        .data-value {
            color: #58a6ff;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 10px;
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

    # 4. GALERÍA DE IMÁGENES ULTRA-VARIADA (20 CATEGORÍAS)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Diccionario de IDs de alta resolución (Unsplash)
        images = {
            'solar': '1509391366360-2e959784a276',
            'eolica': '1466611653911-954ff21b6724',
            'hidro': '1516937941524-747f48d6db12',
            'hidrogeno': '1621533611164-72af051f1343',
            'industria': '1581091226825-a6a2a5aee158',
            'manufactura': '1504917595217-d4dc5dba6ac6',
            'digital': '1518770660439-4636190af475',
            'ia_software': '1550751827-4bd374c3f58b',
            'agro_campo': '1523348837708-15d4a09cfac2',
            'social_comunidad': '1469571486292-0ba58a3f068b',
            'dana_emergencia': '1554123165-c84614e6092d',
            'transporte_ev': '1506521781263-d8422e82f27a',
            'logistica': '1586528116311-c39eb6a4db41',
            'educacion': '1523050853173-ee040a84139b',
            'investigacion': '1532094349884-543bb118196d',
            'vivienda_urb': '1486408736691-c99932400491',
            'turismo_hotel': '1469854523086-cc02fe5d8800',
            'salud_medica': '1505751172107-596229738e60',
            'cultura_arte': '1460667380274-eb7ef7a04790',
            'pesca_mar': '1498654203945-36283ca78f0d',
            'global_tech': '1451187580459-43490279c0fa'
        }
        
        # Lógica de selección
        img_id = images['global_tech']
        if 'dana' in combined: img_id = images['dana_emergencia']
        elif 'hidrogen' in combined: img_id = images['hidrogeno']
        elif any(x in combined for x in ['lector', 'univ', 'docen', 'escuela']): img_id = images['educacion']
        elif any(x in combined for x in ['energ', 'foto', 'placa']): img_id = images['solar']
        elif 'eolic' in combined: img_id = images['eolica']
        elif 'hidro' in combined: img_id = images['hidro']
        elif any(x in combined for x in ['indust', 'manufact', 'cvi']): img_id = images['industria']
        elif any(x in combined for x in ['agro', 'campo', 'forest', 'agri']): img_id = images['agro_campo']
        elif any(x in combined for x in ['digital', 'tic', 'softw', 'ia']): img_id = images['ia_software']
        elif any(x in combined for x in ['social', 'infan', 'tercer sector']): img_id = images['social_comunidad']
        elif any(x in combined for x in ['transp', 'moves', 'vehic', 'electri']): img_id = images['transporte_ev']
        elif any(x in combined for x in ['logist', 'camion', 'almacen']): img_id = images['logistica']
        elif any(x in combined for x in ['investiga', 'ciencia', 'tecnol']): img_id = images['investigacion']
        elif any(x in combined for x in ['edific', 'vivienda', 'rehabilit']): img_id = images['vivienda_urb']
        elif any(x in combined for x in ['turism', 'hotel', 'viaje']): img_id = images['turismo_hotel']
        elif any(x in combined for x in ['salud', 'medic', 'hospi']): img_id = images['salud_medica']
        elif any(x in combined for x in ['cultur', 'arte', 'museo']): img_id = images['cultura_arte']
        elif any(x in combined for x in ['pesca', 'mar', 'barco']): img_id = images['pesca_mar']
        
        # Retornamos la URL con parámetros de optimización para que cargue rápido
        return f"https://images.unsplash.com/photo-{img_id}?auto=format&fit=crop&w=800&q=80"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
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
                
                # Etiquetas
                tags = str(fila.iloc[2]).split('|')
                tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                
                # RENDERIZADO DE LA BURBUJA PERFECTA
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="card-img">
                    <div class="card-content">
                        <span class="badge-prob {p_class}">● {prob}</span>
                        <div class="sub-title">{fila.iloc[1]}</div>
                        <div class="tag-container">{tags_html}</div>
                        <p style="color: #8b949e; font-size: 13px; font-weight: 700; margin-bottom: 0;">💰 CUANTÍA ESTIMADA</p>
                        <p class="data-value">{fila.iloc[3]}</p>
                        <p style="color: #8b949e; font-size: 13px; font-weight: 700; margin-bottom: 0;">⏳ PLAZO LÍMITE</p>
                        <p class="data-value">{fila.iloc[4]}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expander separado para que funcione el botón
                with st.expander("🚀 ANALIZAR EXPEDIENTE COMPLETO"):
                    t1, t2 = st.tabs(["💡 Estrategia", "⚖️ Requisitos"])
                    with t1:
                        st.markdown("**Resumen IA:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Oportunidad:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    st.link_button("🔗 ABRIR EN EL BOE", str(fila.iloc[0]), use_container_width=True)
                
                st.write("") 

    st.caption("Radar Terminal v10.0 • Master Vision • 2025")
