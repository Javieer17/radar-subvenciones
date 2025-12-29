import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import time

# ==============================================================================
# 1. CONFIGURACIÓN DEL MOTOR
# ==============================================================================
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
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Outfit:wght@300;400;700;900&display=swap');

    /* --- VARIABLES DE COLORES DINÁMICAS --- */
    :root {
        /* MODO CLARO (POR DEFECTO) */
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
    }

    /* MODO OSCURO (DETECTADO AUTOMÁTICAMENTE) */
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

    /* ESTILOS GLOBALES */
    .stApp {
        font-family: 'Outfit', sans-serif;
        background-color: var(--bg-app);
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        color: var(--text-primary) !important;
    }

    p, div, span {
        color: var(--text-secondary);
    }
    
    .titan-header {
        background: -webkit-linear-gradient(0deg, var(--primary-btn), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 0px;
    }

    /* METRIC CARDS */
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
    }
    [data-testid="stMetricValue"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700;
        color: var(--accent) !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    /* TARJETA INTELIGENTE */
    .titan-card {
        background: var(--card-bg);
        border-radius: 16px;
        border: 1px solid var(--card-border);
        overflow: hidden;
        position: relative;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
        height: 100%;
        box-shadow: var(--shadow-card);
    }
    
    .titan-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px -5px rgba(0,0,0,0.15);
        border-color: var(--primary-btn);
    }

    .card-img-container {
        position: relative;
        height: 180px;
        overflow: hidden;
    }
    
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
        filter: brightness(0.95);
    }
    
    .titan-card:hover .card-img {
        transform: scale(1.1);
        filter: brightness(1.05);
    }

    .card-overlay {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 80px;
        background: linear-gradient(to top, var(--card-bg), transparent);
    }

    .card-badge {
        position: absolute;
        top: 12px; right: 12px;
        background: var(--metric-bg);
        backdrop-filter: blur(4px);
        color: var(--text-primary);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        border: 1px solid var(--card-border);
        z-index: 10;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .card-body {
        padding: 20px;
        position: relative;
    }

    .card-title {
        color: var(--text-primary);
        font-weight: 800;
        font-size: 1.1rem;
        line-height: 1.4;
        margin-bottom: 12px;
        min-height: 3.2rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* DATA GRID */
    .specs-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid var(--card-border);
    }
    
    .spec-item { display: flex; flex-direction: column; }
    
    .spec-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-secondary);
        font-weight: 700;
    }
    
    .spec-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    /* TAGS */
    .titan-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-right: 4px;
        margin-bottom: 4px;
        text-transform: uppercase;
        color: white;
    }
    
    /* MODIFICACIONES A COMPONENTES NATIVOS DE STREAMLIT */
    .stTextInput input, .stMultiSelect div[data-baseweb="select"] {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--card-border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px;
    }
    
    .stExpander {
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
        background-color: var(--card-bg) !important;
    }
    .streamlit-expanderHeader {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }

    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SEGURIDAD
# ==============================================================================
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
        
    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align:center;'>🔒 ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            st.text_input("CLAVE DE ACCESO", type="password", on_change=password_entered, key="password")
        return False
    return True

# ==============================================================================
# 4. LÓGICA DE DATOS
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
        return df
    except Exception as e:
        return None

def get_tag_bg(tag):
    t = tag.lower()
    if "next" in t: return "background: linear-gradient(90deg, #2563eb, #1d4ed8);"
    if "subvenc" in t: return "background: linear-gradient(90deg, #059669, #047857);"
    if "prestamo" in t: return "background: linear-gradient(90deg, #d97706, #b45309);"
    if "bonif" in t: return "background: linear-gradient(90deg, #7c3aed, #6d28d9);"
    return "background: #475569;"

def get_img_url(sector, titulo):
    c = (str(sector) + " " + str(titulo)).lower()
    if any(x in c for x in ['dana', 'emergencia', 'catastrofe']): return "https://images.unsplash.com/photo-1628135804791-c0a6b490f898?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['solar', 'fotov', 'renovab']): return "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['eolic', 'viento']): return "https://images.unsplash.com/photo-1532601224476-15c79f2f7a51?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['indust', 'fabrica', 'maq']): return "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['tech', 'digital', 'ia ', 'software']): return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['agro', 'campo', 'ganad']): return "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['auto', 'movil', 'transp']): return "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=800&q=80"
    if any(x in c for x in ['invest', 'ciencia', 'idi']): return "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80"
    return "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80"

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
if check_password():
    
    df = load_data()
    
    if df is not None:
        
        # --- SIDEBAR DINÁMICA ---
        with st.sidebar:
            st.markdown("### 🎛️ FILTROS")
            st.markdown("---")
            
            query = st.text_input("Búsqueda Textual", placeholder="Ej: Digitalización...", key="search_bar")
            sectores_unicos = sorted(df.iloc[:, 5].astype(str).unique())
            probs_unicas = sorted(df.iloc[:, 9].astype(str).unique())
            sel_sector = st.multiselect("Sector Estratégico", sectores_unicos)
            sel_prob = st.multiselect("Probabilidad de Éxito", probs_unicas)
            
            filtered_df = df.copy()
            if query: filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
            if sel_sector: filtered_df = filtered_df[filtered_df.iloc[:, 5].astype(str).isin(sel_sector)]
            if sel_prob: filtered_df = filtered_df[filtered_df.iloc[:, 9].astype(str).isin(sel_prob)]
            
            st.markdown("---")
            st.markdown("### 📥 EXPORTAR")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar CSV", data=csv, file_name="titan_export.csv", mime="text/csv", use_container_width=True)

        # --- MAIN CONTENT ---
        c_hero1, c_hero2 = st.columns([3, 1])
        with c_hero1:
            st.markdown("<div class='titan-header'>RADAR <span style='color:var(--primary-btn)'>TITAN</span></div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:1.1rem; margin-top:-10px;'>Detección inteligente de fondos públicos.</p>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # --- KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_ops = len(filtered_df)
        high_prob = len(filtered_df[filtered_df.iloc[:, 9].astype(str).str.contains("Alta", case=False)])
        ratio = round((high_prob / total_ops * 100), 1) if total_ops > 0 else 0
        
        kpi1.metric("OPORTUNIDADES", total_ops, delta="Activas")
        kpi2.metric("ALTA PROBABILIDAD", high_prob, delta="Prioritarias", delta_color="normal")
        kpi3.metric("RATIO DE ÉXITO", f"{ratio}%")
        kpi4.metric("ACTUALIZACIÓN", "Hace 2 min")

        # --- GRÁFICOS (ADAPTABLES A LUZ/OSCURIDAD) ---
        with st.expander("📊 ANALÍTICA DE MERCADO", expanded=False):
            if total_ops > 0:
                g1, g2 = st.columns(2)
                with g1:
                    sector_counts = filtered_df.iloc[:, 5].value_counts().reset_index()
                    sector_counts.columns = ['Sector', 'Count']
                    fig1 = px.pie(sector_counts, values='Count', names='Sector', hole=0.6, color_discrete_sequence=px.colors.sequential.Bluyl)
                    # Eliminamos el color fijo "white" para que Streamlit controle el contraste
                    fig1.update_layout(
                        title_text="Distribución por Sector", 
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                with g2:
                    prob_counts = filtered_df.iloc[:, 9].value_counts().reset_index()
                    prob_counts.columns = ['Probabilidad', 'Count']
                    fig2 = px.bar(prob_counts, x='Probabilidad', y='Count', color='Probabilidad', color_discrete_sequence=px.colors.qualitative.Bold)
                    fig2.update_layout(
                        title_text="Análisis de Probabilidad", 
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False
                    )
                    st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # --- GRID DE TARJETAS ---
        if total_ops == 0:
            st.info("⚠️ No hay resultados que coincidan con tus filtros.")
        else:
            cols = st.columns(2)
            
            for i, (index, row) in enumerate(filtered_df.iterrows()):
                titulo = row.iloc[1]
                sector = row.iloc[5]
                tags_raw = str(row.iloc[2]).split('|')
                tags_html = "".join([f"<span class='titan-tag' style='{get_tag_bg(t.strip())}'>{t.strip()}</span>" for t in tags_raw if t.strip()])
                cuantia = row.iloc[3]
                plazo = row.iloc[4]
                probabilidad = str(row.iloc[9]).strip().upper()
                analisis_ia = row.iloc[6]
                link_boe = str(row.iloc[0])
                img_url = get_img_url(sector, titulo)
                
                badge_color = "#10b981" if "ALTA" in probabilidad else ("#f59e0b" if "MEDIA" in probabilidad else "#64748b")
                
                card_html = f"""
<div class="titan-card">
<div class="card-badge" style="border-color:{badge_color}; color:{badge_color}">● {probabilidad}</div>
<div class="card-img-container">
<img src="{img_url}" class="card-img">
<div class="card-overlay"></div>
</div>
<div class="card-body">
<div class="card-title" title="{titulo}">{titulo}</div>
<div style="margin-bottom:10px;">{tags_html}</div>
<div class="specs-grid">
<div class="spec-item">
<span class="spec-label">Cuantía Disp.</span>
<span class="spec-value">{cuantia}</span>
</div>
<div class="spec-item">
<span class="spec-label">Cierre</span>
<span class="spec-value">{plazo}</span>
</div>
</div>
</div>
</div>
"""
                with cols[i % 2]:
                    st.markdown(card_html, unsafe_allow_html=True)
                    with st.expander("🔻 ANÁLISIS IA", expanded=False):
                        # Caja de análisis dinámica (usa variables CSS)
                        st.markdown(f"""
                        <div style='background:var(--bg-app); padding:15px; border-radius:8px; border-left:3px solid var(--accent); color:var(--text-secondary);'>
                            <h4 style='margin-top:0; color:var(--accent); font-size:0.9rem;'>🧠 SÍNTESIS INTELIGENTE</h4>
                            {analisis_ia}
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("#### 📋 Requisitos")
                        st.caption(str(row.iloc[8])[:300] + "...") 
                        st.markdown("<br>", unsafe_allow_html=True)
                        c_btn1, c_btn2 = st.columns([1,1])
                        with c_btn1: st.link_button("📄 VER BOE", link_boe, use_container_width=True)
                        with c_btn2: st.button("⭐ SEGUIR", key=f"fav_{index}", use_container_width=True)
                    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    else: st.error("DATABASE ERROR")
