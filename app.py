import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Pro Ultra)
st.set_page_config(
    page_title="Radar Subvenciones AI v7.0",
    page_icon="🔥",
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
        st.markdown("<h1 style='text-align: center; color: white; font-family: sans-serif;'>🔒 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        st.text_input("Introduce Credencial Master", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # --- DISEÑO CSS AVANZADO (COLORES VIVOS Y LETRA GRANDE) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        /* Tarjeta con borde degradado suave */
        .subs-card {
            background: #161b22;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #30363d;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .subs-card:hover {
            border-color: #58a6ff;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.2);
            transform: scale(1.01);
        }
        
        /* Imagen de cabecera más grande */
        .card-img {
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 15px;
        }
        
        /* Probabilidad */
        .badge-prob {
            padding: 6px 15px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            float: right;
        }
        .prob-alta { color: #3fb950; border: 2px solid #3fb950; background: rgba(63,185,80,0.1); }
        .prob-media { color: #d29922; border: 2px solid #d29922; background: rgba(210,153,34,0.1); }
        
        /* Etiquetas de Ámbito (MÁS GRANDES) */
        .tag {
            display: inline-block;
            color: white;
            padding: 6px 15px;
            border-radius: 8px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        /* Título de la Subvención */
        .sub-title {
            color: #ffffff;
            font-size: 24px !important;
            font-weight: 800 !important;
            margin-top: 10px;
            line-height: 1.2;
        }
        
        /* Datos Clave (EL CAMBIO QUE PEDISTE: MÁS GRANDES) */
        .data-label {
            color: #8b949e;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 1px;
            margin-bottom: 0px;
        }
        .data-value {
            color: #58a6ff;
            font-size: 19px; /* Tamaño aumentado */
            font-weight: 800;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS
    @st.cache_data(ttl=60)
    def load_data():
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        try:
            response = requests.get(url, timeout=10)
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # 3. LÓGICA DE COLORES DE TAGS
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t or "prtr" in t: return "#1f6feb" # Azul Eléctrico
        if "subvenc" in t: return "#238636" # Verde Dinero
        if "prestamo" in t: return "#da3633" # Rojo Banco
        if "estatal" in t: return "#8957e5" # Morado
        return "#444c56" # Gris por defecto

    # 4. GALERÍA DE IMÁGENES VARIADAS
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        img_ids = {
            'solar': '1509391366360-2e959784a276',
            'eolic': '1466611653911-954ff21b6724',
            'indust': '1581091226825-a6a2a5aee158',
            'digital': '1518770660439-4636190af475',
            'agro': '1523348837708-15d4a09cfac2',
            'social': '1469571486292-0ba58a3f068b',
            'dana': '1554123165-c84614e6092d',
            'transp': '1553265027-99d530167b28',
            'vivienda': '1486408736691-c99932400491',
            'tecnol': '1485827404703-89b55fcc595e',
            'educa': '1523050853173-ee040a84139b',
            'global': '1451187580459-43490279c0fa'
        }
        
        id_img = img_ids['global']
        if 'dana' in combined: id_img = img_ids['dana']
        elif 'vivienda' in combined: id_img = img_ids['vivienda']
        elif 'lector' in combined or 'univ' in combined: id_img = img_ids['educa']
        elif 'energ' in combined or 'foto' in combined: id_img = img_ids['solar']
        elif 'eolic' in combined: id_img = img_ids['eolic']
        elif 'indust' in combined or 'manufact' in combined: id_img = img_ids['indust']
        elif 'agro' in combined: id_img = img_ids['agro']
        elif 'digital' in combined or 'tic' in combined: id_img = img_ids['digital']
        elif 'transp' in combined or 'moves' in combined: id_img = img_ids['transp']
        
        return f"https://images.unsplash.com/photo-{id_img}?auto=format&fit=crop&q=80&w=1000"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    
    c_search, c_info = st.columns([3, 1])
    with c_search:
        query = st.text_input("🔍 FILTRAR POR PALABRA CLAVE", placeholder="Ej: Industria, Energía, Digital...")
    with c_info:
        st.markdown(f"<div style='text-align:right; color:#8b949e; padding-top:25px;'>Oportunidades hoy: <b>{len(df) if df is not None else 0}</b></div>", unsafe_allow_html=True)

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
                
                # Inicia Tarjeta
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="card-img">
                    <span class="badge-prob {p_class}">{prob}</span>
                    <div class="sub-title">{fila.iloc[1]}</div>
                    <div style="margin: 15px 0;">
                """, unsafe_allow_html=True)
                
                # Tags con Colores
                tags = str(fila.iloc[2]).split('|')
                for t in tags:
                    txt = t.strip()
                    st.markdown(f'<span class="tag" style="background:{get_tag_color(txt)};">{txt}</span>', unsafe_allow_html=True)
                
                # Datos Clave (GRANDES)
                st.markdown(f"""
                    </div>
                    <p class="data-label">💰 CUANTÍA TOTAL ESTIMADA</p>
                    <p class="data-value">{fila.iloc[3]}</p>
                    <p class="data-label">⏳ PLAZO DE PRESENTACIÓN</p>
                    <p class="data-value">{fila.iloc[4]}</p>
                """, unsafe_allow_html=True)
                
                # Expander
                with st.expander("🚀 ANALIZAR EXPEDIENTE"):
                    t1, t2 = st.tabs(["REPORTE IA", "REQUISITOS"])
                    with t1:
                        st.markdown("**Resumen:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    st.link_button("🔗 VER EN BOE OFICIAL", str(fila.iloc[0]), use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Terminal de Inteligencia v7.0 Edition • Secure Data • 2025")
