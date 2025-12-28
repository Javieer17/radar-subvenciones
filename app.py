import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones v20.0",
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

    # --- DISEÑO CSS "NIGHT VISION" (TEXTOS BLANCOS + HOVER AZUL) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap');
        
        /* 1. FORZAR FONDO Y TEXTOS GLOBALES */
        .stApp { background-color: #050505 !important; }
        
        /* ESTO ARREGLA LA LECTURA: Fuerza todo el texto a blanco/gris claro */
        p, .stMarkdown, .stMarkdown p, li, span, div {
            color: #e6edf3 !important;
        }
        
        /* 2. LA TARJETA (BURBUJA) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #121417 !important; /* Negro suave base */
            border-radius: 25px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            padding: 0px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            transition: all 0.3s ease-in-out !important;
            margin-bottom: 30px !important;
            overflow: hidden !important;
        }
        
        /* 3. EL EFECTO HOVER (El que querías) */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            /* Cambio de color de fondo a un Azul Noche */
            background-color: #161b26 !important; 
            /* Borde Cian */
            border-color: #00f2ff !important; 
            /* Se levanta */
            transform: translateY(-8px) scale(1.01) !important; 
            /* Resplandor Azul */
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.15) !important;
            cursor: pointer;
        }

        /* 4. IMAGEN DE CABECERA (Ajuste perfecto) */
        .header-box {
            width: 100%;
            height: 230px;
            background-size: cover;
            background-position: center;
            border-radius: 25px 25px 0 0;
            margin-top: -1px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            /* Filtro oscuro para que las letras resalten si van encima */
            filter: brightness(0.9);
            transition: 0.3s;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover .header-box {
            filter: brightness(1.1); /* Se ilumina la foto al pasar el ratón */
        }

        /* 5. CONTENIDO INTERNO */
        .card-body {
            padding: 25px;
        }

        .sub-title {
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif;
            font-size: 22px !important;
            font-weight: 800 !important;
            line-height: 1.3;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        /* Tags */
        .tag-pill {
            display: inline-block;
            color: white !important;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 5px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* Cajas de Datos (Estilo Apple Dark) */
        .info-pill {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .info-label { 
            color: #94a3b8 !important; /* Gris azulado para etiqueta */
            font-size: 10px !important; 
            font-weight: 700 !important; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            margin-bottom: 4px !important;
        }
        .info-value { 
            color: #38bdf8 !important; /* Azul cielo para el valor */
            font-size: 18px !important; 
            font-weight: 800 !important; 
            margin: 0 !important;
        }

        /* 6. ARREGLO DEL EXPANDER (Texto Blanco) */
        .stExpander {
            background-color: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 15px !important;
        }
        
        /* Forzamos el texto dentro del expander a ser blanco */
        .streamlit-expanderContent p, .streamlit-expanderContent li {
            color: #d1d5db !important; /* Blanco grisaceo muy legible */
            font-size: 15px !important;
        }
        
        /* Ocultar menú */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
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
        if "next" in t: return "#2563eb" # Azul Real
        if "subvenc" in t: return "#16a34a" # Verde
        if "prestamo" in t: return "#dc2626" # Rojo
        return "#475569" # Gris

    # 4. IMÁGENES (Nuevas URLs Estables)
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # Fotos nuevas de alta calidad
        ids = {
            'dana': '1636561842959-b3974c2cb01d', # Ayuda/Manos
            'univ': '1523050853173-ee040a84139b', # Universidad/Libros
            'tech': '1550751827-4bd374c3f58b',    # Tech General (Azul)
            'solar': '1508514177221-188b1cf16e9d', # Panel Solar Moderno
            'indus': '1531297461362-76ce3843087d', # Fabrica
            'digital': '1451187580459-43490279c0fa' # Red Digital
        }
        
        img = ids['tech']
        if 'dana' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'lector', 'beca']): img = ids['univ']
        elif any(x in combined for x in ['solar', 'placa', 'energ']): img = ids['solar']
        elif any(x in combined for x in ['indus', 'fabrica']): img = ids['indus']
        elif any(x in combined for x in ['digital', 'tic', 'soft']): img = ids['digital']
        
        return f"https://images.unsplash.com/photo-{img}?q=80&w=1000&auto=format&fit=crop"

    df = load_data()

    # --- UI ---
    st.markdown("<h1 style='color: #00f2ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar Inteligente</h1>", unsafe_allow_html=True)
    query = st.text_input("🔍 FILTRAR RESULTADOS", placeholder="Buscar...")

    if df is not None:
        if query:
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container(border=True):
                    # FOTO
                    img_url = get_sector_image(fila.iloc[5], fila.iloc[1])
                    st.markdown(f'<div class="header-box" style="background-image: url(\'{img_url}\');"></div>', unsafe_allow_html=True)
                    
                    # CONTENIDO
                    st.markdown('<div class="card-body">', unsafe_allow_html=True)
                    
                    # Probabilidad
                    prob = str(fila.iloc[9]).strip()
                    p_color = "#4ade80" if "Alta" in prob else "#fbbf24"
                    st.markdown(f'<div style="float: right; color: {p_color}; font-size: 11px; font-weight: 800; border: 1px solid {p_color}; padding: 2px 8px; border-radius: 10px;">{prob.upper()}</div>', unsafe_allow_html=True)
                    
                    # Título
                    st.markdown(f'<div class="sub-title">{fila.iloc[1]}</div>', unsafe_allow_html=True)
                    
                    # Tags
                    tags = str(fila.iloc[2]).split('|')
                    tags_html = "".join([f'<span class="tag-pill" style="background:{get_tag_color(t.strip())};">{t.strip()}</span>' for t in tags])
                    st.markdown(f'<div style="margin-bottom: 20px;">{tags_html}</div>', unsafe_allow_html=True)
                    
                    # Expander
                    with st.expander("🚀 VER DETALLES Y ESTRATEGIA"):
                        st.markdown("**Resumen Ejecutivo:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 VER BOE OFICIAL", str(fila.iloc[0]), use_container_width=True)
                    
                    # Datos
                    st.write("")
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
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Radar v20.0 • Text Fix Edition • 2025")
