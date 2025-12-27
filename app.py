import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Radar de Subvenciones BOE", layout="wide")

st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades de negocio detectadas por IA directamente del BOE.")

# Conexión al Google Sheets (usa el link de tu hoja en formato CSV)
sheet_id = "TU_ID_DE_GOOGLE_SHEETS"
sheet_name = "Hoja 1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Leer datos
df = pd.read_csv(url)

# --- FILTROS EN LA BARRA LATERAL ---
st.sidebar.header("Filtros")
sector = st.sidebar.multiselect("Selecciona Sector", options=df["Sector"].unique(), default=df["Sector"].unique())
probabilidad = st.sidebar.multiselect("Probabilidad", options=df["Probabilidad"].unique(), default=df["Probabilidad"].unique())

# Filtrar el DataFrame
df_selection = df[(df["Sector"].isin(sector)) & (df["Probabilidad"].isin(probabilidad))]

# --- LISTADO DE SUBVENCIONES ---
for index, row in df_selection.iterrows():
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(f"{row['Título']}")
            st.write(f"**Sector:** {row['Sector']} | **Cuantía:** {row['Cuantía']} | **Plazo:** {row['Plazo']}")
        with col2:
            st.markdown(f"### `{row['Probabilidad']}`")
        
        with st.expander("Ver análisis de la IA"):
            st.write(f"**Resumen:** {row['Resumen']}")
            st.write(f"**Justificación:** {row['Justificación']}")
            st.write(f"**Requisitos:** {row['Requisitos Detallados']}")
            st.link_button("Ver en el BOE", row["ID"])
        st.divider()