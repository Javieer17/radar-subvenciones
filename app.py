import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Radar Subvenciones AI v21.0",
    page_icon="⚡",
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

    # --- DISEÑO CSS "HYBRID MASTER" (TU HOVER FAVORITO + ESTRUCTURA NUEVA) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap');
        
        /* 1. FONDO GLOBAL */
        .stApp { background-color: #050505 !important; }
        
        /* 2. TEXTOS SIEMPRE VISIBLES (Arreglo de lectura) */
        p, .stMarkdown, .stMarkdown p, li, span, div {
            color: #e6edf3 !important;
        }
        
        /* 3. LA TARJETA (Tu diseño favorito recuperado) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            /* El gradiente que te gustaba */
            background: linear-gradient(145deg, #1d2129 0%, #161b22 100%) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 0px !important;
            /* La sombra base original */
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            margin-bottom: 30px !important;
            overflow: hidden !important;
        }
        
        /* 4. EL EFECTO HOVER EXACTO (Azuliza + Levanta) */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            /* Escala al 1.02 como pediste */
            transform: scale(1.02) !important;
            /* Borde azul */
            border-color: #58a6ff !important;
            /* Sombra azulada específica */
            box-shadow: 0 15px 40px rgba(88, 166, 255, 0.2) !important;
            /* Efecto "azuliza": cambiamos ligeramente el gradiente de fondo */
            background: linear-gradient(145deg, #1d2129 0%, #232d3d 100%) !important;
            cursor: pointer;
            z-index: 10;
        }

        /* 5. FOTO DE CABECERA INTEGRADA */
        .header-box {
            width: 100%;
            height: 230px;
            background-size: cover;
            background-position: center;
            border-radius: 20px 20px 0 0; /* Coincide con la tarjeta */
            margin-top: -1px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            transition: 0.3s;
        }
        
        /* Brillo en la foto al pasar el ratón */
        div[data-testid="stVerticalBlockBorderWrapper"]:hover .header-box {
            filter: brightness(1.1) saturate(1.1);
        }

        /* 6. CONTENIDO INTERNO */
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

        /* Datos centrados (Estilo Apple Dark) */
        .info-pill {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .info-label { 
            color: #94a3b8 !important; 
            font-size: 10px !important; 
            font-weight: 700 !important; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            margin-bottom: 4px !important;
        }
        .info-value { 
            color: #38bdf8 !important; 
            font-size: 18px !important; 
            font-weight: 800 !important; 
            margin: 0 !important;
        }

        /* Expander Arreglado */
        .stExpander {
            background-color: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 15px !important;
        }
        
        .streamlit-expanderContent p, .streamlit-expanderContent li {
            color: #d1d5db !important;
            font-size: 15px !important;
        }
        
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

    # 4. IMÁGENES ACTUALIZADAS (Lista "Indestructible")
    def get_sector_image(sector, titulo):
        combined = (str(sector) + " " + str(titulo)).lower()
        
        # IDs de Unsplash verificados que funcionan bien en incrustación
        ids = {
            'dana': '1582213726461-8decb21c5763',     # Manos unidas (Comunidad)
            'univ': '1523240715630-341b21391307',     # Libros/Universidad
            'solar': '1508514177221-188b1cf16e9d',    # Panel Solar
            'eolic': '1466611653911-954ff21b6724',    # Molinos
            'indus': '1581091226825-a6a2a5aee158',    # Industria metal
            'digital': '1518770660439-4636190af475',  # Chips/Tech
            'agri': '1625246333195-78d9c38ad449',     # Campo
            'transp': '1553265027-99d530167b28',      # Coche eléctrico
            'global': '1451187580459-43490279c0fa'    # Tech azul general
        }
        
        img = ids['global']
        if 'dana' in combined: img = ids['dana']
        elif any(x in combined for x in ['univ', 'lector', 'beca', 'curso']): img = ids['univ']
        elif any(x in combined for x in ['solar', 'placa', 'energ']): img = ids['solar']
        elif 'eolic' in combined: img = ids['eolic']
        elif any(x in combined for x in ['indust', 'fabrica', 'manufactura']): img = ids['indus']
        elif any(x in combined for x in ['digital', 'tic', 'soft']): img = ids['digital']
        elif any(x in combined for x in ['agro', 'campo']): img = ids['agri']
        elif any(x in combined for x in ['coche', 'movilidad', 'transporte']): img = ids['transp']
        
        # Usamos parámetros de optimización para asegurar carga rápida
        return f"https://images.unsplash.com/photo-{img}?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"

    df = load_data()

    # --- UI PRINCIPAL ---
    st.markdown("<h1 style='color: #58a6ff; font-weight: 900; letter-spacing: -1px;'>📡 Radar Inteligente</h1>", unsafe_allow_html=True)
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
                    # FOTO INTEGRADA
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
                    
                    # Expander (Texto legible)
                    with st.expander("🚀 VER DETALLES Y ESTRATEGIA"):
                        st.markdown("**Resumen Ejecutivo:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                        st.write(fila.iloc[8])
                        st.link_button("🔗 VER BOE OFICIAL", str(fila.iloc[0]), use_container_width=True)
                    
                    # Datos Abajo (Alineados)
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

    st.caption("Radar v21.0 • Hybrid Master Edition • 2025")
