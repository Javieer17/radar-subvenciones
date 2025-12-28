import streamlit as st
import pandas as pd
import requests
import io

# ==============================================================================
# 1. CONFIGURACIÓN DEL MOTOR
# ==============================================================================
st.set_page_config(
    page_title="Radar Subvenciones | TITAN FILTER",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. CSS DINÁMICO (CHAMELEON + BOLD)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTAMOS FUENTES MÁS GRUESAS (800, 900) */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Inter:wght@500;700;900&display=swap');

    :root {
        /* MODO CLARO (CLEAN PRO) */
        --bg-app: #f3f4f6;
        --card-bg: #ffffff;
        --card-border: #e5e7eb;
        --text-title: #111827;
        --text-body: #374151;
        --accent-color: #2563eb;
        --shadow-color: rgba(0,0,0,0.05);
        --shadow-hover: rgba(37, 99, 235, 0.15);
        --badge-bg: #dbeafe;
        --badge-text: #1e40af;
        --hover-transform: -5px;
        --input-bg: #ffffff;
        --filter-img: brightness(1);
        --metric-val: #2563eb;
    }

    /* MODO OSCURO (TITAN MODE) */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-app: #050505;
            --card-bg: #111111;
            --card-border: #333333;
            --text-title: #ffffff;
            --text-body: #9ca3af;
            --accent-color: #00f2ff;
            --shadow-color: rgba(0,0,0,0.8);
            --shadow-hover: rgba(0, 242, 255, 0.2);
            --badge-bg: rgba(0, 242, 255, 0.1);
            --badge-text: #00f2ff;
            --hover-transform: -8px;
            --input-bg: #111111;
            --filter-img: brightness(0.85);
            --metric-val: #00f2ff;
        }
    }

    .stApp { background-color: var(--bg-app) !important; color: var(--text-title) !important; }
    .block-container { padding-top: 2rem !important; }

    /* TARJETA DINÁMICA */
    .smart-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        overflow: hidden;
        position: relative;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 6px -1px var(--shadow-color);
    }
    .smart-card:hover {
        transform: translateY(var(--hover-transform));
        border-color: var(--accent-color);
        box-shadow: 0 10px 30px -5px var(--shadow-hover);
        z-index: 2;
    }

    /* IMAGEN */
    .card-img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-bottom: 1px solid var(--card-border);
        filter: var(--filter-img);
        transition: 0.3s;
    }
    .smart-card:hover .card-img { filter: brightness(1.1); }

    /* CUERPO */
    .card-body { padding: 20px; }

    /* TEXTOS (AHORA EN NEGRITA EXTREMA) */
    .card-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900 !important; /* NEGRITA MÁXIMA */
        font-size: 19px;
        line-height: 1.3;
        color: var(--text-title);
        margin-bottom: 15px;
        min-height: 50px;
    }

    /* BADGE */
    .card-badge {
        position: absolute; top: 15px; right: 15px;
        background: var(--badge-bg); color: var(--badge-text);
        border: 1px solid var(--badge-text);
        padding: 5px 12px; border-radius: 20px;
        font-size: 11px; font-weight: 800;
        backdrop-filter: blur(4px);
    }

    /* DATA GRID */
    .data-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
        border-top: 1px solid var(--card-border); padding-top: 15px; margin-top: 15px;
    }
    .data-item { text-align: center; }
    .data-label {
        font-size: 10px; color: var(--text-body);
        font-weight: 800; text-transform: uppercase; letter-spacing: 1px;
    }
    .data-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 19px; font-weight: 800; /* NEGRITA */
        color: var(--accent-color);
    }

    /* TAGS */
    .tag-container { display: flex; flex-wrap: wrap; gap: 6px; }
    .smart-tag {
        font-size: 10px; font-weight: 800; padding: 4px 10px;
        border-radius: 6px; color: white; text-transform: uppercase;
    }

    /* INPUTS & FILTROS */
    .stTextInput input, .stMultiSelect div {
        background-color: var(--input-bg) !important;
        border-color: var(--card-border) !important;
        color: var(--text-title) !important;
    }
    
    .stExpander {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        margin-bottom: 20px !important;
    }
    .streamlit-expanderContent p { color: var(--text-body) !important; }
    h1, h2, h3 { color: var(--text-title) !important; }
    [data-testid="stMetricValue"] { color: var(--metric-val) !important; font-family: 'Rajdhani', sans-serif; font-weight: 800; }
    [data-testid="stMetricLabel"] { color: var(--text-body) !important; font-weight: 700; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
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
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br><h1 style='text-align:center;'>🔐 SECURITY CHECK</h1>", unsafe_allow_html=True)
            st.text_input("PASSWORD", type="password", on_change=password_entered, key="password")
        return False
    return True

# ==============================================================================
# 4. LÓGICA Y DATOS
# ==============================================================================
@st.cache_data(ttl=60)
def load_data():
    try:
        sid = st.secrets["sheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        r = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

def get_tag_bg(tag):
    t = tag.lower()
    if "next" in t: return "#2563eb"
    if "subvenc" in t: return "#16a34a"
    if "prestamo" in t: return "#dc2626"
    return "#4b5563"

def get_img_url(sector, titulo):
    combined = (str(sector) + " " + str(titulo)).lower()
    if any(x in combined for x in ['dana', 'social', 'ayuda']): return "https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['solar', 'energ']): return "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['eolic', 'viento']): return "https://images.unsplash.com/photo-1466611653911-954ff21b6724?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['indus', 'fabrica']): return "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['tech', 'digital', 'tic']): return "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['agro', 'campo']): return "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['coche', 'transporte']): return "https://images.unsplash.com/photo-1553265027-99d530167b28?auto=format&fit=crop&w=800&q=80"
    elif any(x in combined for x in ['univ', 'educacion']): return "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80"
    else: return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
if check_password():
    
    c_head, c_search = st.columns([1, 1])
    with c_head:
        st.markdown("<h1 style='margin:0; font-size:32px;'>📡 RADAR <span style='color:var(--accent-color)'>TITAN</span></h1>", unsafe_allow_html=True)
    with c_search:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        query = st.text_input("", placeholder="🔍 Buscar oportunidad...", label_visibility="collapsed")

    df = load_data()

    if df is not None:
        
        # --- NUEVO: SISTEMA DE FILTRADO AVANZADO ---
        with st.expander("⚙️ FILTROS AVANZADOS (SECTOR / PROBABILIDAD)", expanded=False):
            fc1, fc2 = st.columns(2)
            
            # Obtener valores únicos para los desplegables
            sectores_unicos = sorted(df.iloc[:, 5].astype(str).unique())
            probs_unicas = sorted(df.iloc[:, 9].astype(str).unique())
            
            with fc1:
                filtro_sector = st.multiselect("Filtrar por Sector:", sectores_unicos)
            with fc2:
                filtro_prob = st.multiselect("Filtrar por Probabilidad:", probs_unicas)

        st.markdown("---")

        # --- LÓGICA DE FILTRADO ---
        # 1. Filtro Texto
        if query: 
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
        # 2. Filtro Sector
        if filtro_sector:
            df = df[df.iloc[:, 5].astype(str).isin(filtro_sector)]
        # 3. Filtro Probabilidad
        if filtro_prob:
            df = df[df.iloc[:, 9].astype(str).isin(filtro_prob)]

        # --- MÉTRICAS ---
        c1, c2, c3 = st.columns(3)
        c1.metric("Resultados", len(df))
        c2.metric("Alta Probabilidad", len(df[df.iloc[:, 9].astype(str).str.contains("Alta", case=False)]) if len(df)>0 else 0)
        c3.metric("Filtros Activos", "Sí" if (query or filtro_sector or filtro_prob) else "No")
        st.markdown("<br>", unsafe_allow_html=True)

        if len(df) == 0:
            st.warning("⚠️ No hay resultados. Ajusta los filtros.")
        else:
            cols = st.columns(2)
            for i, row in df.iterrows():
                if pd.isna(row.iloc[1]): continue
                
                titulo = row.iloc[1]
                tags_html = "".join([f"<span class='smart-tag' style='background:{get_tag_bg(t.strip())}'>{t.strip()}</span>" for t in str(row.iloc[2]).split('|')])
                img_url = get_img_url(row.iloc[5], titulo)
                prob = str(row.iloc[9]).strip()
                
                html_card = f"""
                <div class="smart-card">
                    <div class="card-badge">● {prob.upper()}</div>
                    <img src="{img_url}" class="card-img">
                    <div class="card-body">
                        <div class="card-title">{titulo}</div>
                        <div class="tag-container">{tags_html}</div>
                        <div class="data-grid">
                            <div class="data-item">
                                <div class="data-label">Cuantía</div>
                                <div class="data-value">{row.iloc[3]}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Plazo</div>
                                <div class="data-value">{row.iloc[4]}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                
                with cols[i % 2]:
                    st.markdown(html_card, unsafe_allow_html=True)
                    with st.expander("🔻 ESTRATEGIA Y DETALLES"):
                        st.markdown("#### 🧠 Análisis IA")
                        st.write(row.iloc[6])
                        st.markdown("#### 📜 Requisitos")
                        st.write(row.iloc[8])
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.link_button("🔗 ACCEDER AL BOE", str(row.iloc[0]), use_container_width=True)
                    st.write("") 
    else: st.error("DATABASE ERROR")
