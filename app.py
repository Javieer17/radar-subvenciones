import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Radar de Subvenciones", layout="wide", page_icon="🚀")

# 2. LIMPIEZA EXTREMA DEL ID
# Copiamos el ID y le quitamos cualquier espacio o salto de línea invisible
RAW_ID = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
CLEAN_ID = re.sub(r'[\s\t\n\r]', '', RAW_ID)

# Construimos la URL de exportación directa (más fiable que la de consulta)
url = f"https://docs.google.com/spreadsheets/d/{CLEAN_ID}/export?format=csv"
# Limpiamos la URL final por si acaso
url = "".join(url.split())

# 3. CARGA DE DATOS
@st.cache_data(ttl=300)
def load_data(url_to_load):
    try:
        # Cargamos el CSV
        data = pd.read_csv(url_to_load)
        # Limpiar nombres de columnas
        data.columns = [str(c).strip() for c in data.columns]
        # Quitar filas vacías
        data = data.dropna(subset=['Título'])
        return data
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# Ejecutar
df = load_data(url)

# --- INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades detectadas por IA directamente del BOE.")
st.divider()

if isinstance(df, str):
    st.error("⚠️ No se ha podido cargar el Excel")
    st.write(f"Detalle técnico: {df}")
    st.info("Revisa que en Google Sheets hayas dado a: Compartir > Cualquier persona con el enlace > Lector.")
else:
    # --- FILTROS ---
    st.sidebar.header("Filtros")
    
    # Filtro Sector
    col_sector = 'Sector' if 'Sector' in df.columns else df.columns[5] # Intento detectar la columna
    sectores = sorted(df[col_sector].unique().tolist())
    sec_sel = st.sidebar.multiselect("Sector", sectores, default=sectores)

    # Filtro Probabilidad
    col_prob = 'Probabilidad' if 'Probabilidad' in df.columns else df.columns[-1]
    probs = df[col_prob].unique().tolist()
    prob_sel = st.sidebar.multiselect("Probabilidad", probs, default=probs)

    # Filtrar
    df_result = df[df[col_sector].isin(sec_sel) & df[col_prob].isin(prob_sel)]

    st.subheader(f"🔍 {len(df_result)} subvenciones encontradas")

    # --- LISTADO ---
    for _, row in df_result.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(row['Título'])
                st.write(f"**💰 Cuantía:** {row.get('Cuantía', 'Ver en BOE')} | **📅 Plazo:** {row.get('Plazo', 'Ver en BOE')}")
            with c2:
                p = str(row.get('Probabilidad', 'Media'))
                color = "green" if "Alta" in p else "orange" if "Media" in p else "gray"
                st.markdown(f"### :{color}[{p}]")
            
            with st.expander("Ver análisis detallado"):
                st.write("**Resumen:**", row.get('Resumen', 'Consultar enlace'))
                st.write("**Justificación:**", row.get('Justificación', 'Consultar enlace'))
                st.write("**Requisitos:**", row.get('Requisitos Detallados', 'Consultar enlace'))
                st.divider()
                st.link_button("🔗 Abrir BOE", str(row.get('ID', '#')))

st.divider()
st.caption("Hecho con n8n, Groq y Streamlit")
