import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI | Clean Pro",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# CSS "CLEAN CORPORATE" - SIN ERRORES DE COLOR
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* 1. FONDO DE LA APP (Gris Muy Claro Profesional) */
    .stApp {
        background-color: #F2F4F8 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* 2. TEXTOS (Siempre oscuros para que se lean bien) */
    h1, h2, h3, h4, p, span, div, li {
        color: #1F2937 !important; /* Gris Oscuro casi negro */
    }
    
    /* Títulos azules para destacar */
    h1 { color: #2563EB !important; } 

    /* 3. INPUTS (Buscador y Clave) */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }

    /* 4. LA TARJETA (BURBUJA) - BLANCA Y LIMPIA */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important; /* Borde gris muy suave */
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        padding: 16px !important; /* Streamlit pone esto, lo compensamos en la foto */
        transition: all 0.3s ease-in-out !important;
        overflow: hidden !important;
    }

    /* 5. EL HOVER (Borde Azul + Levantar) */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) !important;
        border-color: #2563EB !important; /* AZUL FUERTE */
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.15) !important; /* Sombra azulada suave */
        z-index: 10;
        cursor: pointer;
    }

    /* 6. FOTO QUE ENCAJA PERFECTA (TRUCO DE MÁRGENES NEGATIVOS) */
    .card-img-top {
        width: calc(100% + 32px) !important; /* Compensamos el padding */
        margin-left: -16px !important;       /* Movemos a la izquierda */
        margin-top: -16px !important;        /* Movemos arriba */
        margin-right: -16px !important;      /* Movemos a la derecha */
        height: 200px !important;
        object-fit: cover;
        border-radius: 16px 16px 0 0 !important; /* Redondeamos solo arriba */
        display: block;
        margin-bottom: 15px;
        border-bottom: 1px solid #E5E7EB;
    }

    /* 7. ETIQUETAS (TAGS) */
    .tag-pill {
        display: inline-block;
        color: white !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 5px;
        margin-bottom: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* 8. DATOS (CUANTIA/PLAZO) - ESTILO AZUL */
    .info-box {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        border: 1px solid #E5E7EB;
    }
    .info-label {
        font-size: 10px !important;
        color: #6B7280 !important; /* Gris medio */
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    .info-value {
        font-size: 16px !important;
        color: #2563EB !important; /* Azul Principal */
        font-weight: 900 !important;
    }
    
    /* Expander limpio */
    .stExpander {
        border: none !important;
        background: transparent !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# SEGURIDAD
# ---------------------------------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>🔐 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():

    # ---------------------------------------------------------
    # LÓGICA Y DATOS
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

    # COLORES DE ETIQUETAS (Siempre legibles)
    def get_tag_color(tag):
        t = tag.lower()
        if "next" in t: return "#1E40AF" # Azul oscuro
        if "subvenc" in t: return "#166534" # Verde oscuro
        if "prestamo" in t: return "#991B1B" # Rojo oscuro
        return "#374151" # Gris oscuro

    # IMÁGENES ESTABLES (Picsum con keywords)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        seed = "office" # Por defecto
        
        if 'dana' in combined: seed = "hands"
        elif any(x in combined for x in ['univ', 'lector', 'beca']): seed = "books"
        elif any(x in combined for x in ['solar', 'placa', 'energ']): seed = "solar"
        elif 'eolic' in combined: seed = "wind"
        elif any(x in combined for x in ['indust', 'fabrica']): seed = "factory"
        elif any(x in combined for x in ['digital', 'tic', 'soft']): seed = "laptop"
        elif any(x in combined for x in ['agro', 'campo']): seed = "nature"
        elif any(x in combined for x in ['coche', 'movilidad']): seed = "car"
        
        # Usamos Picsum Photos, muy rápido y estable
        return f"https://picsum.photos/seed/{seed}/800/400"

    df = load_data()

    # ---------------------------------------------------------
    # INTERFAZ (UI)
    # ---------------------------------------------------------
    st.title("📡 Radar de Inteligencia")
    st.markdown("**Sistema de Monitorización de Oportunidades**")
    
    query = st.text_input("🔍 FILTRAR", placeholder="Buscar por palabra clave...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container(border=True): # Creamos la caja
                    
                    # 1. IMAGEN AJUSTADA (Con margen negativo para tocar bordes)
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<img src="{img_url}" class="card-img-top">', unsafe_allow_html=True)
                    
                    # 2. PROBABILIDAD (Badge)
                    prob = str(fila.iloc[9]).strip()
                    color_badge = "#166534" if "Alta" in prob else "#854D0E"
                    bg_badge = "#DCFCE7" if "Alta" in prob else "#FEF9C3"
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="font-size:10px; font-weight:800; color:#9CA3AF;">SECTOR: {str(fila.iloc[5]).upper()}</span>
                            <span style="background-color:{bg_badge}; color:{color_badge}; padding:4px 8px; border-radius:12px; font-size:11px; font-weight:800; border:1px solid {color_badge};">● {prob.upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. TÍTULO
                    st.markdown(f'<h3 style="margin:0 0 15px 0; font-size:18px; line-height:1.4;">{fila.iloc[1]}</h3>', unsafe_allow_html=True)
                    
                    # 4. TAGS
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 15px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # 5. DATOS (Cajas Azules Claras)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="info-box"><div class="info-label">💰 Cuantía</div><div class="info-value">{fila.iloc[3]}</div></div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="info-box"><div class="info-label">⏳ Plazo</div><div class="info-value">{fila.iloc[4]}</div></div>', unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # 6. EXPANDER
                    with st.expander("Ver Detalles y Estrategia"):
                        st.markdown("**Resumen:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.link_button("🔗 Abrir BOE Oficial", str(fila.iloc[0]), use_container_width=True)

    st.markdown("---")
    st.caption("Sistema Radar v26.0 - Clean Corporate Edition")
