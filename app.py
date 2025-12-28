import streamlit as st
import pandas as pd
import requests
import io

# ==============================================================================
# 1. CONFIGURACIÓN DEL MOTOR
# ==============================================================================
st.set_page_config(
    page_title="Radar Subvenciones | TITAN",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. CSS DINÁMICO (LA MAGIA DEL CAMBIO AUTOMÁTICO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;600;800&display=swap');

    /* --- DEFINICIÓN DE VARIABLES (EL CEREBRO DEL TEMA) --- */
    :root {
        /* VALORES POR DEFECTO (MODO CLARO - CLEAN PRO) */
        --bg-app: #f3f4f6;              /* Gris muy suave */
        --card-bg: #ffffff;             /* Blanco puro */
        --card-border: #e5e7eb;         /* Borde gris sutil */
        --text-title: #111827;          /* Casi negro */
        --text-body: #4b5563;           /* Gris oscuro */
        --accent-color: #2563eb;        /* AZUL ROYAL */
        --shadow-color: rgba(0,0,0,0.05);
        --shadow-hover: rgba(37, 99, 235, 0.15); /* Sombra azulada */
        --badge-bg: #dbeafe;
        --badge-text: #1e40af;
        --hover-transform: -5px;
        --input-bg: #ffffff;
        --filter-img: brightness(1);    /* Foto normal */
        --metric-val: #2563eb;
    }

    /* DETECCIÓN AUTOMÁTICA DE MODO OSCURO (TITAN MODE) */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-app: #050505;          /* Negro Titan */
            --card-bg: #111111;         /* Gris Carbón */
            --card-border: #333333;     /* Borde oscuro */
            --text-title: #ffffff;      /* Blanco */
            --text-body: #9ca3af;       /* Gris plata */
            --accent-color: #00f2ff;    /* CIAN NEÓN */
            --shadow-color: rgba(0,0,0,0.8);
            --shadow-hover: rgba(0, 242, 255, 0.2); /* Resplandor Cian */
            --badge-bg: rgba(0, 242, 255, 0.1);
            --badge-text: #00f2ff;
            --hover-transform: -8px;
            --input-bg: #111111;
            --filter-img: brightness(0.85); /* Un poco oscura para resaltar textos */
            --metric-val: #00f2ff;
        }
    }

    /* --- APLICACIÓN DE VARIABLES --- */
    
    .stApp {
        background-color: var(--bg-app) !important;
        color: var(--text-title) !important;
    }
    
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
        margin-bottom: 0px;
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
    .smart-card:hover .card-img { filter: brightness(1.05); }

    /* CUERPO */
    .card-body { padding: 20px; }

    /* TEXTOS */
    .card-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 18px;
        line-height: 1.4;
        color: var(--text-title);
        margin-bottom: 15px;
        min-height: 50px;
    }

    /* BADGE */
    .card-badge {
        position: absolute;
        top: 15px; 
        right: 15px;
        background: var(--badge-bg);
        color: var(--badge-text);
        border: 1px solid var(--badge-text);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        backdrop-filter: blur(4px);
    }

    /* GRID DE DATOS */
    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        border-top: 1px solid var(--card-border);
        padding-top: 15px;
        margin-top: 15px;
    }
    .data-item { text-align: center; }
    .data-label {
        font-size: 10px; 
        color: var(--text-body);
        font-weight: 700; 
        text-transform: uppercase;
    }
    .data-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px; 
        font-weight: 700;
        color: var(--accent-color);
    }

    /* TAGS */
    .tag-container { display: flex; flex-wrap: wrap; gap: 5px; }
    .smart-tag {
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        color: white; /* Los tags siempre blancos pq llevan fondo de color */
        text-transform: uppercase;
    }

    /* COMPONENTES NATIVOS ADAPTADOS */
    .stTextInput input {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--card-border) !important;
        color: var(--text-title) !important;
    }
    .stTextInput input:focus { border-color: var(--accent-color) !important; }
    
    .stExpander {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-top: none !important;
        border-radius: 0 0 16px 16px !important;
    }
    .streamlit-expanderContent p { color: var(--text-body) !important; }
    h1, h2, h3 { color: var(--text-title) !important; }
    
    /* Métrica Custom */
    [data-testid="stMetricValue"] { color: var(--metric-val) !important; font-family: 'Rajdhani', sans-serif; }
    [data-testid="stMetricLabel"] { color: var(--text-body) !important; }

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
# 4. LÓGICA & IMÁGENES
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

# Helper para color de tags
def get_tag_bg(tag):
    t = tag.lower()
    if "next" in t: return "#2563eb" # Azul Real
    if "subvenc" in t: return "#16a34a" # Verde
    if "préstamo" in t: return "#dc2626" # Rojo
    return "#4b5563" # Gris oscuro

def get_img_url(sector, titulo):
    combined = (str(sector) + " " + str(titulo)).lower()
    # Enlaces de Unsplash optimizados y temáticos
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
        # El color del título cambia con CSS var(--text-title)
        st.markdown("<h1 style='margin:0; font-size:32px;'>📡 RADAR <span style='color:var(--accent-color)'>TITAN</span></h1>", unsafe_allow_html=True)
    with c_search:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        query = st.text_input("", placeholder="🔍 Buscar oportunidad...", label_visibility="collapsed")

    st.markdown("---")
    df = load_data()

    if df is not None:
        # 1. FILTRADO
        if query: df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

        # 2. MÉTRICAS (LA GUINDA DEL PASTEL)
        c1, c2, c3 = st.columns(3)
        c1.metric("Resultados", len(df))
        c2.metric("Alta Probabilidad", len(df[df.iloc[:, 9].astype(str).str.contains("Alta", case=False)]) if len(df)>0 else 0)
        c3.metric("Filtro Activo", "Sí" if query else "No")
        st.markdown("<br>", unsafe_allow_html=True)

        # 3. CONTROL DE "SIN RESULTADOS"
        if len(df) == 0:
            st.warning("⚠️ No se encontraron subvenciones con ese criterio. Intenta otra búsqueda.")
        else:
            # 4. RENDERIZADO DE TARJETAS
            cols = st.columns(2)
            for i, row in df.iterrows():
                if pd.isna(row.iloc[1]): continue
                
                titulo = row.iloc[1]
                tags_html = "".join([f"<span class='smart-tag' style='background:{get_tag_bg(t.strip())}'>{t.strip()}</span>" for t in str(row.iloc[2]).split('|')])
                img_url = get_img_url(row.iloc[5], titulo)
                prob = str(row.iloc[9]).strip()
                
                # HTML CARD (Usa variables CSS)
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
