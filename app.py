import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Radar de Subvenciones BOE", layout="wide", page_icon="🚀")

# 2. CONFIGURACIÓN DE DATOS (Tu ID real)
SHEET_ID = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
SHEET_NAME = "Hoja 1"

# Esta parte arregla el error de "control characters" codificando el espacio
query = urllib.parse.quote(SHEET_NAME)
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={query}"

# 3. CARGA DE DATOS CON CACHÉ
@st.cache_data(ttl=300)
def get_data():
    try:
        # Leemos el CSV directamente desde la URL corregida
        data = pd.read_csv(URL)
        # Limpiamos los nombres de las columnas para evitar espacios invisibles
        data.columns = [str(c).strip() for c in data.columns]
        # Quitamos filas que no tengan título
        data = data.dropna(subset=['Título'])
        return data
    except Exception as e:
        return f"Error al leer el Excel: {str(e)}"

# Ejecutar carga
df = get_data()

# --- INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades de negocio analizadas por IA directamente del BOE.")

# Si el resultado es un texto, es que ha habido un error
if isinstance(df, str):
    st.error(df)
    st.info("💡 Consejo: Asegúrate de que en Google Sheets la pestaña se llame exactamente 'Hoja 1' y el archivo sea público.")
else:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")
    
    # Filtro Sector
    sectores = sorted(df['Sector'].dropna().unique().tolist())
    sector_sel = st.sidebar.multiselect("Filtrar Sector", sectores, default=sectores)
    
    # Filtro Probabilidad
    probs = df['Probabilidad'].dropna().unique().tolist()
    prob_sel = st.sidebar.multiselect("Filtrar Probabilidad", probs, default=probs)

    # Aplicar filtros
    mask = df['Sector'].isin(sector_sel) & df['Probabilidad'].isin(prob_sel)
    df_result = df[mask]

    st.subheader(f"🔍 {len(df_result)} subvenciones encontradas")

    # --- LISTADO ---
    for _, row in df_result.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(row['Título'])
                st.write(f"**💰 Cuantía:** {row['Cuantía']} | **📅 Plazo:** {row['Plazo']}")
            with c2:
                # Color según probabilidad
                p = str(row['Probabilidad'])
                color = "green" if "Alta" in p else "orange" if "Media" in p else "gray"
                st.markdown(f"### :{color}[{p}]")
            
            with st.expander("Ver análisis detallado y requisitos"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Resumen:**")
                    st.write(row.get('Resumen', 'No disponible'))
                    st.write("**Oportunidad:**")
                    st.write(row.get('Justificación', 'No disponible'))
                with col_b:
                    st.write("**Requisitos:**")
                    st.write(row.get('Requisitos Detallados', 'No disponible'))
                
                st.divider()
                # Buscamos la URL en la columna ID o Enlace
                url_final = row.get('ID', row.get('Enlace Directo', '#'))
                st.link_button("🔗 Ver en el BOE", str(url_final))

st.divider()
st.caption("Actualizado automáticamente mediante n8n y Groq AI.")
