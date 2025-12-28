import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Radar Subvenciones", layout="wide", page_icon="🚀")

@st.cache_data(ttl=30) # Cache de solo 30 segundos para pruebas
def load_data_final():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        # LIMPIEZA TOTAL DE COLUMNAS
        # Quitamos espacios, tildes y ponemos en minúsculas para que no falle nada
        df.columns = [str(c).strip().lower()
                      .replace('á', 'a').replace('é', 'e')
                      .replace('í', 'i').replace('ó', 'o')
                      .replace('ú', 'u') for c in df.columns]
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# Cargar los datos
df = load_data_final()

st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades del BOE analizadas por IA.")

if isinstance(df, str):
    st.error(f"Error de conexión: {df}")
else:
    # --- BUSCADOR DE COLUMNAS POR ORDEN (SISTEMA SEGURO) ---
    # En lugar de nombres, usamos la posición según la lista que me has pasado
    # ID(0), Título(1), Ámbito(2), Cuantía(3), Plazo(4), Sector(5), Resumen(6), Justificación(7), Requisitos(8), Probabilidad(9)
    
    try:
        # Extraemos las columnas por posición para que no importe el nombre
        # Usamos .iloc para mayor seguridad
        for i in range(len(df)):
            fila = df.iloc[i]
            
            with st.container(border=True):
                col_izq, col_der = st.columns([4, 1])
                
                with col_izq:
                    # Columna 1: Título
                    st.subheader(fila.iloc[1])
                    # Columna 3: Cuantía | Columna 4: Plazo
                    st.write(f"**💰 Cuantía:** {fila.iloc[3]} | **📅 Plazo:** {fila.iloc[4]}")
                    # Columna 5: Sector
                    st.write(f"**🏢 Sector:** {fila.iloc[5]}")
                
                with col_der:
                    # Columna 9: Probabilidad
                    p = str(fila.iloc[9]).lower()
                    color = "green" if "alta" in p else "orange" if "med" in p else "gray"
                    st.markdown(f"### :{color}[{fila.iloc[9]}]")

                with st.expander("🔍 Ver análisis detallado y requisitos"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Resumen:**")
                        st.write(fila.iloc[6]) # Columna 6
                        st.write("**Oportunidad:**")
                        st.write(fila.iloc[7]) # Columna 7
                    with c2:
                        st.write("**Requisitos:**")
                        st.write(fila.iloc[8]) # Columna 8
                    
                    st.divider()
                    # Columna 0: ID (Enlace)
                    st.link_button("🔗 Abrir en el BOE", str(fila.iloc[0]))
                    
    except Exception as e:
        st.warning("Hay un problema con el formato de las filas.")
        st.write("Columnas que veo:", df.columns.tolist())
        st.write("Error:", e)

st.divider()
st.caption("Radar v2.0 - Funcionando sin depender de nombres de columnas")
