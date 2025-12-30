import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import time
import re
import os
from datetime import datetime
from groq import Groq
from tavily import TavilyClient
from fpdf import FPDF

# ==============================================================================
# 0. CONFIGURACIÓN GLOBAL Y LOGO
# ==============================================================================
LOGO_FILE = "logo.png" 

st.set_page_config(
    page_title="Radar Subvenciones | TITAN X",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CSS DINÁMICO (TITAN ADAPTIVE THEME)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTACIÓN DE FUENTES */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700;800&family=Outfit:wght@300;400;700;900&display=swap');

    /* --- VARIABLES DE COLORES --- */
    :root {
        --bg-app: #f8fafc;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --accent: #06b6d4;
        --primary-btn: #3b82f6;
        --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        --metric-bg: rgba(255, 255, 255, 0.7);
        --input-bg: #ffffff;
        --urgency-color: #ef4444;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-app: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #22d3ee;
            --primary-btn: #60a5fa;
            --shadow-card: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            --metric-bg: rgba(30, 41, 59, 0.7);
            --input-bg: #1e293b;
        }
    }

    .stApp { font-family: 'Outfit', sans-serif; background-color: var(--bg-app); }
    h1, h2, h3 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; color: var(--text-primary) !important; }
    
    .titan-header {
        background: -webkit-linear-gradient(0deg, var(--primary-btn), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem; font-weight: 900; margin-bottom: 0px;
    }

    /* --- ESTILOS DE KPIS --- */
    div[data-testid="metric-container"] {
        background-color: var(--metric-bg); 
        border: 1px solid var(--card-border);
        padding: 15px 20px; 
        border-radius: 12px; 
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover { 
        border-color: var(--accent); 
        transform: translateY(-2px); 
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricValue"] { 
        font-family: 'Rajdhani', sans-serif !important; 
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, var(--accent), var(--primary-btn));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    [data-testid="stMetricLabel"] { 
        color: var(--text-secondary) !important; 
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* --- TARJETAS TITAN --- */
    .titan-card {
        background: var(--card-bg); 
        border-radius: 16px; 
        border: 1px solid var(--card-border);
        overflow: hidden; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px; 
        height: 100%; 
        box-shadow: var(--shadow-card);
        display: flex;
        flex-direction: column;
    }
    .titan-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px -5px rgba(0,0,0,0.15); border-color: var(--primary-btn); }

    /* --- CONTENEDOR DE IMAGEN --- */
    .card-img-container { 
        position: relative; 
        height: 180px; 
        width: 100%; 
        overflow: hidden;
        background-color: #0f172a; 
        border-bottom: 1px solid var(--card-border);
    }
    
    .card-img { 
        width: 100% !important; 
        height: 100% !important; 
        object-fit: cover !important; 
        object-position: center;
        display: block;
        transition: transform 0.5s ease; 
        filter: brightness(0.9); 
    }
    .titan-card:hover .card-img { transform: scale(1.1); filter: brightness(1.05); }

    .card-overlay { 
        position: absolute; bottom: 0; left: 0; right: 0; height: 100%; 
        background: linear-gradient(to top, var(--card-bg) 0%, transparent 60%); 
        pointer-events: none;
    }

    /* --- BURBUJA (BADGE) --- */
    .card-badge {
        position: absolute; 
        top: 12px; 
        right: 12px; 
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(8px); 
        -webkit-backdrop-filter: blur(8px);
        color: #ffffff !important; 
        padding: 5px 12px;
        border-radius: 8px; 
        font-size: 0.7rem; 
        font-family: 'Rajdhani', sans-serif; 
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid rgba(255, 255, 255, 0.15); 
        z-index: 20; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* --- ALERTA DE URGENCIA (NUEVO) --- */
    .urgency-badge {
        position: absolute; top: 12px; left: 12px; 
        background: rgba(239, 68, 68, 0.95);
        color: white; padding: 4px 10px; border-radius: 20px; 
        font-size: 0.65rem; font-weight: 800;
        z-index: 20; box-shadow: 0 2px 10px rgba(239, 68, 68, 0.5); 
        animation: pulse 2s infinite;
        font-family: 'Rajdhani', sans-serif;
        text-transform: uppercase;
        border: 1px solid rgba(255,255,255,0.3);
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

    .card-body { padding: 20px; position: relative; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    
    .card-title {
        color: var(--text-primary); font-weight: 800; font-size: 1.15rem; line-height: 1.3;
        margin-bottom: 12px; min-height: 3rem; display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden;
    }

    .specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--card-border); }
    .spec-item { display: flex; flex-direction: column; }
    .spec-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); font-weight: 700; }
    .spec-value { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }

    .titan-tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-right: 4px; margin-bottom: 4px; text-transform: uppercase; color: white; }
    
    .stTextInput input, .stMultiSelect div[data-baseweb="select"] { background-color: var(--input-bg) !important; border: 1px solid var(--card-border) !important; color: var(--text-primary) !important; border-radius: 8px; }
    .stExpander { border: 1px solid var(--card-border) !important; border-radius: 8px !important; background-color: var(--card-bg) !important; }
    .streamlit-expanderHeader { background-color: transparent !important; color: var(--text-primary) !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SEGURIDAD
# ==============================================================================
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True; del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align:center;'>🔒 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        with c2: st.text_input("CLAVE DE ACCESO", type="password", on_change=password_entered, key="password")
        return False
    return True

# ==============================================================================
# 4. LÓGICA Y HERRAMIENTAS
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(subset=[df.columns[1]]) 
        
        # IMPORTANTE: Para evitar que falle si la columna no existe aún
        if 'Beneficiario' not in df.columns:
            df['Beneficiario'] = 'General'
            
        return df
    except Exception as e: return None

# --- NUEVA FUNCIÓN DE URGENCIA ---
def check_urgency(fecha_str):
    """Devuelve True si faltan 7 días o menos"""
    try:
        # Intenta parsear DD/MM/AAAA
        fecha_obj = datetime.strptime(str(fecha_str).strip(), '%d/%m/%Y')
        dias_restantes = (fecha_obj - datetime.now()).days
        return dias_restantes <= 7 and dias_restantes >= -1 # Incluimos hoy y ayer por si acaso
    except:
        return False

def investigar_con_ia(titulo, link_boe):
    try:
        tavily = TavilyClient(api_key=st.secrets["tavily_key"])
        client = Groq(api_key=st.secrets["groq_key"])
        search_query = f"requisitos beneficiarios exclusiones bases reguladoras {titulo} oficial"
        busqueda = tavily.search(query=search_query, search_depth="basic", max_results=3)
        contexto = "\n".join([f"Fuente: {r['url']}\nContenido: {r['content']}" for r in busqueda['results']])
        prompt = f"""Eres un Consultor Senior. Analiza: {titulo} ({link_boe})
        CONTEXTO: {contexto}
        IMPORTANTE: NO USES FORMATO MARKDOWN. NO USES '###', NI '**', NI '####'.
        Escribe en texto plano, usando guiones para listas.
        Responde con 3 bloques:
        1. REQUISITOS TÉCNICOS OCULTOS
        2. EXCLUSIONES CLAVE
        3. ESTRATEGIA PARA GANAR
        """
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        return chat.choices[0].message.content
    except Exception as e: return f"Error en la investigación: {str(e)}"

def clean_format(text):
    if not isinstance(text, str): return str(text)
    text = re.sub(r'#{1,6}\s?', '', text) 
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) 
    text = re.sub(r'\*(.*?)\*', r'\1', text) 
    replacements = {'—': '-', '–': '-', '“': '"', '”': '"', '’': "'", '‘': "'", '€': 'EUR', '•': '-', '…': '...', '🔍': '->', '⚠️': '(!)', '💡': '(IDEA)', '✅': '(SI)'}
    for k, v in replacements.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDFReport(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, x=10, y=8, w=40) 
            except: pass
        self.set_font('Arial', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'TITAN X | INFORME DE ESTRATEGIA', 0, 1, 'R')
        self.ln(15)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf(titulo, resumen, requisitos, investigacion):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(0, 8, clean_format(titulo.upper()), align='L')
    pdf.ln(5)
    pdf.set_draw_color(6, 182, 212)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    sections = [("RESUMEN EJECUTIVO", resumen), ("REQUISITOS OFICIALES", requisitos), ("AUDITORIA ESTRATEGICA (IA)", investigacion)]
    for title, content in sections:
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, clean_format(title), ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, clean_format(content))
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def get_tag_bg(tag):
    t = tag.lower()
    if "next" in t: return "background: linear-gradient(90deg, #2563eb, #1d4ed8);"
    if "subvenc" in t: return "background: linear-gradient(90deg, #059669, #047857);"
    if "prestamo" in t: return "background: linear-gradient(90deg, #d97706, #b45309);"
    if "bonif" in t: return "background: linear-gradient(90deg, #7c3aed, #6d28d9);"
    return "background: #475569;"

# ==============================================================================
#  IMÁGENES INTELIGENTES (CON ORDEN DE PRIORIDAD CORRECTO Y ANIMALES)
# ==============================================================================
def get_img_url(sector, titulo):
    # 1. Limpieza de texto y tildes
    text_content = (str(sector) + " " + str(titulo)).lower()
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n"))
    for a, b in replacements:
        text_content = text_content.replace(a, b)
    
    base_params = "?auto=format&fit=crop&w=800&q=80"
    
    # 1. ANIMALES / PROTECTORAS (NUEVO - PRIORIDAD MÁXIMA)
    if any(x in text_content for x in ['animal', 'protectora', 'perro', 'gato', 'mascota', 'veterinari', 'fauna', 'especie']): 
        return f"https://images.unsplash.com/photo-1548767797-d8c844163c4c{base_params}"

    # 2. EMERGENCIAS / DANA
    if any(x in text_content for x in ['dana', 'catastrofe', 'emergencia', 'inundaci']): return f"https://images.unsplash.com/photo-1639164631388-857f29935861{base_params}"
    # 3. MARITIMO / NAVAL
    if any(x in text_content for x in ['maritimo', 'naval', 'barco', 'puerto', 'portuari', 'mercancia', 'transporte maritimo']): return f"https://images.unsplash.com/photo-1606185540834-d6e7483ee1a4{base_params}"
    # 4. OBRAS CIVILES
    if any(x in text_content for x in ['paviment', 'calle', 'asfalt', 'urbaniz', 'pluvial', 'saneamiento', 'alcantarillado', 'abastecimiento', 'obras de']): return f"https://images.unsplash.com/photo-1621255558983-0498b98b76c1{base_params}"
    # 5. CULTURA
    if any(x in text_content for x in ['cultur', 'patrimonio', 'historic', 'archivo', 'museo', 'arte', 'bellas artes', 'restauracion', 'bienes inmuebles']): return f"https://images.unsplash.com/photo-1544211603-99b3b8793540{base_params}"
    # 6. HIDROELÉCTRICA
    if any(x in text_content for x in ['hidro', 'repotencia', 'central', 'presa', 'agua']): return f"https://images.unsplash.com/photo-1468421201266-2a86ef21940d{base_params}"
    # 7. EÓLICA
    if any(x in text_content for x in ['eolic', 'viento', 'aerogenerador', 'wind']): return f"https://images.unsplash.com/photo-1548337138-e87d889cc369{base_params}"
    # 8. SOLAR
    if any(x in text_content for x in ['solar', 'fotov', 'placas', 'autoconsumo', 'almacenamiento', 'renovable', 'bomba de calor']): return f"https://images.unsplash.com/photo-1756913454593-ac5cab482a7a{base_params}"
    # 9. GAS
    if any(x in text_content for x in ['gas', 'combustible', 'hidrogeno', 'biogas']): return f"https://images.unsplash.com/photo-1626573867620-302324147748{base_params}"
    # 10. MOVILIDAD
    if any(x in text_content for x in ['moves', 'coche', 'vehiculo', 'puntos de recarga', 'automocion']): return f"https://images.unsplash.com/photo-1596731498067-99aeb581d3d7{base_params}"
    # 11. SALUD
    if any(x in text_content for x in ['salud', 'sanitar', 'farma', 'medic', 'hospital', 'cancer']): return f"https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7{base_params}"
    # 12. INDUSTRIA
    if any(x in text_content for x in ['indust', 'manufac', 'fabrica', 'maquina', 'cadena de valor']): return f"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158{base_params}"
    # 13. AGRO
    if any(x in text_content for x in ['agro', 'campo', 'forest', 'ganad', 'rural']): return f"https://images.unsplash.com/photo-1625246333195-78d9c38ad449{base_params}"
    # 14. TURISMO
    if any(x in text_content for x in ['turis', 'hotel', 'viaje', 'hostel']): return f"https://images.unsplash.com/photo-1551882547-ff40c63fe5fa{base_params}"
    # 15. EDUCACIÓN
    if any(x in text_content for x in ['educa', 'formaci', 'universidad', 'beca', 'lector', 'curso', 'joven', 'estudiante', 'egresado', 'asociaci']): return f"https://images.unsplash.com/photo-1524178232363-1fb2b075b655{base_params}"
    # 16. DIGITAL
    if any(x in text_content for x in ['digital', 'ia ', 'softw', 'tic', 'cyber', 'ciber', 'asesora', 'consultor', 'transformacion']): return f"https://images.unsplash.com/photo-1580894894513-541e068a3e2b{base_params}"
    # 17. CONSTRUCCIÓN
    if any(x in text_content for x in ['construc', 'vivienda', 'rehab', 'edific']): return f"https://images.unsplash.com/photo-1503387762-592deb58ef4e{base_params}"
    # 18. INNOVACIÓN
    if any(x in text_content for x in ['startup', 'emprende', 'idi', 'innovacion', 'tecnologic', 'investig', 'transferencia']): return f"https://images.unsplash.com/photo-1519389950473-47ba0277781c{base_params}"

    return f"https://images.unsplash.com/photo-1497215728101-856f4ea42174{base_params}"

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
if check_password():
    df = load_data()
    if df is not None:
        
        with st.sidebar:
            if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, use_container_width=True)
            st.markdown("### 🎛️ FILTROS")
            st.markdown("---")
            
            query = st.text_input("Búsqueda Textual", placeholder="Ej: Digitalización...", key="search_bar")
            
            # FILTRO CASCADA (SIN FALLOS)
            tipos_beneficiarios = sorted(df['Beneficiario'].astype(str).unique())
            sel_tipo = st.multiselect("Tipo de Beneficiario", tipos_beneficiarios)
            
            df_filtered_step1 = df.copy()
            if sel_tipo:
                df_filtered_step1 = df[df['Beneficiario'].isin(sel_tipo)]
            
            sectores_disponibles = sorted(df_filtered_step1.iloc[:, 5].astype(str).unique())
            sel_sector = st.multiselect("Sector Estratégico", sectores_disponibles)
            
            probs_unicas = sorted(df.iloc[:, 9].astype(str).unique())
            sel_prob = st.multiselect("Probabilidad de Éxito", probs_unicas)
            
            filtered_df = df_filtered_step1.copy()
            if query: filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
            if sel_sector: filtered_df = filtered_df[filtered_df.iloc[:, 5].astype(str).isin(sel_sector)]
            if sel_prob: filtered_df = filtered_df[filtered_df.iloc[:, 9].astype(str).isin(sel_prob)]
            
            st.markdown("---")
            st.markdown("### 📥 EXPORTAR")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar CSV", data=csv, file_name="titan_export.csv", mime="text/csv", use_container_width=True)

        c_hero1, c_hero2 = st.columns([3, 1])
        with c_hero1:
            st.markdown("<div class='titan-header'>RADAR <span style='color:var(--primary-btn)'>TITAN</span></div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:1.1rem; margin-top:-10px;'>Detección inteligente de fondos públicos.</p>", unsafe_allow_html=True)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_ops = len(filtered_df)
        high_prob = len(filtered_df[filtered_df.iloc[:, 9].astype(str).str.contains("Alta", case=False)])
        ratio = round((high_prob / total_ops * 100), 1) if total_ops > 0 else 0
        kpi1.metric("OPORTUNIDADES", total_ops, delta="Activas")
        kpi2.metric("ALTA PROBABILIDAD", high_prob, delta="Prioritarias", delta_color="normal")
        kpi3.metric("RATIO DE ÉXITO", f"{ratio}%")
        kpi4.metric("ACTUALIZACIÓN", "En Vivo")

        with st.expander("📊 ANALÍTICA DE MERCADO", expanded=False):
            if total_ops > 0:
                g1, g2 = st.columns(2)
                with g1:
                    sector_counts = filtered_df.iloc[:, 5].value_counts().reset_index()
                    sector_counts.columns = ['Sector', 'Count']
                    fig1 = px.pie(sector_counts, values='Count', names='Sector', hole=0.6, color_discrete_sequence=px.colors.sequential.Bluyl)
                    fig1.update_layout(title_text="Distribución por Sector", height=350, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    fig1.update_traces(hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>(%{percent})')
                    st.plotly_chart(fig1, use_container_width=True)
                with g2:
                    prob_counts = filtered_df.iloc[:, 9].value_counts().reset_index()
                    prob_counts.columns = ['Probabilidad', 'Count']
                    fig2 = px.bar(prob_counts, x='Probabilidad', y='Count', color='Probabilidad', color_discrete_sequence=px.colors.qualitative.Bold)
                    fig2.update_layout(title_text="Análisis de Probabilidad", height=350, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        if total_ops == 0:
            st.info("⚠️ No hay resultados que coincidan con tus filtros.")
        else:
            cols = st.columns(2)
            # --- BUCLE BLINDADO (TRY-EXCEPT) PARA QUE NO SE ROMPA LA WEB ---
            for i, (index, row) in enumerate(filtered_df.iterrows()):
                try:
                    titulo = row.iloc[1]
                    sector = row.iloc[5]
                    tags_raw = str(row.iloc[2]).split('|')
                    tags_html = "".join([f"<span class='titan-tag' style='{get_tag_bg(t.strip())}'>{t.strip()}</span>" for t in tags_raw if t.strip()])
                    cuantia = row.iloc[3]
                    plazo = row.iloc[4]
                    probabilidad = str(row.iloc[9]).strip().upper()
                    analisis_ia = row.iloc[6]
                    requisitos_txt = row.iloc[8]
                    link_boe = str(row.iloc[0])
                    img_url = get_img_url(sector, titulo)
                    
                    badge_border = "rgba(16, 185, 129, 0.5)" if "ALTA" in probabilidad else ("rgba(245, 158, 11, 0.5)" if "MEDIA" in probabilidad else "rgba(148, 163, 184, 0.5)")
                    
                    # ALERTA URGENCIA
                    is_urgent = check_urgency(plazo)
                    urgency_html = "<div class='urgency-badge'>🚨 CIERRE INMINENTE</div>" if is_urgent else ""

                    card_html = f"""
                    <div class="titan-card">
                        <div class="card-img-container">
                            <img src="{img_url}" class="card-img">
                            <div class="card-overlay"></div>
                            {urgency_html}
                            <div class="card-badge" style="border-color:{badge_border};">● {probabilidad}</div>
                        </div>
                        <div class="card-body">
                            <div>
                                <div class="card-title" title="{titulo}">{titulo}</div>
                                <div style="margin-bottom:10px;">{tags_html}</div>
                            </div>
                            <div class="specs-grid">
                                <div class="spec-item"><span class="spec-label">Cuantía Disp.</span><span class="spec-value">{cuantia}</span></div>
                                <div class="spec-item"><span class="spec-label">Cierre</span><span class="spec-value" style="{'color:#ef4444' if is_urgent else ''}">{plazo}</span></div>
                            </div>
                        </div>
                    </div>
                    """
                    with cols[i % 2]:
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        with st.expander("🔬 INVESTIGACIÓN PROFUNDA & PDF"):
                            key_investigacion = f"investigacion_{index}"
                            if key_investigacion not in st.session_state:
                                st.info("💡 Pulsa para analizar las Bases Oficiales en tiempo real.")
                                if st.button("🔍 BUSCAR BASES REALES", key=f"ai_btn_{index}", use_container_width=True):
                                    with st.spinner("⏳ TITAN AI leyendo el BOE y extrayendo datos clave..."):
                                        res_profundo = investigar_con_ia(titulo, link_boe)
                                        st.session_state[key_investigacion] = res_profundo
                                        st.rerun() 
                            else:
                                st.success("✅ Auditoría Completada")
                                st.markdown(f"<div style='font-size:0.9rem; color:#475569'>{st.session_state[key_investigacion]}</div>", unsafe_allow_html=True)
                                pdf_data = generar_pdf(titulo, analisis_ia, requisitos_txt, st.session_state[key_investigacion])
                                st.download_button(label="📥 DESCARGAR INFORME PDF OFICIAL", data=pdf_data, file_name=f"Informe_Titan_{index}.pdf", mime="application/pdf", use_container_width=True, key=f"pdf_btn_{index}")

                        with st.expander("🔻 ANÁLISIS PREVIO", expanded=False):
                            st.markdown(f"""<div style='background:var(--bg-app); padding:15px; border-radius:8px; border-left:3px solid var(--accent); color:var(--text-secondary);'>
                                <h4 style='margin-top:0; color:var(--accent); font-size:0.9rem;'>🧠 SÍNTESIS INTELIGENTE</h4>{analisis_ia}</div>""", unsafe_allow_html=True)
                            st.markdown("#### 📋 Requisitos")
                            st.caption(str(requisitos_txt)[:300] + "...") 
                            c_btn1, c_btn2 = st.columns([1,1])
                            with c_btn1: st.link_button("📄 VER BOE", link_boe, use_container_width=True)
                            with c_btn2: st.button("⭐ SEGUIR", key=f"fav_{index}", use_container_width=True)
                        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                
                except Exception as e:
                    # Si falla una fila, la ignoramos y seguimos (NO ROMPEMOS LA WEB)
                    continue
    else: st.error("DATABASE ERROR")
