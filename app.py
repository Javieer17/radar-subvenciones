import streamlit as st
import pandas as pd
import requests
import io
import re
import os
from datetime import datetime
from groq import Groq
from tavily import TavilyClient
from fpdf import FPDF

# ==============================================================================
# 1. CONFIGURACIÓN Y CSS (TITAN THEME)
# ==============================================================================
st.set_page_config(page_title="Radar Subvenciones | TITAN X", page_icon="💠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700;800&family=Outfit:wght@300;400;700;900&display=swap');

:root {
    --bg-app: #f8fafc;
    --card-bg: #ffffff;
    --text-primary: #0f172a;
    --accent: #06b6d4;
    --primary-btn: #3b82f6;
}

.stApp { font-family: 'Outfit', sans-serif; background-color: var(--bg-app); }

/* TARJETAS */
.titan-card {
    background: var(--card-bg); 
    border-radius: 16px; 
    border: 1px solid #e2e8f0;
    overflow: hidden; 
    margin-bottom: 20px; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    display: flex; flex-direction: column;
}

.card-img-container { position: relative; height: 180px; width: 100%; overflow: hidden; }
.card-img { width: 100%; height: 100%; object-fit: cover; }
.card-overlay { position: absolute; bottom: 0; left: 0; right: 0; height: 100%; background: linear-gradient(to top, white 0%, transparent 60%); }

/* BADGES */
.card-badge {
    position: absolute; top: 12px; right: 12px; 
    background: rgba(15, 23, 42, 0.8); color: white; 
    padding: 5px 12px; border-radius: 8px; font-size: 0.7rem; font-weight: 800;
}

.urgency-badge {
    position: absolute; top: 12px; left: 12px; 
    background: #ef4444; color: white; 
    padding: 4px 10px; border-radius: 20px; font-size: 0.65rem; font-weight: 800;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
    animation: pulse 2s infinite;
}
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

.card-body { padding: 20px; }
.card-title { font-weight: 800; font-size: 1.15rem; margin-bottom: 10px; color: var(--text-primary); }
.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; border-top: 1px solid #e2e8f0; padding-top: 15px; }
.spec-label { font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.spec-value { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 700; }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNCIONES DE LÓGICA (AQUÍ ESTÁ LA SOLUCIÓN)
# ==============================================================================

def check_password():
    """Simple password check"""
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        pwd = st.text_input("CLAVE DE ACCESO", type="password")
        if pwd == st.secrets["password"]: st.session_state["password_correct"] = True; st.rerun()
        return False
    return True

@st.cache_data(ttl=600)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{st.secrets['sheet_id']}/export?format=csv"
        df = pd.read_csv(io.StringIO(requests.get(url).content.decode('utf-8')))
        df = df.fillna("") # Rellenar vacíos para que no falle
        return df
    except: return None

def check_urgency(texto_fecha):
    """
    ESTA ES LA FUNCIÓN CLAVE.
    Busca patrones de fecha (DD/MM/AAAA) dentro del texto.
    Si encuentra texto como 'No especificada', lo ignora y devuelve False.
    """
    try:
        texto = str(texto_fecha).strip()
        
        # Usamos Regex para buscar formato fecha: 2 digitos / 2 digitos / 4 digitos
        match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', texto)
        
        if match:
            # Si encontramos una fecha válida, la extraemos y calculamos
            fecha_str = match.group(1)
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            dias_restantes = (fecha_obj - datetime.now()).days
            
            # Es urgente si quedan 7 días o menos (y no ha pasado ayer)
            if -1 <= dias_restantes <= 7:
                return True
                
        return False # Si no es fecha o no es urgente
    except:
        return False # Ante cualquier error, no romper la web

def get_img_url(texto):
    """Devuelve imagen basada en palabras clave"""
    t = str(texto).lower()
    base = "https://images.unsplash.com/photo-"
    params = "?auto=format&fit=crop&w=800&q=80"
    
    if 'animal' in t or 'protectora' in t: return f"{base}1548767797-d8c844163c4c{params}"
    if 'maritimo' in t or 'naval' in t: return f"{base}1606185540834-d6e7483ee1a4{params}"
    if 'dana' in t or 'emergencia' in t: return f"{base}1639164631388-857f29935861{params}"
    if 'agro' in t or 'campo' in t: return f"{base}1625246333195-78d9c38ad449{params}"
    if 'digital' in t or 'tic' in t: return f"{base}1580894894513-541e068a3e2b{params}"
    
    return f"{base}1497215728101-856f4ea42174{params}" # Default

# ==============================================================================
# 3. INTERFAZ PRINCIPAL
# ==============================================================================

if check_password():
    df = load_data()
    
    if df is not None:
        # Sidebar simple
        with st.sidebar:
            st.header("Filtros")
            search = st.text_input("Buscar...")
            
            # Filtro básico
            filtered_df = df.copy()
            if search:
                filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            
            st.metric("Oportunidades", len(filtered_df))

        # Título
        st.markdown("<h1 style='color:#0f172a'>RADAR <span style='color:#3b82f6'>TITAN</span></h1>", unsafe_allow_html=True)
        st.markdown("---")

        # GRID DE TARJETAS
        cols = st.columns(2)
        
        for i, (index, row) in enumerate(filtered_df.iterrows()):
            # Bloque de seguridad: Si una fila falla, saltamos a la siguiente
            try:
                # Extracción de datos (ajusta los índices si tu excel cambia)
                link_boe = row.iloc[0]
                titulo = row.iloc[1]
                tags = str(row.iloc[2]).replace("|", " ")
                cuantia = row.iloc[3]
                plazo = str(row.iloc[4]) # Convertimos a string por seguridad
                sector = row.iloc[5]
                probabilidad = row.iloc[9]
                
                # 1. CHECK URGENCIA
                es_urgente = check_urgency(plazo)
                html_urgencia = "<div class='urgency-badge'>🚨 CIERRE INMINENTE</div>" if es_urgente else ""
                style_cierre = "color: #ef4444;" if es_urgente else ""
                
                # 2. IMAGEN
                img = get_img_url(str(titulo) + " " + str(sector))

                # 3. HTML TARJETA
                card = f"""
                <div class="titan-card">
                    <div class="card-img-container">
                        <img src="{img}" class="card-img">
                        <div class="card-overlay"></div>
                        {html_urgencia}
                        <div class="card-badge">{probabilidad}</div>
                    </div>
                    <div class="card-body">
                        <div class="card-title">{titulo}</div>
                        <div style="font-size:0.8rem; color:#64748b; margin-bottom:10px">{tags}</div>
                        <div class="specs-grid">
                            <div><div class="spec-label">Cuantía</div><div class="spec-value">{cuantia}</div></div>
                            <div><div class="spec-label">Cierre</div><div class="spec-value" style="{style_cierre}">{plazo}</div></div>
                        </div>
                    </div>
                </div>
                """
                
                with cols[i % 2]:
                    st.markdown(card, un
