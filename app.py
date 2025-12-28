import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Pro)
st.set_page_config(
    page_title="Radar de Subvenciones Inteligente",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed", # Cerramos la barra lateral por defecto
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    
    .subs-card {
        background-color: #1d2129;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
        transition: transform 0.3s ease, border-color 0.3s ease;
        min-height: 450px;
    }
    .subs-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    
    .badge-prob {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        float: right;
    }
    
    .card-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #30363d;
    }

    .tag {
        display: inline-block;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 11px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        response = requests.get(url, timeout=10)
        # Forzamos UTF-8 para evitar los símbolos raros en acentos y €
        contenido = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(contenido))
        # Limpieza de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

# 3. LÓGICA DE IMÁGENES POR SECTOR
def get_sector_image(sector):
    s = str(sector).lower()
    if 'energ' in s or 'foto' in s or 'eolic' in s:
        return "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=800"
    elif 'industr' in s or 'cvi' in s or 'manufact' in s:
        return "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800"
    elif 'agro' in s or 'campo' in s or 'forest' in s:
        return "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=800"
    elif 'digital' in s or 'tic' in s or 'tecnol' in s:
        return "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800"
    elif 'transporte' in s or 'moves' in s or 'vehicul' in s:
        return "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&q=80&w=800"
    elif 'dana' in s or 'social' in s:
        return "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&q=80&w=800"
    else:
        return "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=800"

df = load_data()

# --- HEADER PRINCIPAL ---
st.title("📡 Radar de Inteligencia de Subvenciones")
st.markdown("##### Detección estratégica mediante IA del Boletín Oficial del Estado")

if df is not None:
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Oportunidades", len(df))
    c2.metric("Sectores Clave", len(df.iloc[:, 5].unique()) if len(df) > 0 else 0)
    c3.metric("Status", "En tiempo real")
    
    st.divider()

    # --- GRID DE TARJETAS (2 columnas) ---
    cols = st.columns(2)
    
    for i in range(len(df)):
        fila = df.iloc[i]
        if pd.isna(fila.iloc[1]): continue
        
        with cols[i % 2]:
            with st.container():
                # Probabilidad con colores
                prob_text = str(fila.iloc[9]).strip()
                prob_color = "#238636" if "Alta" in prob_text else "#9e6a03" if "Media" in prob_text else "#455A64"
                
                # Imagen y Título
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5])}" class="card-img">
                    <div style="margin-bottom: 10px;">
                        <span class="badge-prob" style="color:{prob_color}; border: 1px solid {prob_color}; padding: 2px 10px; border-radius:10px;">
                            ● {prob_text}
                        </span>
                        <h3 style="margin-top:0; font-size: 20px;">{fila.iloc[1]}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # --- SISTEMA DE ETIQUETAS DINÁMICAS ---
                partes_ambito = str(fila.iloc[2]).split('|')
                etiquetas_html = '<div style="margin-bottom: 15px;">'
                for p in partes_ambito:
                    p = p.strip()
                    if "Next" in p or "PRTR" in p or "EU" in p:
                        color, icon = "#1565C0", "🇪🇺"
                    elif "Subvención" in p or "Fondo Perdido" in p:
                        color, icon = "#2E7D32", "💰"
                    elif "Préstamo" in p:
                        color, icon = "#C62828", "🏦"
                    else:
                        color, icon = "#455A64", "📍"
                    
                    etiquetas_html += f'<span class="tag" style="background-color:{color};">{icon} {p}</span>'
                
                etiquetas_html += '</div>'
                st.markdown(etiquetas_html, unsafe_allow_html=True)
                
                # Datos rápidos
                st.write(f"💵 **Cuantía:** {fila.iloc[3]}")
                st.write(f"⏰ **Plazo:** {fila.iloc[4]}")
                st.write(f"🏢 **Sector:** {fila.iloc[5]}")
                
                # Detalles expandibles
                with st.expander("📄 Ver Análisis de Negocio y Requisitos"):
                    t1, t2 = st.tabs(["💡 Oportunidad", "⚖️ Requisitos"])
                    with t1:
                        st.markdown("**Resumen Ejecutivo:**")
                        st.write(fila.iloc[6])
                        st.info(f"**Justificación:** {fila.iloc[7]}")
                    with t2:
                        st.write(fila.iloc[8])
                    
                    st.divider()
                    st.link_button("🔗 Ver documentación en BOE", str(fila.iloc[0]))
                
                # Cerramos el div de la card
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Error cargando la base de datos de Google Sheets.")

st.caption("Radar Inteligente v3.1 | n8n + Groq + Streamlit Cloud")
