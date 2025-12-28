import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN DE PÁGINA (Tema Oscuro Premium)
st.set_page_config(
    page_title="Radar de Subvenciones Pro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CSS PERSONALIZADOS (El "maquillaje") ---
st.markdown("""
    <style>
    /* Fondo y fuente general */
    .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    
    /* Estilo de las tarjetas */
    .subs-card {
        background-color: #1d2129;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .subs-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    
    /* Badges de probabilidad */
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-alta { background-color: #238636; color: white; }
    .badge-media { background-color: #9e6a03; color: white; }
    .badge-baja { background-color: #da3633; color: white; }
    
    /* Imagen de cabecera de tarjeta */
    .card-img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        response = requests.get(url, timeout=10)
        contenido = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(contenido))
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

# --- DICCIONARIO DE IMÁGENES POR SECTOR ---
# Esto asigna una foto profesional según la palabra que encuentre en "Sector"
def get_sector_image(sector):
    sector = str(sector).lower()
    if 'energ' in sector or 'foto' in sector:
        return "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=800"
    elif 'industr' in sector or 'cvi' in sector:
        return "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800"
    elif 'agro' in sector or 'campo' in sector:
        return "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=800"
    elif 'digital' in sector or 'tic' in sector:
        return "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800"
    elif 'transporte' in sector or 'moves' in sector:
        return "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&q=80&w=800"
    else:
        return "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=800"

df = load_data()

# --- HEADER PRINCIPAL ---
st.title("📡 Radar de Inteligencia de Subvenciones")
st.markdown("##### Análisis en tiempo real del BOE mediante IA")

if df is not None:
    # Métricas rápidas arriba
    c1, c2, c3 = st.columns(3)
    c1.metric("Ayudas Detectadas", len(df))
    c2.metric("Sectores Activos", len(df.iloc[:, 5].unique()))
    c3.metric("Última Actualización", "Hoy 08:00")
    
    st.divider()

    # --- GRID DE TARJETAS (2 por fila para que se vea más moderno) ---
    cols = st.columns(2)
    
    for i in range(len(df)):
        fila = df.iloc[i]
        if pd.isna(fila.iloc[1]): continue
        
        # Elegimos en qué columna poner la tarjeta (alternando)
        with cols[i % 2]:
            # Contenedor con borde y sombra (vía CSS)
            with st.container():
                st.markdown(f"""
                <div class="subs-card">
                    <img src="{get_sector_image(fila.iloc[5])}" class="card-img">
                </div>
                """, unsafe_allow_html=True)
                
                # Título y Probabilidad
                p = str(fila.iloc[9]).strip()
                p_class = "badge-alta" if "Alta" in p else "badge-media" if "Media" in p else "badge-baja"
                
                col_t, col_p = st.columns([3, 1])
                col_t.subheader(fila.iloc[1])
                col_p.markdown(f'<span class="badge {p_class}">{p}</span>', unsafe_allow_html=True)
                
                # Datos rápidos
                st.write(f"💰 **Cuantía:** {fila.iloc[3]}")
                st.write(f"📅 **Plazo:** {fila.iloc[4]}")
                st.write(f"🏢 **Sector:** {fila.iloc[5]}")
                
                # Detalles expandibles
                with st.expander("🔍 Análisis e Información Detallada"):
                    st.markdown("#### 📋 Resumen")
                    st.write(fila.iloc[6])
                    st.markdown("#### 🎯 Oportunidad de Negocio")
                    st.info(fila.iloc[7])
                    st.markdown("#### ⚖️ Requisitos")
                    st.write(fila.iloc[8])
                    st.divider()
                    st.link_button("🔗 Ir al documento oficial del BOE", str(fila.iloc[0]))
                
                st.write("") # Espaciado

else:
    st.error("No se pudo cargar la base de datos.")

st.caption("Tecnología: n8n + Groq Llama 3 + Streamlit Cloud")
