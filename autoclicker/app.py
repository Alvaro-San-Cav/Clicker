"""
app.py - Autoclicker v2.0 — Interfaz Streamlit
Ejecutar: streamlit run app.py --server.port 8501
O usar launcher.py para modo ventana nativa.
"""

import os
import sys
import threading
import time
import streamlit as st
from datetime import datetime, timedelta

# ──────────────────────────────────────────
# Configuración DPI Awareness para Windows
# ──────────────────────────────────────────
if sys.platform == "win32":
    try:
        import ctypes
        # Configurar el proceso como DPI aware para coordenadas precisas del mouse
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    except Exception:
        pass

# Asegurar que el directorio raíz del proyecto sea el CWD
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

# Agregar la ruta del proyecto al PYTHONPATH si no está
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports: intentar relativos primero (cuando se ejecuta como paquete),
# si falla usar absolutos (cuando se ejecuta como script)
try:
    from .recorder import MouseRecorder
    from .scheduler import AlertManager, REPEAT_OPTIONS, REPEAT_LABELS
    from .i18n import t
except ImportError:
    from autoclicker.recorder import MouseRecorder
    from autoclicker.scheduler import AlertManager, REPEAT_OPTIONS, REPEAT_LABELS
    from autoclicker.i18n import t

# ────────────────────────────────────────────────────────────
# Configuración global y estado básico
# ────────────────────────────────────────────────────────────
RECORDINGS_DIR = os.path.join(project_root, "recordings")

def load_config():
    config_file = os.path.join(RECORDINGS_DIR, "config.json")
    default_config = {"trim_seconds": 0.0, "lang": "es", "favorites": []}
    if not os.path.exists(config_file):
        return default_config
    try:
        import json
        with open(config_file, "r") as f:
            return {**default_config, **json.load(f)}
    except Exception:
        return default_config

def save_config(config_data):
    config_file = os.path.join(RECORDINGS_DIR, "config.json")
    try:
        import json
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
    except Exception:
        pass

if "app_config" not in st.session_state:
    st.session_state.app_config = load_config()

LANG = st.session_state.app_config.get("lang", "es")

# ────────────────────────────────────────────────────────────
# Configuración de página
# ────────────────────────────────────────────────────────────
try:
    from PIL import Image
    icon_img = Image.open(os.path.join(project_root, "assets/iconoclick.ico"))
except Exception:
    icon_img = "🖱️"

st.set_page_config(
    page_title="Autoclicker",
    page_icon=icon_img,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Evitar que Chrome sugiera traducir la página y forzar idioma
st.markdown("""
<script>
    document.documentElement.lang = 'es';
</script>
<meta name="google" content="notranslate">
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────
# CSS personalizado — estilo oscuro premium
# ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Layout ultra-compacto ── */
    .block-container {
        padding: 0.4rem 0.5rem 0.2rem 0.5rem !important;
        max-width: 100% !important;
    }
    .stMarkdown, p, span, div, label, small {
        font-size: 0.72rem !important;
        line-height: 1.15 !important;
    }
    h1, h2, h3, h4 { line-height: 1.1 !important; }
    hr { margin: 0.15em 0 !important; }

    /* ── Fondo ── */
    .stApp {
        background: linear-gradient(160deg, #0b0d14 0%, #161830 50%, #1a1d2e 100%);
    }

    /* ── Header ── */
    .app-header {
        background: linear-gradient(135deg, rgba(82, 70, 201, 0.15) 0%, rgba(59, 47, 160, 0.05) 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 14px;
        border: 1px solid rgba(124, 108, 255, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    .app-header h1 {
        background: linear-gradient(to right, #ffffff, #a5a2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.6rem; margin: 0;
        font-weight: 800; line-height: 1.1;
        letter-spacing: 0.5px;
    }
    .app-header p {
        color: #8888a8; font-size: 0.85rem;
        margin: 6px 0 0 0; line-height: 1.3;
        font-weight: 500;
    }
    .app-header-icon {
        width: 48px !important; height: 48px !important; margin-right: 4px;
        filter: drop-shadow(0 0 10px rgba(124, 108, 255, 0.5));
    }
    .app-header-emoji {
        font-size: 2.8rem; margin-right: 4px;
        filter: drop-shadow(0 0 10px rgba(124, 108, 255, 0.3));
    }

    /* ── Metric cards ── */
    .metric-card {
        background: linear-gradient(145deg, #1e2235 0%, #252944 100%);
        border: 1px solid #363a5e;
        border-radius: 6px;
        padding: 0.25rem 0.3rem;
        text-align: center;
    }
    .metric-card h3 {
        color: #8b83ff; font-size: 1rem;
        margin: 0; line-height: 1;
        font-weight: 700;
    }
    .metric-card p {
        color: #7a7a9a; font-size: 0.58rem;
        margin: 2px 0 0 0;
    }

    /* ── Status badge ── */
    .status-badge {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 600;
        margin-bottom: 0.05rem;
    }
    .status-idle      { background: #2e3050; color: #8888a8; }
    .status-recording { background: linear-gradient(90deg,#ff4757,#ff6b81); color: #fff; animation: pulse 1.2s infinite; }
    .status-playing   { background: linear-gradient(90deg,#4ecca3,#38d9a9); color: #0f1117; }
    @keyframes pulse {
        0%,100% { opacity:1; box-shadow:0 0 6px rgba(255,71,87,.4); }
        50%     { opacity:.65; box-shadow:none; }
    }

    /* ── Routine rows ── */
    .routine-row {
        background: #1e2235; border: 1px solid #2e3050;
        border-radius: 5px; padding: 0.25rem 0.4rem;
        margin-bottom: 0.15rem;
        display: flex; align-items: center; justify-content: space-between;
    }
    .routine-name { color: #e8e8f0; font-weight: 600; font-size: 0.75rem; }
    .routine-meta { color: #7a7a9a; font-size: 0.6rem; }

    /* ── Ocultar chrome de Streamlit ── */
    #MainMenu, footer, .stDeployButton { display: none !important; }
    header[data-testid="stHeader"], div[data-testid="stToolbar"] { display: none !important; }

    /* ── Columnas — siempre horizontales, nunca apilar ── */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.25rem !important;
    }
    div[data-testid="stColumn"] {
        min-width: 0 !important;
    }

    /* ── Tabs (Navegación principal) ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; 
        background: rgba(20, 22, 42, 0.4);
        border-radius: 12px; 
        padding: 6px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 8px 14px;
        color: #7a7a9a;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.05);
        color: #fff;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6c63ff 0%, #4a43c8 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(108,99,255,0.3) !important;
    }
    /* Ocultar la línea azul inferior por defecto de Streamlit */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
        background-color: transparent !important;
    }

    /* ── Inputs ── */
    .stTextInput input, .stSelectbox div[data-baseweb="select"],
    .stNumberInput input, .stDateInput input, .stTimeInput input {
        min-height: 26px !important; font-size: 0.7rem;
        background: #1e2235 !important; border-color: #363a5e !important;
        color: #e8e8f0 !important;
    }

    /* ── Botones ── */
    .stButton > button {
        border-radius: 5px; font-weight: 600;
        border: none; padding: 0.15rem 0.4rem;
        font-size: 0.72rem; min-height: 28px;
        transition: all .15s ease;
        box-shadow: 0 1px 4px rgba(0,0,0,.2);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(108,99,255,.35);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#6c63ff,#5246c9) !important;
    }

    /* ── Botón INICIAR (verde) y DETENER (rojo) ── */
    /* Aplica solo cuando el marcador hermano está presente en el DOM */
    div:has(.btn-start-marker) ~ div .stButton > button,
    .btn-start-marker + div .stButton > button {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        box-shadow: 0 4px 15px rgba(46,204,113,0.4) !important;
    }
    div:has(.btn-stop-marker) ~ div .stButton > button,
    .btn-stop-marker + div .stButton > button {
        background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
        box-shadow: 0 0 15px rgba(231,76,60,0.6) !important;
    }
    
    /* Botones de lista de rutinas (alineados a la izquierda y sin fondo pesado) */
    div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
        background: transparent !important;
        box-shadow: none !important;
        border: 1px solid #363a5e !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.3rem 0.5rem !important;
        white-space: pre-wrap !important;
    }
    div[data-testid="stColumn"]:nth-of-type(1) .stButton > button:hover {
        background: #252944 !important;
        border-color: #6c63ff !important;
    }

    /* ── Expanders más compactos ── */
    .streamlit-expanderHeader { font-size: 0.72rem !important; padding: 0.2rem 0 !important; }
    details[data-testid="stExpander"] { border-color: #2e3050 !important; }

    /* ── Captions & info boxes ── */
    .stCaption, [data-testid="stCaption"] { font-size: 0.6rem !important; color: #7a7a9a !important; }
    .stAlert { padding: 0.3rem 0.5rem !important; font-size: 0.68rem !important; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Inicialización del estado
# ────────────────────────────────────────────────────────────
def get_recorder():
    if "recorder" not in st.session_state:
        st.session_state.recorder = MouseRecorder(recordings_dir=RECORDINGS_DIR)
    return st.session_state.recorder


def _on_alert_trigger(alert):
    """Callback que ejecuta la rutina asociada a una alerta."""
    rec = get_recorder()
    meta = rec.load_recording(alert.recording)
    if meta:
        speed = meta.get('default_speed', 1.0)
        rec.play_recording(speed=speed)


def get_alert_manager():
    if "alert_manager" not in st.session_state:
        alerts_file = os.path.join(RECORDINGS_DIR, "alerts.json")
        st.session_state.alert_manager = AlertManager(
            alerts_file=alerts_file,
            on_trigger=_on_alert_trigger,
        )
        st.session_state.alert_manager.start()
    return st.session_state.alert_manager


recorder = get_recorder()
alert_manager = get_alert_manager()

if "status" not in st.session_state:
    st.session_state.status = "idle"  # idle | recording | playing
if "last_msg" not in st.session_state:
    st.session_state.last_msg = ""


# ────────────────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────────────────
import base64
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""

icon_b64 = get_image_base64(os.path.join(project_root, "assets", "iconoclick.ico"))
img_html = f'<img src="data:image/png;base64,{icon_b64}" class="app-header-icon">' if icon_b64 else '<div class="app-header-emoji">🖱️</div>'

st.markdown(f"""
<div class="app-header">
    {img_html}
    <div>
        <h1>{t("header_title", LANG).replace("🖱️ ", "").replace("🖱️", "")}</h1>
        <p>{t("header_desc", LANG)}</p>
    </div>
</div>
""", unsafe_allow_html=True)


tab_auto, tab_rec, tab_routines, tab_alerts, tab_settings = st.tabs([
    t("tab_auto", LANG),
    t("tab_rec", LANG),
    t("tab_routines", LANG),
    t("tab_alerts", LANG),
    t("tab_settings", LANG)
])


# ═══════════════════════════════════════════════════════════
# TAB 0: AUTOMATIZACIONES (Favoritos)
# ═══════════════════════════════════════════════════════════
with tab_auto:
    st.markdown(t("auto_title", LANG))
    st.caption(t("auto_desc", LANG))
    
    favorites = st.session_state.app_config.get("favorites", [])
    all_recordings = recorder.list_recordings()
    
    # Filtrar favoritos que aún existen
    fav_recordings = [r for r in all_recordings if r['filename'] in favorites]
    
    if not fav_recordings:
        st.info(t("no_favorites", LANG))
    else:
        for j, fav in enumerate(fav_recordings):
            fname = fav.get('name', fav['filename'])
            fspeed = fav.get('default_speed', 1.0)
            fdur = fav.get('duration', 0)
            fdesc = fav.get('description', '')
            
            btn_text = f"▶  {fname}"
            if fdesc:
                btn_text += f"\n📝 {fdesc}"
            btn_text += f"\n⏱️ {fdur:.1f}s · ⚡ {fspeed:.1f}x"
            
            if st.button(btn_text, key=f"fav_run_{j}", use_container_width=True, type="primary"):
                m = recorder.load_recording(fav['filename'])
                if m:
                    s = m.get('default_speed', 1.0)
                    threading.Thread(
                        target=lambda: recorder.play_recording(speed=s),
                        daemon=True
                    ).start()
                    st.toast(t("msg_playing_fav", LANG, name=fname, speed=s))


# ═══════════════════════════════════════════════════════════
# TAB 1: GRABACIÓN
# ═══════════════════════════════════════════════════════════
with tab_rec:
    status = st.session_state.status
    
    # ── 1. Preparación ──
    st.markdown(t("new_routine", LANG))
    rec_name = st.text_input(t("name_label", LANG), key="new_rec_name", placeholder=t("name_placeholder", LANG), 
                             disabled=(status == "recording"))
    rec_desc = st.text_input(t("desc_label", LANG), key="new_rec_desc", placeholder=t("desc_placeholder", LANG),
                             disabled=(status == "recording"))
    
    st.write("") # Spacer

    # ── 2. Botón Principal de Grabación ──
    rec_keyboard = st.checkbox(
        "⌨️ Grabar también el teclado" if LANG == "es" else "⌨️ Record keyboard too",
        key="rec_keyboard",
        disabled=(status == "recording")
    )

    # Usamos st.html (renderizado nativo, sin iframe) para los marcadores CSS
    if status != "recording":
        st.html('<div class="btn-start-marker"></div>')
        if st.button(t("btn_start_record", LANG), use_container_width=True, type="primary"):
            recorder.start_recording(record_keyboard=rec_keyboard)
            st.session_state.status = "recording"
            st.session_state.last_msg = t("msg_recording", LANG)
            st.rerun()
    else:
        st.html('<div class="btn-stop-marker"></div>')
        if st.button(t("btn_stop_record", LANG), use_container_width=True, type="secondary"):
            recorder.stop_recording()
            
            # Recortar grabación si está configurado
            trim_secs = st.session_state.app_config.get("trim_seconds", 0.0)
            if trim_secs > 0:
                recorder.trim_last_seconds(trim_secs)

            # Auto-guardado
            name = st.session_state.new_rec_name.strip()
            desc = st.session_state.new_rec_desc.strip()
            filepath, meta = recorder.save_recording(
                name=name or None,
                description=desc,
                default_speed=1.0
            )
            
            st.session_state.status = "idle"
            if filepath:
                st.session_state.last_msg = t("msg_saved", LANG, name=meta['name'])
            else:
                st.session_state.last_msg = t("msg_no_events", LANG)
            st.rerun()

    # ── Mensajes de estado ──
    st.write("")
    if status == "playing":
        st.markdown(f'<div style="text-align:center"><span class="status-badge status-playing">{t("status_playing", LANG)}</span></div>', unsafe_allow_html=True)
        # Auto-rerun para detectar cuando termine la reproducción
        time.sleep(1)
        if st.session_state.status != "playing":
            st.rerun()
        else:
            st.rerun()
    elif status == "recording":
        st.markdown(f'<div style="text-align:center"><span class="status-badge status-recording">{t("status_recording", LANG)}</span></div>', unsafe_allow_html=True)
    
    if st.session_state.last_msg:
        st.info(st.session_state.last_msg)

    # ── 3. Resultados y Prueba ──
    if recorder.events_count > 0 and status != "recording":
        st.divider()
        st.markdown(t("last_recording", LANG))
        
        col1, col2 = st.columns(2)
        with col1:
            events_lbl = t("events", LANG)
            st.markdown(f"""<div class="metric-card">
                <h3>{recorder.events_count}</h3>
                <p>{events_lbl}</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            dur_lbl = t("duration", LANG)
            st.markdown(f"""<div class="metric-card">
                <h3>{recorder.recording_duration:.1f}s</h3>
                <p>{dur_lbl}</p>
            </div>""", unsafe_allow_html=True)
        
        st.write("")
        col_btn1, col_btn2 = st.columns([2, 3])
        with col_btn1:
            speed = st.number_input(t("speed_test", LANG), min_value=0.5, max_value=5.0, value=1.0, step=0.5, format="%.1f", key="play_speed")
        with col_btn2:
            st.write("")
            st.write("")
            if st.button(t("btn_test_play", LANG), use_container_width=True):
                st.session_state.status = "playing"
                st.session_state.last_msg = t("msg_testing", LANG, speed=speed)
                def _play(spd=speed):
                    recorder.play_recording(speed=spd)
                    st.session_state.status = "idle"
                    st.session_state.last_msg = ""
                threading.Thread(target=_play, daemon=True).start()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 2: MIS RUTINAS
# ═══════════════════════════════════════════════════════════
with tab_routines:
    st.markdown(t("routines_title", LANG))

    search = st.text_input(t("search_label", LANG), key="search_routines",
                            placeholder=t("search_placeholder", LANG))

    recordings = recorder.list_recordings()
    if search:
        search_lower = search.lower()
        recordings = [r for r in recordings
                      if search_lower in r.get('name', '').lower()
                      or search_lower in r.get('description', '').lower()]

    if not recordings:
        st.info(t("no_routines", LANG))
    else:
        st.caption(t("routines_found", LANG, count=len(recordings)))

        # Initialize session state for selected routine index
        if "edit_select_idx" not in st.session_state:
            st.session_state.edit_select_idx = 0

        # Helper to clear cached edit inputs when changing selection
        def clear_edit_inputs():
            for key in ["edit_rename", "edit_speed", "edit_desc"]:
                if key in st.session_state:
                    del st.session_state[key]

        for i, meta in enumerate(recordings):
            name = meta.get('name', meta['filename'])
            events = meta.get('events_count', 0)
            dur = meta.get('duration', 0)
            spd = meta.get('default_speed', 1.0)
            desc = meta.get('description', '')
            created = meta.get('created', '')
            try:
                created = datetime.fromisoformat(created).strftime("%d/%m/%Y %H:%M")
            except Exception:
                pass

            with st.container():
                c_info, c_fav, c_play, c_del = st.columns([5, 1, 1, 1], gap="small")
                with c_info:
                    info_parts = [f"⏱️ {dur:.1f}s", f"⚡ {spd:.1f}x"]
                    caption_str = " · ".join(info_parts)
                    
                    btn_label = f"📝 {name}\n{caption_str}"
                    if st.button(btn_label, key=f"sel_{i}", help="Edit", use_container_width=True):
                        st.session_state.edit_select_idx = i
                        clear_edit_inputs()
                        st.rerun()

                with c_fav:
                    favorites = st.session_state.app_config.setdefault("favorites", [])
                    is_fav = meta['filename'] in favorites
                    fav_icon = "⭐" if is_fav else "☆"
                    if st.button(fav_icon, key=f"fav_{i}", help=t("btn_fav", LANG), use_container_width=True):
                        if is_fav:
                            favorites.remove(meta['filename'])
                            st.toast(t("msg_fav_removed", LANG))
                        else:
                            favorites.append(meta['filename'])
                            st.toast(t("msg_fav_added", LANG))
                        save_config(st.session_state.app_config)
                        st.rerun()

                with c_play:
                    if st.button("▶", key=f"play_{i}", help=t("btn_play", LANG), use_container_width=True):
                        m = recorder.load_recording(meta['filename'])
                        if m:
                            s = m.get('default_speed', 1.0)
                            threading.Thread(
                                target=lambda: recorder.play_recording(speed=s),
                                daemon=True
                            ).start()
                            st.toast(t("msg_testing", LANG, speed=s))
                with c_del:
                    if st.button("🗑", key=f"del_{i}", help=t("btn_del", LANG), use_container_width=True):
                        recorder.delete_recording(meta['filename'])
                        st.session_state.edit_select_idx = 0
                        st.rerun()

                st.divider()

        # ── Edición rápida ──
        st.markdown(t("quick_edit", LANG))
        rec_names = [r.get('name', r['filename']) for r in recordings]
        rec_files = [r['filename'] for r in recordings]

        # Validar que el índice guardado no se salga de rango
        if st.session_state.edit_select_idx >= len(rec_names):
            st.session_state.edit_select_idx = 0

        selected_idx = st.session_state.edit_select_idx
        current_rec_name = rec_names[selected_idx]

        st.markdown(t("selected", LANG, name=current_rec_name))

        # Use columns to constrain input width
        col_ed1, col_ed2 = st.columns([2, 1])
        with col_ed1:
            new_name = st.text_input(t("rename", LANG), value=current_rec_name,
                                      key=f"edit_rename_{selected_idx}")
            new_desc = st.text_input(t("desc_label", LANG),
                                      value=recordings[selected_idx].get('description', ''),
                                      key=f"edit_desc_{selected_idx}")
            new_speed = st.number_input(t("speed", LANG), min_value=0.5, max_value=10.0,
                                         value=float(recordings[selected_idx].get('default_speed', 1.0)),
                                         step=0.5, key=f"edit_speed_{selected_idx}")

        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button(t("btn_apply", LANG), type="primary"):
                fn = rec_files[selected_idx]
                old_name = current_rec_name
                
                # Renombrar si cambió
                if new_name and new_name != old_name:
                    ok = recorder.rename_recording(fn, new_name)
                    if ok:
                        fn = f"{new_name}.json"
                        st.session_state.edit_select_idx = selected_idx
                        st.toast(t("msg_renamed", LANG, name=new_name))
                    else:
                        st.error(t("msg_rename_err", LANG))
                
                # Actualizar metadata
                recorder.update_metadata(fn, default_speed=new_speed, description=new_desc)
                st.toast(t("msg_edit_saved", LANG))
                st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 3: ALERTAS
# ═══════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown(t("alerts_title", LANG))
    st.caption(t("alerts_desc", LANG))

    # Formulario nueva alerta
    with st.expander(t("new_alert", LANG), expanded=True):
        alert_name = st.text_input(t("alert_name", LANG), key="alert_name", placeholder="Ej: Reporte Diario")
        
        recs = recorder.list_recordings()
        rec_options = [r['filename'] for r in recs]
        if rec_options:
            alert_rec = st.selectbox(t("alert_rec", LANG), rec_options, key="alert_rec")
        else:
            st.warning(t("no_routines", LANG))
            alert_rec = None

        _now_plus5 = datetime.now() + timedelta(minutes=5)
        
        ca_d1, ca_d2, ca_d3 = st.columns([4, 2, 2])
        with ca_d1:
            alert_date = st.date_input(t("alert_date", LANG), value=datetime.now().date(), key="alert_date")
        with ca_d2:
            alert_hour = st.selectbox(
                "Hora" if LANG == "es" else "Hour",
                options=list(range(24)),
                index=_now_plus5.hour,
                format_func=lambda h: f"{h:02d}h",
                key="alert_hour",
            )
        with ca_d3:
            alert_minute = st.number_input(
                "Min",
                min_value=0,
                max_value=59,
                value=_now_plus5.minute,
                step=1,
                key="alert_minute"
            )

        repeat_labels = list(REPEAT_OPTIONS.keys())
        alert_repeat = st.selectbox(t("alert_repeat", LANG), repeat_labels, key="alert_repeat")
        alert_desc = st.text_input(t("desc_label", LANG), key="alert_desc", placeholder="Opcional...")

        if st.button(t("btn_add_alert", LANG), type="primary", disabled=(not alert_rec)):
            if not alert_name:
                st.error(t("msg_alert_name_err", LANG))
            else:
                from datetime import time as dtime
                dt = datetime.combine(alert_date, dtime(int(alert_hour), int(alert_minute)))
                if dt <= datetime.now():
                    st.warning(t("msg_alert_past_err", LANG))
                else:
                    repeat_val = REPEAT_OPTIONS.get(alert_repeat, "once")
                    alert_manager.add_alert(
                        name=alert_name,
                        recording=alert_rec,
                        scheduled_dt=dt.isoformat(),
                        repeat=repeat_val,
                        description=alert_desc,
                    )
                    st.success(t("msg_alert_ok", LANG, name=alert_name, dt=dt.strftime('%d/%m/%Y %H:%M')))
                    st.rerun()

    # Lista de alertas
    st.divider()
    alerts = alert_manager.get_alerts()

    if not alerts:
        st.info(t("no_alerts", LANG))
    else:
        st.caption(f"{len(alerts)} alerta(s) configurada(s)")

        for j, alert in enumerate(alerts):
            try:
                dt_str = datetime.fromisoformat(alert.scheduled_dt).strftime("%d/%m/%Y %H:%M")
            except Exception:
                dt_str = alert.scheduled_dt

            active_icon = "✅" if alert.active else "⛔"
            repeat_lbl = REPEAT_LABELS.get(alert.repeat, alert.repeat)

            with st.container():
                ac1, ac2 = st.columns([3, 1])
                with ac1:
                    st.markdown(f"**{active_icon} {alert.name}**")
                    st.caption(f"🎯 {alert.recording} · 📅 {dt_str} · 🔄 {repeat_lbl}")
                    if alert.description:
                        st.caption(f"📝 {alert.description}")
                with ac2:
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        toggle_label = "⛔" if alert.active else "✅"
                        if st.button(toggle_label, key=f"atog_{j}", help="Activar/Desactivar", use_container_width=True):
                            alert_manager.toggle_alert(alert.id)
                            st.rerun()
                    with bc2:
                        if st.button("🗑", key=f"adel_{j}", help="Eliminar", use_container_width=True):
                            alert_manager.remove_alert(alert.id)
                            st.toast("🗑 Alerta eliminada")
                            st.rerun()
                st.divider()


# ═══════════════════════════════════════════════════════════
# TAB 4: CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════
with tab_settings:
    st.markdown(t("settings_title", LANG))

    st.markdown(t("settings_lang", LANG))
    st.caption(t("settings_lang_desc", LANG))
    
    LANG_OPTS = {"es": "🇪🇸 Español", "en": "🇬🇧 English"}
    lang_val = st.selectbox(
        "Language", 
        list(LANG_OPTS.keys()), 
        index=0 if LANG == "es" else 1,
        format_func=lambda x: LANG_OPTS[x],
        label_visibility="collapsed"
    )

    st.markdown(t("settings_trim", LANG))
    st.caption(t("settings_trim_desc", LANG))

    trim_val = st.slider(
        t("settings_trim_slider", LANG),
        min_value=0.0,
        max_value=10.0,
        value=float(st.session_state.app_config.get("trim_seconds", 0.0)),
        step=0.5,
        format="%.1f s"
    )

    if st.button(t("btn_save_config", LANG), type="primary"):
        st.session_state.app_config["trim_seconds"] = trim_val
        st.session_state.app_config["lang"] = lang_val
        save_config(st.session_state.app_config)
        st.success(t("msg_config_saved", LANG))
        st.rerun()


# ────────────────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center;color:#4a4a6a;font-size:0.55rem;margin-top:0.3rem'>"
    "Autoclicker v2 · "
    "<a href='https://github.com/Alvaro-San-Cav/Autoclicker' style='color:#6c63ff;text-decoration:none'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True
)
