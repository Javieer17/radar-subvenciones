import streamlit as st
import pandas as pd
import requests
import io
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Radar Subvenciones", layout="wide", page_icon="🚀")

@st.cache_data(ttl=60)
def load_data_pro():
    sheet_id = "1XpsEMDFuvV-0fYM51ajDTdtZz21MGFp7t-M-bkrNpRk"
    # Usamos la exportación directa que es la más estable
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Leemos el CSV
        df = pd.read_csv(io.StringIO(response.text))
        
        # LIMPIEZA DE COLUMNAS: Quitamos espacios y ponemos todo en minúsculas para buscar mejor
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return f"Error técnico: {str(e)}"

# Cargar datos
df = load_data_pro()

st.title("🚀 Radar de Subvenciones Inteligente")
st.divider()

if isinstance(df, str):
    st.error(f"No se pudo cargar el Excel: {df}")
else:
    # --- BUSCADOR INTELIGENTE DE COLUMNAS ---
    # Buscamos la columna que se parezca a "Título"
    col_titulo = next((c for c in df.columns if 'tit' in c.lower()), None)
    col_sector = next((c for c in df.columns if 'sect' in c.lower()), None)
    col_prob = next((c for c in df.columns if 'prob' in c.lower()), None)

    # Si no encontramos la columna Título, mostramos diagnóstico
    if not col_titulo:
        st.warning("⚠️ No encuentro la columna 'Título' en tu Excel.")
        st.write("Las columnas que he detectado son estas:", list(df.columns))
        st.info("Asegúrate de que la primera fila de tu Excel tenga los nombres de las columnas.")
    else:
        # --- FILTROS ---
        st.sidebar.header("Filtros")
        
        # Filtro Sector
        if col_sector:
            opciones_sector = sorted(df[col_sector].dropna().unique().tolist())
            sel_sector = st.sidebar.multiselect("Sector", opciones_sector, default=opciones_sector)
            df = df[df[col_sector].isin(sel_sector)]
        
        # Filtro Probabilidad
        if col_prob:
            opciones_prob = sorted(df[col_prob].dropna().unique().tolist())
            sel_prob = st.sidebar.multiselect("Probabilidad", opciones_prob, default=opciones_prob)
            df = df[df[col_prob].isin(sel_prob)]

        # --- LISTADO ---
        st.subheader(f"🔍 {len(df)} subvenciones encontradas")

        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.subheader(row[col_titulo])
                    # Intentamos sacar cuantía y plazo si existen
                    cuantia = next((row[c] for c in df.columns if 'cuan' in c.lower()), "Ver BOE")
                    plazo = next((row[c] for c in df.columns if 'plaz' in c.lower()), "Ver BOE")
                    st.write(f"**💰 Cuantía:** {cuantia} | **📅 Plazo:** {plazo}")
                
                with c2:
                    if col_prob:
                        p = str(row[col_prob])
                        color = "green" if "alta" in p.lower() else "orange" if "med" in p.lower() else "gray"
                        st.markdown(f"### :{color}[{p}]")

                with st.expander("Ver análisis de la IA"):
                    # Buscamos resumen y justificacion por aproximación
                    resumen = next((row[c] for c in df.columns if 'resum' in c.lower()), "No disponible")
                    justif = next((row[c] for c in df.columns if 'just' in c.lower()), "No disponible")
                    req = next((row[c] for c in df.columns if 'requi' in c.lower()), "No disponible")
                    
                    st.write("**Resumen:**", resumen)
                    st.write("**Oportunidad:**", justif)
                    st.write("**Requisitos:**", req)
                    
                    st.divider()
                    # Buscamos la URL (columna ID)
                    url_link = row.get('ID', row.get('url_final', '#'))
                    st.link_button("🔗 Abrir en el BOE", str(url_link))

st.caption("Actualizado con n8n y Groq AI")
