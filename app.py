import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Radar de Subvenciones BOE", layout="wide", page_icon="🚀")

# 2. CONEXIÓN CON TU GOOGLE SHEETS
# Tu ID real extraído del enlace que me pasaste
sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
sheet_name = "Hoja 1"  # Asegúrate de que en tu Excel la pestaña se llame así
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# 3. CARGA DE DATOS
@st.cache_data(ttl=600)  # Actualiza los datos cada 10 minutos
def load_data():
    try:
        df = pd.read_csv(url)
        # Limpiar filas completamente vacías si las hay
        df = df.dropna(subset=['Título']) 
        return df
    except Exception as e:
        st.error(f"Error al conectar con el Radar: {e}")
        return pd.DataFrame()

df = load_data()

# --- DISEÑO DE LA INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades de negocio detectadas por IA directamente del BOE.")
st.divider()

if df.empty:
    st.warning("No se han encontrado datos. Revisa que el Google Sheets sea público y tenga datos.")
else:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros de Búsqueda")
    
    # Filtro por Sector
    sectores = df['Sector'].unique().tolist()
    sector_sel = st.sidebar.multiselect("Filtrar por Sector", opciones=sectores, default=sectores)
    
    # Filtro por Probabilidad
    probabilidades = df['Probabilidad'].unique().tolist()
    prob_sel = st.sidebar.multiselect("Filtrar por Probabilidad", opciones=probabilidades, default=probabilidades)

    # Aplicar filtros
    df_filtrado = df[df['Sector'].isin(sector_sel) & df['Probabilidad'].isin(prob_sel)]

    # --- LISTADO DE RESULTADOS ---
    st.subheader(f"🔍 {len(df_filtrado)} subvenciones encontradas")

    for index, row in df_filtrado.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {row['Título']}")
                st.markdown(f"**💰 Cuantía:** {row['Cuantía']} | **📅 Plazo:** {row['Plazo']}")
                st.markdown(f"**📍 Ámbito:** {row['Ámbito']} | **🏢 Sector:** {row['Sector']}")
            
            with col2:
                # Color según probabilidad
                color = "green" if "Alta" in str(row['Probabilidad']) else "orange" if "Media" in str(row['Probabilidad']) else "gray"
                st.markdown(f"### :{color}[{row['Probabilidad']}]")
            
            # Detalle desplegable
            with st.expander("📄 Ver Análisis Detallado y Requisitos"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Resumen:**")
                    st.write(row['Resumen'])
                    st.write("**Justificación de negocio:**")
                    st.write(row['Justificación'])
                with c2:
                    st.write("**Requisitos:**")
                    st.write(row['Requisitos Detallados'])
                
                st.divider()
                # El enlace al BOE es la columna ID o Enlace Directo
                url_boe = row['ID'] if 'ID' in row else "#"
                st.link_button("🔗 Abrir en el BOE", url_boe)

# Estilo visual extra
st.markdown("""
    <style>
    .stMainContainer {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
