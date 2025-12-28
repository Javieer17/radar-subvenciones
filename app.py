import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v8.0",
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

    # --- DISEÑO CSS AVANZADO ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        .subs-card {
            background: #161b22;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid #30363d;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }
        
        .card-img {
            width: 100%;
            height: 240px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
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
        
        /* ETIQUETAS EN LÍNEA */
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        .tag {
            color: white;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sub-title {
            color: #ffffff;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 10px;
        }
        
        .data-label {
            color: #8b949e;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 2px;
            text-transform: uppercase;
        }
        .data-value {
            color: #58a6ff;
            font-size: 20px;
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

    # COLORES DE TAGS
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t or "prtr" in t: return "#1f6feb" 
        if "subvenc" in t: return "#238636" 
        if "prestamo" in t: return "#da3633" 
        if "estatal" in t: return "#8957e5" 
        return "#444c56"

    # IMÁGENES FIJAS
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        # IDs que cargan rápido y bien
        img_ids = {
            'solar': '1509391366360-2e959784a276',
            'eolic': '1466611653911-954ff21b6724',
            'indust': '1581091226825-a6a2a5aee158',
            'digital': '1518770660439-4636190af475',
            'social': '1469571486292-0ba58a3f068b',
            'dana': '1554123165-c84614e6092d',
            'educa': '1523050853173-ee040a84139b',
            'global': '1451187580459-43490279c0fa'
        }
        id_img = img_ids['global']
        if 'dana' in combined: id_img = img_ids['dana']
        elif 'lector' in combined or 'univ' in combined: id_img = img_ids['educa']
        elif 'energ' in combined or 'foto' in combined: id_img = img_ids['solar']
        elif 'eolic' in combined: id_img = img_ids['eolic']
        elif 'indust' in combined: id_img = img_ids['indust']
        elif 'digital' in combined: id_img = img_ids['digital']
        elif 'social' in combined: id_img = img_ids['social']
        
        return f"https://images.unsplash.com/photo-{id_img}?auto=format&fit=crop&w=800&q=60"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR RESULTADOS", placeholder="Ej: Industria, Energía, DANA...")

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
                
                # Construir etiquetas en una sola línea HTML
                tags = str(fila.iloc[2]).split('|')
                tags_html = "".join([f'<span class="tag" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                
                # Tarjeta Completa
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="card-img">
                    <span class="badge-prob {p_class}">{prob}</span>
                    <div class="sub-title">{fila.iloc[1]}</div>
                    <div class="tag-container">{tags_html}</div>
                    <p class="data-label">💰 Cuantía estimada</p>
                    <p class="data-value">{fila.iloc[3]}</p>
                    <p class="data-label">⏳ Plazo límite</p>
                    <p class="data-value">{fila.iloc[4]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Expander fuera del bloque HTML para que funcione
                with st.expander("🚀 ANALIZAR EXPEDIENTE IA"):
                    t1, t2 = st.tabs(["ESTRATEGIA", "REQUISITOS"])
                    with t1:
                        st.write(fila.iloc[6])
                        st.info(f"**OPORTUNIDAD:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    st.link_button("🔗 VER EN EL BOE", str(fila.iloc[0]), use_container_width=True)
                
                st.write("") # Espaciador

    st.caption("Radar Terminal v8.0 • 2025")
