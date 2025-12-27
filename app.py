import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Radar de Subvenciones BOE", layout="wide", page_icon="🚀")

# 2. CONEXIÓN LIMPIA (Solo el ID, sin nombres de hoja para evitar errores)
# Hemos limpiado el ID de cualquier espacio invisible con .strip()
SHEET_ID = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk".strip()

# Usamos el formato de exportación directa a CSV, que es el más robusto
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 3. FUNCIÓN DE CARGA
@st.cache_data(ttl=300)
def load_data():
    try:
        # Cargamos los datos
        data = pd.read_csv(URL)
        # Limpieza de nombres de columnas (quitar espacios en blanco)
        data.columns = [str(c).strip() for c in data.columns]
        # Eliminar filas donde el Título esté vacío
        data = data.dropna(subset=['Título'])
        return data
    except Exception as e:
        return f"Error al leer los datos: {str(e)}"

# Ejecutar carga
df = load_data()

# --- INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades de negocio analizadas por IA directamente del BOE.")
st.divider()

if isinstance(df, str):
    st.error(df)
    st.info("Asegúrate de que el Google Sheets esté en 'Cualquier persona con el enlace' como Lector.")
else:
    # --- FILTROS LATERALES ---
    st.sidebar.header("Filtros")
    
    # Filtro Sector
    if 'Sector' in df.columns:
        sectores = sorted(df['Sector'].unique().tolist())
        sec_sel = st.sidebar.multiselect("Filtrar por Sector", sectores, default=sectores)
    else:
        sec_sel = []

    # Filtro Probabilidad
    if 'Probabilidad' in df.columns:
        probs = df['Probabilidad'].unique().tolist()
        prob_sel = st.sidebar.multiselect("Filtrar por Probabilidad", probs, default=probs)
    else:
        prob_sel = []

    # Aplicar Filtros
    df_result = df[df['Sector'].isin(sec_sel) & df['Probabilidad'].isin(prob_sel)]

    st.subheader(f"🔍 {len(df_result)} subvenciones encontradas")

    # --- LISTADO ---
    for _, row in df_result.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(row['Título'])
                st.write(f"**💰 Cuantía:** {row.get('Cuantía', 'N/A')} | **📅 Plazo:** {row.get('Plazo', 'N/A')}")
            with col2:
                p = str(row.get('Probabilidad', 'Media'))
                color = "green" if "Alta" in p else "orange" if "Media" in p else "gray"
                st.markdown(f"### :{color}[{p}]")
            
            with st.expander("Ver análisis y requisitos"):
                ca, cb = st.columns(2)
                with ca:
                    st.write("**Resumen:**")
                    st.write(row.get('Resumen', 'Consultar en el BOE'))
                    st.write("**Justificación:**")
                    st.write(row.get('Justificación', 'Consultar en el BOE'))
                with cb:
                    st.write("**Requisitos:**")
                    st.write(row.get('Requisitos Detallados', 'Consultar en el BOE'))
                
                st.divider()
                # El enlace es la columna ID o 'Enlace Directo'
                link = row.get('ID', '#')
                st.link_button("🔗 Abrir enlace oficial", str(link))

st.divider()
st.caption("Sistema automatizado con n8n y Groq AI.")
