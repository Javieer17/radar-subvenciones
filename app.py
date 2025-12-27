import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Radar de Subvenciones BOE", layout="wide", page_icon="🚀")

# 2. DATOS DE CONEXIÓN
sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
sheet_name = "Hoja 1"

# TRUCO: Codificamos el nombre de la hoja para que el espacio no rompa la URL
sheet_name_encoded = urllib.parse.quote(sheet_name)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"

# 3. FUNCIÓN PARA CARGAR DATOS
@st.cache_data(ttl=60) # Se actualiza cada minuto
def load_data():
    try:
        # Leemos el CSV
        df = pd.read_csv(url)
        # Limpiamos nombres de columnas por si tienen espacios ocultos
        df.columns = df.columns.str.strip()
        # Quitamos filas que no tengan título
        df = df.dropna(subset=['Título'])
        return df
    except Exception as e:
        return str(e)

df = load_data()

# --- INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades de negocio detectadas por IA directamente del BOE.")

if isinstance(df, str):
    st.error(f"Error crítico de conexión: {df}")
    st.info("Asegúrate de que la pestaña del Excel se llama exactamente 'Hoja 1' (con espacio) y que el archivo es público.")
else:
    # --- FILTROS ---
    st.sidebar.header("Filtros")
    
    # Filtro de Sector
    lista_sectores = sorted(df['Sector'].unique().tolist())
    sector_sel = st.sidebar.multiselect("Sector", options=lista_sectores, default=lista_sectores)
    
    # Filtro de Probabilidad
    lista_prob = df['Probabilidad'].unique().tolist()
    prob_sel = st.sidebar.multiselect("Probabilidad", options=lista_prob, default=lista_prob)

    # Aplicar filtros
    df_filtrado = df[df['Sector'].isin(sector_sel) & df['Probabilidad'].isin(prob_sel)]

    st.subheader(f"🔍 {len(df_filtrado)} subvenciones encontradas")

    # --- LISTADO ---
    for index, row in df_filtrado.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(row['Título'])
                st.write(f"**💰 Cuantía:** {row['Cuantía']} | **📅 Plazo:** {row['Plazo']}")
            with col2:
                # Color dinámico
                color = "green" if "Alta" in str(row['Probabilidad']) else "orange"
                st.markdown(f"### :{color}[{row['Probabilidad']}]")
            
            with st.expander("Ver detalles y requisitos"):
                st.write("**Resumen:**", row['Resumen'])
                st.write("**Justificación:**", row['Justificación'])
                st.write("**Requisitos:**", row['Requisitos Detallados'])
                st.divider()
                # Usamos el campo ID para el enlace
                st.link_button("🔗 Abrir en el BOE", str(row['ID']))

st.divider()
st.caption("Sistema automatizado con n8n, Groq AI y Streamlit.")
