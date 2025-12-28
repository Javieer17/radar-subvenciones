import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v9.0",
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

    # --- DISEÑO CSS "CYBER-BUNKER" (EFECTO BURBUJA & NEÓN) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
        
        .main { background-color: #0d1117; font-family: 'Outfit', sans-serif; }
        
        /* La Tarjeta (Burbuja principal) */
        .subs-card {
            background: #161b22;
            border-radius: 25px;
            padding: 28px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            overflow: hidden;
        }
        
        /* EFECTO HOVER (El que te gustaba) */
        .subs-card:hover {
            transform: scale(1.02);
            border-color: #58a6ff;
            box-shadow: 0 0 30px rgba(88, 166, 255, 0.25);
        }
        
        /* La Foto dentro de la burbuja */
        .card-img {
            width: 100%;
            height: 250px;
            object-fit: cover; /* Hace que la foto encaje perfecta */
            border-radius: 18px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Etiquetas en Línea (Flexbox) */
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tag {
            color: white;
            padding: 6px 14px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        
        .sub-title {
            color: #ffffff;
            font-size: 24px !important;
            font-weight: 800 !important;
            line-height: 1.2;
            margin-bottom: 12px;
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
            font-size: 21px;
            font-weight: 800;
            margin-bottom: 18px;
        }
        
        /* Probabilidad arriba a la derecha */
        .badge-prob {
            padding: 6px 15px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 900;
            text-transform: uppercase;
            float: right;
        }
        .prob-alta { color: #3fb950; border: 2px solid #3fb950; background: rgba(63,185,80,0.15); }
        .prob-media { color: #d29922; border: 2px solid #d29922; background: rgba(210,153,34,0.15); }
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
        if "next" in t or "prtr" in t: return "#1f6feb" 
        if "subvenc" in t: return "#238636" 
        if "prestamo" in t: return "#da3633" 
        if "estatal" in t: return "#8957e5" 
        return "#444c56"

    # 4. GALERÍA DE IMÁGENES PREMIUM (IDs verificados)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        # Diccionario con 12 categorías reales de subvenciones
        img_ids = {
            'solar': '1509391366360-2e959784a276',      # Paneles solares
            'eolic': '1466611653911-954ff21b6724',      # Molinos
            'indust': '1581091226825-a6a2a5aee158',     # Fábrica moderna
            'digital': '1518770660439-4636190af475',    # Código / IA
            'agro': '1523348837708-15d4a09cfac2',       # Campo / Tractor
            'social': '1469571486292-0ba58a3f068b',     # Ayuda social / Infancia
            'dana': '1554123165-c84614e6092d',          # Reconstrucción / Comunidad
            'transp': '1506521781263-d8422e82f27a',     # Coche eléctrico / Moves
            'educa': '1523050853173-ee040a84139b',      # Universidad / Lectorados
            'vivienda': '1486408736691-c99932400491',   # Edificios / Construcción
            'hidro': '1516937941524-747f48d6db12',      # Agua / Central hidroeléctrica
            'startup': '1522202176988-66273c2fd55f',    # Emprendimiento / Startup
            'global': '1451187580459-43490279c0fa'      # Tecnología global
        }
        
        # Selección inteligente de la foto
        id_img = img_ids['global']
        if 'dana' in combined: id_img = img_ids['dana']
        elif any(x in combined for x in ['lector', 'univ', 'docen', 'escuela']): id_img = img_ids['educa']
        elif any(x in combined for x in ['energ', 'foto', 'placas']): id_img = img_ids['solar']
        elif 'eolic' in combined: id_img = img_ids['eolic']
        elif any(x in combined for x in ['indust', 'manufact', 'cvi', 'descarboni']): id_img = img_ids['indust']
        elif any(x in combined for x in ['agro', 'campo', 'forest', 'agri']): id_img = img_ids['agro']
        elif any(x in combined for x in ['digital', 'tic', 'softw', 'ia']): id_img = img_ids['digital']
        elif any(x in combined for x in ['social', 'infan', 'tercer sector', 'dana']): id_img = img_ids['social']
        elif any(x in combined for x in ['transp', 'moves', 'vehic', 'electri']): id_img = img_ids['transp']
        elif 'hidro' in combined: id_img = img_ids['hidro']
        elif any(x in combined for x in ['emprend', 'startup', 'pyme']): id_img = img_ids['startup']
        elif any(x in combined for x in ['edific', 'vivienda', 'rehabilit']): id_img = img_ids['vivienda']
        
        return f"https://images.unsplash.com/photo-{id_img}?auto=format&fit=crop&w=1000&q=80"

    df = load_data()

    # --- HEADER ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar de Inteligencia Estratégica</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR POR PALABRA CLAVE", placeholder="Busca industria, digital, energía...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        st.divider()

        # --- GRID DE TARJETAS (Burbujas Neón) ---
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
                
                # Renderizamos la Tarjeta (Burbuja)
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5], fila.iloc[1])}" class="card-img">
                    <span class="badge-prob {p_class}">● {prob}</span>
                    <div class="sub-title">{fila.iloc[1]}</div>
                    <div class="tag-container">{tags_html}</div>
                    <p class="data-label">💰 Cuantía estimada</p>
                    <p class="data-value">{fila.iloc[3]}</p>
                    <p class="data-label">⏳ Plazo de presentación</p>
                    <p class="data-value">{fila.iloc[4]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Desplegable fuera del HTML
                with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                    t1, t2 = st.tabs(["💡 Estrategia", "⚖️ Requisitos"])
                    with t1:
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    st.link_button("🔗 ABRIR EXPEDIENTE BOE", str(fila.iloc[0]), use_container_width=True)
                
                st.write("") 

    st.caption("Radar Terminal v9.0 • Premium Intelligence • 2025")
