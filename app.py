import streamlit as st
import pandas as pd
import requests
import io
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Radar Subvenciones", layout="wide", page_icon="🚀")

# 2. FUNCIÓN PARA LIMPIAR Y CARGAR DATOS
@st.cache_data(ttl=300)
def load_data_from_google():
    # ID de tu Excel (limpiado de cualquier carácter raro)
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    # Construimos la URL de exportación a CSV
    raw_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    # LIMPIEZA EXTREMA: Borramos cualquier carácter invisible o de control
    # Solo permitimos letras, números y símbolos de URL estándar
    clean_url = re.sub(r'[^a-zA-Z0-9:/._?=&-]', '', raw_url)
    
    try:
        # Descargamos el contenido usando requests (más estable)
        response = requests.get(clean_url, timeout=10)
        response.raise_for_status() # Lanza error si no puede entrar
        
        # Convertimos el texto descargado en un DataFrame de Pandas
        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Limpiar nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        # Quitar filas sin título
        df = df.dropna(subset=['Título'])
        return df
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# Ejecutar la carga
df = load_data_from_google()

# --- INTERFAZ ---
st.title("🚀 Radar de Subvenciones Inteligente")
st.markdown("Oportunidades analizadas por IA directamente del BOE.")
st.divider()

if isinstance(df, str):
    st.error("⚠️ No se ha podido conectar con el Excel")
    st.write(f"Detalle técnico: {df}")
    st.info("Revisa: 1. Que el Excel sea público (Cualquier persona con el enlace > Lector). 2. Que no hayas cambiado el nombre de las columnas.")
else:
    # --- FILTROS EN BARRA LATERAL ---
    st.sidebar.header("Filtros")
    
    # Sector
    col_sector = 'Sector' if 'Sector' in df.columns else df.columns[5]
    lista_sectores = sorted(df[col_sector].unique().tolist())
    sec_sel = st.sidebar.multiselect("Filtrar por Sector", lista_sectores, default=lista_sectores)

    # Probabilidad
    col_prob = 'Probabilidad' if 'Probabilidad' in df.columns else df.columns[-1]
    lista_probs = df[col_prob].unique().tolist()
    prob_sel = st.sidebar.multiselect("Probabilidad", lista_probs, default=lista_probs)

    # Filtrado
    df_final = df[df[col_sector].isin(sec_sel) & df[col_prob].isin(prob_sel)]

    st.subheader(f"🔍 {len(df_final)} subvenciones detectadas")

    # --- LISTADO DE TARJETAS ---
    for _, row in df_final.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(row['Título'])
                st.write(f"**💰 Cuantía:** {row.get('Cuantía', 'Ver BOE')} | **📅 Plazo:** {row.get('Plazo', 'Ver BOE')}")
            with c2:
                p = str(row.get('Probabilidad', 'Media'))
                color = "green" if "Alta" in p else "orange" if "Media" in p else "gray"
                st.markdown(f"### :{color}[{p}]")
            
            with st.expander("Ver detalles y requisitos"):
                ca, cb = st.columns(2)
                with ca:
                    st.write("**Resumen:**")
                    st.write(row.get('Resumen', 'Consultar enlace'))
                    st.write("**Oportunidad:**")
                    st.write(row.get('Justificación', 'Consultar enlace'))
                with cb:
                    st.write("**Requisitos:**")
                    st.write(row.get('Requisitos Detallados', 'Consultar enlace'))
                
                st.divider()
                # El enlace al BOE
                url_final = str(row.get('ID', '#'))
                st.link_button("🔗 Abrir enlace del BOE", url_final)

st.divider()
st.caption("Automatizado con n8n, Groq y Streamlit")
