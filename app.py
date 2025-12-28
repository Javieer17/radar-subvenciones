import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Radar Subvenciones", layout="wide", page_icon="🚀")

@st.cache_data(ttl=60)
def load_data_diagnostic():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    # Esta URL exporta la primera hoja del Sheets
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Leemos el CSV
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# Cargar datos
df = load_data_diagnostic()

st.title("🚀 Radar de Subvenciones Inteligente")

if isinstance(df, str):
    st.error(f"No se pudo acceder al Google Sheets: {df}")
else:
    # --- BLOQUE DE DIAGNÓSTICO (Esto nos dirá qué está fallando) ---
    st.write("### 🔍 Diagnóstico de datos")
    st.write("Columnas detectadas:", df.columns.tolist())
    
    # Limpiar columnas: quitar espacios y posibles caracteres raros
    df.columns = [str(c).strip() for c in df.columns]

    # Buscar columnas clave (por si tienen nombres ligeramente diferentes)
    col_titulo = next((c for c in df.columns if 'tit' in c.lower()), None)
    
    if not col_titulo:
        st.error("❌ No encuentro la columna 'Título'. Mira arriba la lista de 'Columnas detectadas' y comprueba cómo se llaman en el Excel.")
        st.write("Vista previa de los datos recibidos:", df.head(3))
    else:
        st.success(f"✅ Columna '{col_titulo}' encontrada. Cargando subvenciones...")
        
        # --- LISTADO DE SUBVENCIONES ---
        for index, row in df.iterrows():
            # Solo mostramos si tiene título
            if pd.notna(row[col_titulo]):
                with st.container(border=True):
                    st.subheader(row[col_titulo])
                    
                    # Intentamos mostrar datos si existen esas columnas
                    resumen = row.get('Resumen', 'Sin resumen disponible')
                    st.write(f"**Resumen:** {resumen}")
                    
                    # Enlace al BOE
                    link = row.get('ID', '#')
                    st.link_button("🔗 Ver en el BOE", str(link))

st.divider()
st.caption("Sistema Radar v1.0 - n8n + Streamlit")
