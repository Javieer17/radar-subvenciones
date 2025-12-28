import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURACIÓN VISUAL PRO
st.set_page_config(page_title="Radar Subvenciones", layout="wide", page_icon="🚀")

@st.cache_data(ttl=30)
def load_data_final():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # TRUCO PARA LOS ACENTOS: Forzamos la lectura en UTF-8
        contenido = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(contenido))
        
        # Limpieza de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return f"Error: {str(e)}"

df = load_data_final()

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stExpander { border: 1px solid #30363d !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades del BOE detectadas y analizadas por Inteligencia Artificial.")
st.divider()

if isinstance(df, str):
    st.error(f"Error de conexión: {df}")
else:
    # Usamos las posiciones que ya sabemos que funcionan
    # 0:ID, 1:Título, 2:Ámbito, 3:Cuantía, 4:Plazo, 5:Sector, 6:Resumen, 7:Justificación, 8:Requisitos, 9:Probabilidad
    
    for i in range(len(df)):
        fila = df.iloc[i]
        if pd.isna(fila.iloc[1]): continue # Saltamos filas vacías

        with st.container():
            # Título y Probabilidad en la misma línea
            col_t, col_p = st.columns([5, 1])
            with col_t:
                st.subheader(fila.iloc[1])
            with col_p:
                p = str(fila.iloc[9]).strip()
                color = "green" if "Alta" in p else "orange" if "Media" in p else "gray"
                st.markdown(f"### :{color}[{p}]")
            
            # Datos clave con iconos
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**💰 Cuantía:**\n{fila.iloc[3]}")
            with c2:
                # Si el plazo es un número (error de Excel), lo mostramos tal cual o avisamos
                plazo = fila.iloc[4]
                st.markdown(f"**📅 Plazo:**\n{plazo}")
            with c3:
                st.markdown(f"**🏢 Sector:**\n{fila.iloc[5]}")

            # Desplegable de análisis
            with st.expander("🔍 Ver análisis detallado, justificación y requisitos"):
                tab1, tab2 = st.tabs(["📋 Resumen y Oportunidad", "⚖️ Requisitos Legales"])
                
                with tab1:
                    st.markdown("### Resumen")
                    st.write(fila.iloc[6])
                    st.markdown("### ¿Por qué es una oportunidad?")
                    st.info(fila.iloc[7])
                
                with tab2:
                    st.markdown("### Requisitos para acceder")
                    st.write(fila.iloc[8])
                
                st.divider()
                st.link_button("🔗 Abrir documentación oficial en el BOE", str(fila.iloc[0]))
            
            st.divider()

st.caption("Sistema Radar v2.1 | n8n + Groq AI + Streamlit Cloud")
