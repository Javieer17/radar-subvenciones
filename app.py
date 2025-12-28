import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Pro)
st.set_page_config(
    page_title="Radar de Subvenciones Inteligente",
    page_icon="📡",
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
        st.title("🔐 Acceso Privado")
        st.info("Introduce la contraseña para acceder al Radar de Inteligencia.")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Privado")
        st.error("❌ Contraseña incorrecta.")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- SOLO SI LA CONTRASEÑA ES CORRECTA, SE MUESTRA EL RESTO ---
if check_password():

    # --- ESTILOS CSS PERSONALIZADOS (CORREGIDO EL ESPACIO) ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
        
        .subs-card {
            background-color: #1d2129;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 10px; /* Reducido para evitar espacios vacíos */
            border: 1px solid #30363d;
            transition: transform 0.3s ease, border-color 0.3s ease;
            /* Eliminado el min-height que causaba el fallo del espacio */
        }
        .subs-card:hover {
            transform: translateY(-3px);
            border-color: #58a6ff;
        }
        
        .badge-prob {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            float: right;
            background: rgba(255,255,255,0.05);
        }
        
        .card-img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #30363d;
        }

        .tag {
            display: inline-block;
            color: white;
            padding: 3px 12px;
            border-radius: 15px;
            margin-right: 6px;
            margin-bottom: 6px;
            font-size: 10.5px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        /* Ajuste para reducir espacio de títulos */
        h3 { margin-bottom: 5px !important; line-height: 1.2 !important; }
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

    # 3. LÓGICA DE IMÁGENES (Añadidas más categorías)
    def get_sector_image(sector):
        s = str(sector).lower()
        if any(x in s for x in ['energ', 'foto', 'eolic', 'hidro']):
            return "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=800"
        elif any(x in s for x in ['industr', 'cvi', 'manufact']):
            return "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800"
        elif any(x in s for x in ['agro', 'campo', 'forest', 'agri']):
            return "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=800"
        elif any(x in s for x in ['digital', 'tic', 'tecnol', 'universi', 'docen']):
            return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&q=80&w=800"
        elif any(x in s for x in ['transporte', 'moves', 'vehicul']):
            return "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&q=80&w=800"
        elif any(x in s for x in ['dana', 'social', 'tercer sector', 'infanc']):
            return "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&q=80&w=800"
        else:
            return "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=800"

    df = load_data()

    # --- HEADER ---
    st.title("📡 Radar de Inteligencia de Subvenciones")
    st.markdown("##### Detección estratégica mediante IA del Boletín Oficial del Estado")

    if df is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Oportunidades", len(df))
        c2.metric("Sectores Activos", len(df.iloc[:, 5].unique()) if len(df) > 0 else 0)
        c3.metric("Acceso", "🔐 Protegido")
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
                    
                    # El div contenedor inicial
                    st.markdown(f"""
                    <div class="subs-card">
                        <img src="{get_sector_image(fila.iloc[5])}" class="card-img">
                        <div style="margin-bottom: 10px; overflow: hidden;">
                            <span class="badge-prob" style="color:{p_color}; border: 1px solid {p_color};">● {p_text}</span>
                            <h3 style="margin-top:0;">{fila.iloc[1]}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # ETIQUETAS
                    partes = str(fila.iloc[2]).split('|')
                    tags_html = '<div style="margin-bottom: 10px;">'
                    for p in partes:
                        p = p.strip()
                        color = "#1565C0" if "Next" in p or "PRTR" in p else "#2E7D32" if "Subvención" in p else "#455A64"
                        icon = "🇪🇺" if "Next" in p else "💰" if "Subvención" in p else "📍"
                        tags_html += f'<span class="tag" style="background-color:{color};">{icon} {p}</span>'
                    st.markdown(tags_html + '</div>', unsafe_allow_html=True)
                    
                    # DATOS RÁPIDOS
                    st.write(f"💵 **Cuantía:** {fila.iloc[3]}")
                    st.write(f"⏰ **Plazo:** {fila.iloc[4]}")
                    
                    # EXPANDER
                    with st.expander("📄 Análisis y Requisitos"):
                        tab_a, tab_b = st.tabs(["💡 Estrategia", "⚖️ Legal"])
                        with tab_a:
                            st.write(fila.iloc[6])
                            st.info(f"**Oportunidad:** {fila.iloc[7]}")
                        with tab_b:
                            st.write(fila.iloc[8])
                        st.link_button("🔗 Abrir en BOE", str(fila.iloc[0]))
                    
                    # Cerramos la tarjeta
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.write("") # Pequeño respiro entre tarjetas
    else:
        st.error("No se pudo conectar con la base de datos.")

st.caption("Radar Pro v4.0 | n8n + Groq + Streamlit Cloud (Private)")
