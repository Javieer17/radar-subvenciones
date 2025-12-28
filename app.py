import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Pro)
st.set_page_config(
    page_title="Radar Subvenciones AI",
    page_icon="⚡",
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
        st.title("🔐 Acceso de Seguridad")
        st.info("Introduce la clave de acceso al sistema de inteligencia.")
        st.text_input("Credencial de acceso", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso de Seguridad")
        st.error("❌ Credencial no autorizada.")
        st.text_input("Credencial de acceso", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- SOLO SI LA CONTRASEÑA ES CORRECTA, SE MUESTRA EL RESTO ---
if check_password():

    # --- ESTILOS CSS AVANZADOS (EL GLOW UP) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
        
        /* Efecto de Tarjeta Premium */
        .subs-card {
            background: linear-gradient(145deg, #1d2129 0%, #161b22 100%);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .subs-card:hover {
            transform: scale(1.02);
            border-color: #58a6ff;
            box-shadow: 0 15px 40px rgba(88, 166, 255, 0.2);
        }
        
        /* Badges */
        .badge-prob {
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            float: right;
            backdrop-filter: blur(5px);
        }
        
        .card-img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 18px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        .tag {
            display: inline-block;
            color: white;
            padding: 4px 14px;
            border-radius: 8px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: rgba(255,255,255,0.1);
        }
        
        h3 { 
            color: #f0f6fc; 
            font-weight: 800 !important; 
            font-size: 22px !important;
            margin-bottom: 10px !important;
        }

        /* Estilo para las métricas */
        [data-testid="stMetricValue"] {
            font-weight: 800;
            color: #58a6ff;
        }
        </style>
        """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS (Usando Secret)
    @st.cache_data(ttl=60)
    def load_data():
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        try:
            response = requests.get(url, timeout=10)
            contenido = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(contenido))
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None

    # 3. LÓGICA DE IMÁGENES (Fotos Premium Seleccionadas)
    def get_sector_image(sector):
        s = str(sector).lower()
        if any(x in s for x in ['energ', 'foto', 'eolic', 'hidro']):
            return "https://images.unsplash.com/photo-1466611653911-954ff21b6724?q=80&w=1000" # Modern Solar
        elif any(x in s for x in ['industr', 'cvi', 'manufact', 'descarboni']):
            return "https://images.unsplash.com/photo-1565467311310-985f679786a3?q=80&w=1000" # Cyber Industry
        elif any(x in s for x in ['agro', 'campo', 'forest', 'agri']):
            return "https://images.unsplash.com/photo-1560493676-04071c5f4b52?q=80&w=1000" # High-tech Agri
        elif any(x in s for x in ['digital', 'tic', 'tecnol', 'universi', 'docen', 'lector']):
            return "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=1000" # Clean Tech
        elif any(x in s for x in ['transporte', 'moves', 'vehicul']):
            return "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?q=80&w=1000" # EV Future
        elif any(x in s for x in ['dana', 'social', 'tercer sector', 'infanc', 'atencion']):
            return "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1000" # Community
        else:
            return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000" # Data Global

    df = load_data()

    # --- HEADER CON BUSCADOR ---
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.title("📡 Radar de Inteligencia")
        st.markdown("##### BOE Deep Scanning • Análisis Estratégico mediante IA")
    with col_h2:
        search_query = st.text_input("🔍 Buscar por palabra clave...", placeholder="Ej: Industria, DANA, Digital...")

    if df is not None:
        # Filtrar si hay búsqueda
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        c1, c2, c3 = st.columns(3)
        c1.metric("Resultados", len(df))
        c2.metric("Sectores", len(df.iloc[:, 5].unique()) if len(df) > 0 else 0)
        c3.metric("Filtro", "Activo" if search_query else "Total")
        st.divider()

        # --- GRID DE TARJETAS ---
        cols = st.columns(2)
        for i in range(len(df)):
            fila = df.iloc[i]
            if pd.isna(fila.iloc[1]): continue
            
            with cols[i % 2]:
                with st.container():
                    p_text = str(fila.iloc[9]).strip()
                    p_color = "#238636" if "Alta" in p_text else "#9e6a03"
                    
                    st.markdown(f"""
                    <div class="subs-card">
                        <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 5px;">
                            <img src="{get_sector_image(fila.iloc[5])}" class="card-img">
                        </div>
                        <div style="margin-top: 10px;">
                            <span class="badge-prob" style="color:{p_color}; border: 1px solid {p_color};">● {p_text}</span>
                            <h3 style="margin-top:0;">{fila.iloc[1]}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # ETIQUETAS DINÁMICAS
                    partes = str(fila.iloc[2]).split('|')
                    tags_html = '<div style="margin-bottom: 15px;">'
                    for p in partes:
                        p = p.strip()
                        color = "#1565C0" if "Next" in p or "PRTR" in p or "EU" in p else "#2E7D32" if "Subvención" in p else "#455A64"
                        icon = "🇪🇺" if "Next" in p else "💰" if "Subvención" in p else "📍"
                        tags_html += f'<span class="tag" style="background-color:{color};">{icon} {p}</span>'
                    st.markdown(tags_html + '</div>', unsafe_allow_html=True)
                    
                    # INFO PRINCIPAL
                    st.write(f"💸 **CUANTÍA:** {fila.iloc[3]}")
                    st.write(f"🕒 **PLAZO:** {fila.iloc[4]}")
                    
                    # ACORDEÓN DE DETALLES
                    with st.expander("🚀 ANALIZAR OPORTUNIDAD"):
                        tab_a, tab_b = st.tabs(["🎯 Estrategia Comercial", "📜 Requisitos de Acceso"])
                        with tab_a:
                            st.markdown("---")
                            st.markdown("**Resumen IA:**")
                            st.write(fila.iloc[6])
                            st.info(f"**Justificación de Negocio:** {fila.iloc[7]}")
                        with tab_b:
                            st.markdown("---")
                            st.write(fila.iloc[8])
                        
                        st.link_button("🔗 Acceder al BOE", str(fila.iloc[0]), use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.write("") 
    else:
        st.error("Fallo de enlace con la base de datos.")

st.caption("Radar v5.0 Master Edition | Secure Intelligent Monitoring")
