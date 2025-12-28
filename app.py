import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v25.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS NUCLEAR (FORZADO GLOBAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
    
    /* 1. FORZADO ABSOLUTO DE MODO OSCURO */
    .stApp {
        background-color: #0e1117 !important; /* El fondo oscuro que te gusta */
        color: #ffffff !important;
    }
    
    /* Forzar textos a blanco/gris claro siempre */
    p, h1, h2, h3, h4, span, div, li {
        color: #e6edf3 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Input de contraseña estilo Hacker */
    .stTextInput input {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    /* 2. LA BURBUJA (DISEÑO FUSIONADO) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        /* TU FONDO FAVORITO (Gradiente) */
        background: linear-gradient(145deg, #1d2129 0%, #161b22 100%) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        /* TU SOMBRA FAVORITA */
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        margin-bottom: 25px !important;
        padding: 0px !important; /* CRUCIAL: Quita el relleno para que la foto toque los bordes */
        overflow: hidden !important;
    }
    
    /* Eliminar padding interno de Streamlit para que la foto llene todo */
    div[data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) {
        padding: 0px !important;
    }

    /* 3. EL EFECTO HOVER EXACTO QUE QUIERES */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: scale(1.02) !important; /* El salto */
        border-color: #58a6ff !important; /* Borde azul */
        box-shadow: 0 15px 40px rgba(88, 166, 255, 0.2) !important; /* El brillo azul */
        z-index: 10;
        cursor: pointer;
    }

    /* 4. FOTO OMNIPRESENTE (Ocupa todo el ancho) */
    .card-img-top {
        width: 100%;
        height: 240px; /* Altura fija para uniformidad */
        object-fit: cover;
        border-radius: 20px 20px 0 0; /* Solo redondea arriba */
        display: block;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* 5. CONTENIDO INTERNO (Con Padding) */
    .card-body {
        padding: 24px;
    }

    /* Título Grande */
    .sub-title {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        line-height: 1.2;
        margin-bottom: 15px;
        text-shadow: 0 4px 4px rgba(0,0,0,0.3);
    }

    /* 6. TAGS (MÁS GRANDES Y LLAMATIVOS) */
    .tag-pill {
        display: inline-block;
        color: white !important;
        padding: 6px 14px; /* Más grandes */
        border-radius: 8px;
        font-size: 12px; /* Letra más grande */
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 6px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* 7. DATOS PLAZO Y CUANTÍA (MÁS GRANDES) */
    .info-pill {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .info-label { 
        color: #8b949e !important; 
        font-size: 11px !important; /* Etiqueta más grande */
        font-weight: 800 !important; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        margin-bottom: 5px !important;
    }
    .info-value { 
        color: #58a6ff !important; /* Azul intenso */
        font-size: 22px !important; /* VALOR MUCHO MÁS GRANDE */
        font-weight: 900 !important; 
        margin: 0 !important;
    }

    /* Expander arreglado */
    .stExpander {
        background-color: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
    }
    .streamlit-expanderContent p { color: #d1d5db !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>🔒 SYSTEM ACCESS</h1>", unsafe_allow_html=True)
        st.text_input("Credencial Master", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

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

    # 3. COLORES DE TAGS (Fijos, no cambian con el tema)
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t or "eu" in t: return "#1f6feb" # Azul NextGen
        if "subvenc" in t: return "#238636" # Verde Dinero
        if "prestamo" in t: return "#da3633" # Rojo
        if "estatal" in t: return "#8957e5" # Morado
        return "#30363d" # Gris oscuro elegante

    # 4. IMÁGENES ESTABLES (Enlaces directos de alta calidad)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Enlaces directos a Unsplash (Optimizados para web)
        ids = {
            'dana': '1582213726461-8decb21c5763',     # Manos
            'univ': '1524178232363-1fb2b075b655',     # Biblioteca
            'solar': '1509391366360-2e959784a276',    # Solar
            'eolic': '1466611653911-954ff21b6724',    # Viento
            'indus': '1581091226825-a6a2a5aee158',    # Fabrica
            'digital': '1550751827-4bd374c3f58b',     # Codigo
            'agri': '1625246333195-78d9c38ad449',     # Campo
            'transp': '1553265027-99d530167b28',      # Coche
            'global': '1451187580459-43490279c0fa'    # Tech Blue
        }
        
        img = ids['global']
        if 'dana' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'lector', 'beca']): img = ids['univ']
        elif any(x in combined for x in ['solar', 'placa']): img = ids['solar']
        elif 'eolic' in combined: img = ids['eolic']
        elif any(x in combined for x in ['indust', 'fabrica']): img = ids['indus']
        elif any(x in combined for x in ['digital', 'tic']): img = ids['digital']
        elif any(x in combined for x in ['agro', 'campo']): img = ids['agri']
        elif any(x in combined for x in ['coche', 'movilid']): img = ids['transp']
        
        return f"https://images.unsplash.com/photo-{img}?auto=format&fit=crop&w=800&q=80"

    df = load_data()

    # --- UI PRINCIPAL ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; letter-spacing: -1px; text-align: left;'>📡 Radar de Inteligencia</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR SISTEMA", placeholder="Buscar oportunidad...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container(border=True):
                    # 1. IMAGEN HTML DIRECTA (Sin márgenes)
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<img src="{img_url}" class="card-img-top">', unsafe_allow_html=True)
                    
                    # 2. CUERPO DE LA TARJETA
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Probabilidad (Badge Flotante)
                    prob = str(fila.iloc[9]).strip()
                    p_color = "#3fb950" if "Alta" in prob else "#d29922"
                    st.markdown(f'<div style="float: right; color: {p_color}; font-size: 12px; font-weight: 800; border: 1px solid {p_color}; padding: 4px 10px; border-radius: 20px; text-transform: uppercase;">● {prob}</div>', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags (Aumentados de tamaño)
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 25px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # DATOS (Aumentados de tamaño)
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
                    
                    st.write("") # Espacio
                    
                    # Expander
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        st.markdown("**Resumen Estratégico:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.markdown("**Requisitos:**")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 VER BOE OFICIAL", str(fila.iloc[0]), use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Radar v25.0 • Ultimate Master Edition • 2025")
