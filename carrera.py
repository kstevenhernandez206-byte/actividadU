# carrera.py — Versión gamer elegante con nave sci-fi moderna y música espacial
# Requisitos: pip install streamlit streamlit-autorefresh pandas requests
# Coloca ambient.mp3 en la misma carpeta si deseas usar un archivo local.
# Música pública por defecto: https://cdn.pixabay.com/audio/2022/11/11/audio_2db585d7ad.mp3

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json
import requests

# ---------- CONFIG ----------
st.set_page_config(page_title="Carrera - Gamer Galáctico", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=700, key="auto_refresh")  # refresco visual

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")
MUSIC_FILE = os.path.join(BASE_DIR, "ambient.mp3")  # si existe, lo usará
# Música pública espacial (pixabay, free)
DEFAULT_MUSIC_URL = "https://cdn.pixabay.com/audio/2022/11/11/audio_2db585d7ad.mp3"
MUSIC_URL = os.environ.get("MUSIC_URL", DEFAULT_MUSIC_URL)

# Nave (sci-fi moderna) - PNG público
SPACESHIP_URL = "https://pngimg.com/uploads/spaceship/spaceship_PNG52.png"

# ---------- I/O helpers ----------
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"inicio": None, "jugadores": [], "players_info": {}, "organizer": None}

def save_state(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_answers():
    try:
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_answers(data):
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_answer(entry):
    answers = load_answers()
    answers.append(entry)
    save_answers(answers)

# ---------- Preguntas (8 ejemplo) ----------
questions = [
    {"q":"¿Qué define Russell y Norvig (2021) como propósito central de la inteligencia artificial?",
     "options":["Construir agentes capaces de actuar racionalmente","Generar entretenimiento digital","Sustituir totalmente al ser humano","Crear máquinas que imiten emociones humanas"],
     "correct":"Construir agentes capaces de actuar racionalmente"},
    {"q":"Según Wiener (2019), la cibernética estudia principalmente:",
     "options":["La historia de la informática","La programación de videojuegos","La economía digital","Los mecanismos de control en sistemas naturales y artificiales"],
     "correct":"Los mecanismos de control en sistemas naturales y artificiales"},
    {"q":"¿Cuál es uno de los riesgos de los sistemas cibernéticos autónomos?",
     "options":["Incremento de la creatividad humana","Reducción de costos operativos","Fallos en cascada y accesos no autorizados","Mejora en diagnósticos médicos"],
     "correct":"Fallos en cascada y accesos no autorizados"},
    {"q":"Brynjolfsson y McAfee (2016) señalan que la automatización laboral impulsa principalmente:",
     "options":["La desaparición de la comunicación digital","Incrementos en la eficiencia y productividad","La eliminación de la ética en el trabajo","La reducción de la alfabetización digital"],
     "correct":"Incrementos en la eficiencia y productividad"},
    {"q":"Un desafío ético crítico en la inteligencia artificial es:",
     "options":["La falta de creatividad en algoritmos","La ausencia de hardware avanzado","El sesgo algorítmico en la toma de decisiones","La escasez de datos disponibles"],
     "correct":"El sesgo algorítmico en la toma de decisiones"},
    {"q":"Según Jobin, Ienca y Vayena (2019), los marcos éticos internacionales coinciden en la importancia de:",
     "options":["Innovación, velocidad y competitividad","Transparencia, justicia y responsabilidad","Exclusividad, privacidad y lucro","Entretenimiento y diseño"],
     "correct":"Transparencia, justicia y responsabilidad"},
    {"q":"Castells (2013) afirma que la comunicación en red es el espacio donde se construyen:",
     "options":["Estrategias de marketing empresarial","Juegos interactivos en línea","Relaciones de poder, identidad y participación social","Programas de entretenimiento digital"],
     "correct":"Relaciones de poder, identidad y participación social"},
    {"q":"Tufekci (2015) advierte que los algoritmos de redes sociales tienden a priorizar:",
     "options":["Información científica verificada","Noticias oficiales de gobiernos","Contenidos académicos","Contenidos que generan respuestas emocionales intensas"],
     "correct":"Contenidos que generan respuestas emocionales intensas"}
]

TOTAL_QUESTIONS = len(questions)
QUESTION_TIME = 60
AUTO_CONTINUE_TIME = 20
POINTS_PER_CORRECT = 10
MAX_POINTS = POINTS_PER_CORRECT * TOTAL_QUESTIONS

# ---------- Helpers ----------
def ensure_state_keys(fs):
    fs.setdefault("inicio", None)
    fs.setdefault("jugadores", [])
    fs.setdefault("players_info", {})
    fs.setdefault("organizer", None)
    return fs

def format_seconds_to_mmss(s):
    try:
        s = int(s)
    except:
        return "—"
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"

def remote_resource_ok(url, timeout=2):
    try:
        r = requests.head(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

SPACESHIP_OK = remote_resource_ok(SPACESHIP_URL)
MUSIC_OK = remote_resource_ok(MUSIC_URL)

# ---------- CSS / Estilo gamer con fondo galáctico ----------
st.markdown(
    """
    <style>
    :root{
      --accent1: #00d0ff;
      --accent2: #9b7bff;
      --accent3: #6df0d6;
    }
    html, body, #root, .main {
      background: radial-gradient(ellipse at bottom, rgba(15,18,30,0.6) 0%, rgba(0,0,0,1) 70%), black;
      color: #e6eef8;
      min-height:100vh;
    }
    .star-field {
      position:fixed;
      inset:0;
      z-index:0;
      background:
        radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.06), transparent),
        radial-gradient(1px 1px at 70% 10%, rgba(255,255,255,0.04), transparent),
        radial-gradient(1px 1px at 80% 80%, rgba(255,255,255,0.03), transparent),
        radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.05), transparent),
        radial-gradient(1px 1px at 60% 45%, rgba(255,255,255,0.025), transparent);
      animation: twinkle 6s linear infinite;
      pointer-events:none;
      opacity:0.9;
      mix-blend-mode: screen;
    }
    @keyframes twinkle {
      0% { transform: translateY(0px) scale(1); opacity:0.9}
      50% { transform: translateY(-6px) scale(1.02); opacity:1}
      100% { transform: translateY(0px) scale(1); opacity:0.9}
    }
    .player-wrapper { max-width:900px; margin:28px auto 120px auto; position:relative; z-index:5; }
    .question-card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(109,240,214,0.06);
      padding:18px;
      border-radius:14px;
      box-shadow: 0 12px 30px rgba(16,16,30,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
      backdrop-filter: blur(4px);
      margin-bottom:12px;
    }
    .question-title { font-size:20px; font-weight:600; color:var(--accent2); margin-bottom:8px; }
    .question-text { font-size:15px; color:#dbeeff; margin-bottom:12px; }
    .btn-small {
      background: linear-gradient(90deg, rgba(0,208,255,0.12), rgba(155,123,255,0.08));
      border: 1px solid rgba(109,240,214,0.12);
      color: #e9fbff;
      padding:8px 14px;
      border-radius:10px;
      font-size:14px;
      font-weight:600;
      transition: box-shadow .18s ease, transform .08s ease;
      box-shadow: 0 6px 20px rgba(11,14,22,0.55);
    }
    .btn-small:hover { box-shadow: 0 10px 30px rgba(109,240,214,0.14); transform: translateY(-2px); }
    .stTextInput>div>div>input { border-radius:10px; padding:10px 12px; background: rgba(255,255,255,0.02); color: #eaf8ff; border: 1px solid rgba(255,255,255,0.03); }
    #bottom-car-bar {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 8px;
      z-index: 9999;
      display:flex;
      justify-content:center;
      pointer-events:none;
    }
    .bottom-inner {
      width: calc(90% - 20px);
      max-width: 980px;
      background: linear-gradient(180deg, rgba(12,14,22,0.92), rgba(8,10,14,0.88));
      padding: 8px 12px;
      border-radius: 14px;
      box-shadow: 0 12px 34px rgba(0,0,0,0.6);
      pointer-events:auto;
      border: 1px solid rgba(109,240,214,0.06);
    }
    .car-track {
      height: 40px;
      background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius:20px;
      padding:4px;
      position:relative;
      overflow:hidden;
      border: 1px solid rgba(109,240,214,0.04);
    }
    .car-fill {
      height: 32px;
      background: linear-gradient(90deg, rgba(0,208,255,0.14), rgba(155,123,255,0.12));
      border-radius: 16px;
      transition: width 0.6s cubic-bezier(.2,.9,.2,1);
      box-shadow: 0 6px 24px rgba(109,240,214,0.06), inset 0 -2px 8px rgba(0,0,0,0.35);
      filter: drop-shadow(0 8px 14px rgba(63,81,181,0.06));
    }
    .car-icon {
      position:absolute;
      top:4px;
      width:34px;
      height:34px;
      transition:left 0.6s cubic-bezier(.2,.9,.2,1);
      transform: translateX(-50%);
      display:flex; align-items:center; justify-content:center;
      filter: drop-shadow(0 6px 18px rgba(0,0,0,0.6));
    }
    .car-flag {
      position:absolute;
      right:12px;
      top:8px;
      font-size:18px;
      color:var(--accent1);
      text-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }
    .small-note { font-size:12px; color:#bcd8ff; margin-top:8px; }
    @media (max-width:760px){
      .player-wrapper { margin:18px 12px 120px 12px; }
      .car-icon { width:28px; height:28px; top:6px; }
      .car-fill { height:28px; }
    }
    </style>
    <div class="star-field"></div>
    """,
    unsafe_allow_html=True
)

# ---------- Session init ----------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "last_answer_time" not in st.session_state:
    st.session_state.last_answer_time = {}
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "music_playing" not in st.session_state:
    st.session_state.music_playing = False

# ---------- basic ops ----------
def add_player(name):
    name = name.strip()
    if not name:
        return
    fs = ensure_state_keys(load_state())
    if name not in fs["jugadores"]:
        fs["jugadores"].append(name)
    fs.setdefault("players_info", {})
    fs["players_info"].setdefault(name, {
        "points": 0,
        "aciertos": 0,
        "preg": 0,
        "fin": False,
        "tiempo": None,
        "joined": time.time()
    })
    save_state(fs)
    st.session_state.jugadores[name] = fs["players_info"][name]

def reset_all():
    save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
    save_answers([])
    st.session_state.jugadores = {}
    st.session_state.answers = []
    st.session_state.last_answer_time = {}
    st.session_state.admin_authenticated = False

# ---------- Sidebar (compacto) ----------
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")
if show_admin:
    st.sidebar.header("Administrador (compacto)")
    if not st.session_state.admin_authenticated:
        admin_user = st.sidebar.text_input("Usuario (admin)")
        admin_pass = st.sidebar.text_input("Contraseña (admin)", type="password")
        if st.sidebar.button("Iniciar sesión como admin"):
            if admin_user == "Grupo5" and admin_pass == "2025":
                st.session_state.admin_authenticated = True
                st.sidebar.success("Autenticado")
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        fs = ensure_state_keys(load_state())
        organizer = st.sidebar.text_input("Nombre del organizador:", value=fs.get("organizer") or "")
        st.sidebar.markdown("**Jugadores conectados**", unsafe_allow_html=True)
        players_list = []
        for n, info in fs.get("players_info", {}).items():
            joined = info.get("joined")
            joined_str = time.strftime("%H:%M:%S", time.localtime(joined)) if joined else "—"
            players_list.append({"Jugador": n, "Aciertos": info.get("aciertos",0), "Puntos": info.get("points",0), "Conectado": joined_str})
        if players_list:
            st.sidebar.dataframe(pd.DataFrame(players_list).sort_values("Conectado"), height=220)
        else:
            st.sidebar.info("No hay jugadores conectados")
        st.sidebar.markdown("---")
        cols = st.sidebar.columns([1,1])
        if cols[0].button("🚀 Iniciar carrera (confirmar)"):
            if not organizer.strip():
                st.sidebar.warning("Ingrese el nombre del organizador")
            else:
                fs["inicio"] = time.time()
                fs["organizer"] = organizer
                save_state(fs)
                st.sidebar.success("Carrera iniciada")
        if cols[1].button("🧹 Limpiar TODO"):
            reset_all()
            st.sidebar.success("Sistema reiniciado")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Auditoría (compacta)")
        answers = load_answers()
        if answers:
            df_a = pd.DataFrame(answers)
            if "timestamp" in df_a.columns:
                df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            sel = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")})))
            if sel != "(Todos)":
                df_a = df_a[df_a["jugador"] == sel]
            cols_a = [c for c in ["hora","jugador","pregunta_idx","selected","correct"] if c in df_a.columns]
            if cols_a:
                st.sidebar.dataframe(df_a[cols_a].sort_values(by="hora", ascending=False).reset_index(drop=True), height=200)
        else:
            st.sidebar.info("Sin registros de auditoría")

# ---------- MAIN (jugador) ----------
st.markdown("<div class='player-wrapper'>", unsafe_allow_html=True)
st.markdown("<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:8px'>", unsafe_allow_html=True)
st.markdown("<h2 style='margin:0;color:#dceeff'>Carrera - Modo Gamer Galáctico</h2>", unsafe_allow_html=True)

# Music controls
music_col1, music_col2 = st.columns([4,1])
with music_col1:
    st.markdown("<div style='font-size:12px;color:#9fbff7'>Fondo: Galaxia suave · Música ambiental espacial (pulsa ▶️)</div>", unsafe_allow_html=True)
with music_col2:
    if os.path.exists(MUSIC_FILE) or MUSIC_OK:
        def toggle_music():
            st.session_state.music_playing = not st.session_state.music_playing
        label = "⏸️" if st.session_state.music_playing else "▶️"
        if st.button(label, key="music_toggle"):
            toggle_music()
    else:
        st.markdown("<div style='font-size:12px;color:#7f9fbf'>No hay música disponible local; usa MUSIC_URL si quieres</div>", unsafe_allow_html=True)

player_name = st.text_input("Ingresa tu nombre:", key="player_name_input")
if player_name and player_name.strip():
    add_player(player_name.strip())

fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)

if inicio_global:
    tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
    pasado = int(time.time() - inicio_global)
    tiempo_restante = max(0, tiempo_total - pasado)
    st.info(f"⏳ Tiempo global restante: {format_seconds_to_mmss(tiempo_restante)}")
else:
    st.info("⏳ Esperando al organizador para iniciar la carrera...")

if not player_name or not player_name.strip():
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# cargar jugador
player = st.session_state.jugadores.get(player_name.strip())
if player is None:
    fs_try = ensure_state_keys(load_state())
    if player_name.strip() in fs_try.get("players_info", {}):
        st.session_state.jugadores[player_name.strip()] = fs_try["players_info"][player_name.strip()]
        player = st.session_state.jugadores.get(player_name.strip())
    else:
        st.warning("Registro pendiente; espera o recarga la página.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# terminado?
if player.get("fin", False):
    st.success("Has terminado la carrera. ¡Buen trabajo!")
    if player.get("tiempo") is not None:
        st.info(f"Tiempo total: {format_seconds_to_mmss(player.get('tiempo'))}")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    if not inicio_global:
        st.info("La carrera aún no ha iniciado. Espera al organizador.")
    else:
        tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
        pasado = int(time.time() - inicio_global)
        tiempo_restante = max(0, tiempo_total - pasado)
        st.info(f"⏳ Tiempo global restante: {format_seconds_to_mmss(tiempo_restante)}")

    preg_idx = player.get("preg", 0)
    if preg_idx >= TOTAL_QUESTIONS:
        player["fin"] = True
        player["tiempo"] = int(time.time() - inicio_global) if inicio_global else None
        fs_update = ensure_state_keys(load_state())
        fs_update["players_info"][player_name.strip()] = player
        save_state(fs_update)
        st.experimental_rerun()

    last_t = st.session_state.last_answer_time.get(player_name.strip(), None)
    in_continue = False
    if last_t:
        elapsed = time.time() - last_t
        if elapsed < AUTO_CONTINUE_TIME:
            in_continue = True
        else:
            st.session_state.last_answer_time[player_name.strip()] = None
            st.experimental_rerun()

    if in_continue:
        siguiente = preg_idx + 1
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)
        st.markdown("<div class='question-title'>Resultado registrado ✅</div>", unsafe_allow_html=True)
        answers = load_answers()
        last_answers = [a for a in answers if a.get("jugador")==player_name.strip()]
        if last_answers:
            last = last_answers[-1]
            if last.get("correct"):
                st.success("Respuesta correcta. +10 pts")
            else:
                st.error("Respuesta incorrecta.")
        st.write("")
        if st.button(f"Continuar → Pregunta {siguiente}", key=f"cont_{player_name}_{preg_idx}", help="Avanzar de pantalla"):
            st.session_state.last_answer_time[player_name.strip()] = None
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        qobj = questions[preg_idx]
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-title'>Pregunta #{preg_idx+1}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>{qobj['q']}</div>", unsafe_allow_html=True)
        radio_key = f"radio_{player_name.strip()}_{preg_idx}"
        try:
            selection = st.radio("", qobj["options"], key=radio_key, label_visibility="collapsed")
        except Exception:
            selection = qobj["options"][0]
        send_key = f"send_{player_name.strip()}_{preg_idx}"
        send_col1, send_col2 = st.columns([1,1])
        with send_col1:
            if st.button("Enviar respuesta", key=send_key):
                if selection not in qobj["options"]:
                    st.warning("Selecciona una opción antes de enviar.")
                else:
                    correcto = (selection == qobj["correct"])
                    append_answer({"timestamp":int(time.time()), "jugador":player_name.strip(), "pregunta_idx":preg_idx, "selected":selection, "correct":correcto})
                    if correcto:
                        player["points"] = player.get("points",0) + POINTS_PER_CORRECT
                        player["aciertos"] = player.get("aciertos",0) + 1
                    player["preg"] = player.get("preg",0) + 1
                    if player["preg"] >= TOTAL_QUESTIONS:
                        player["fin"] = True
                        player["tiempo"] = int(time.time() - inicio_global) if inicio_global else None
                    fs_save = ensure_state_keys(load_state())
                    fs_save.setdefault("players_info", {})
                    fs_save["players_info"][player_name.strip()] = player
                    if player_name.strip() not in fs_save.get("jugadores", []):
                        fs_save.setdefault("jugadores", []).append(player_name.strip())
                    save_state(fs_save)
                    st.session_state.last_answer_time[player_name.strip()] = time.time()
                    st.experimental_rerun()
        with send_col2:
            st.markdown("<div style='text-align:right'><small style='color:#9fbff7'>Puntos actuales: <strong style='color:#dff6ff'>{}</strong></small></div>".format(player.get("points",0)), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Bottom fixed single bar (nave)
# ---------------------------
display_progress = 0.0
display_label = ""
if player is not None:
    display_progress = player.get("points",0) / MAX_POINTS if MAX_POINTS>0 else 0.0
    display_label = f"{player.get('points',0)} pts — Pregunta {min(player.get('preg',0)+1, TOTAL_QUESTIONS)} / {TOTAL_QUESTIONS}"

display_percent = max(0.0, min(1.0, display_progress)) * 100

# Ajuste de tamaño: nave ocupa el tamaño de .car-icon (34px), usa object-fit
spaceship_html = f'<img src="{SPACESHIP_URL}" style="width:100%;height:100%;border-radius:6px;object-fit:contain;"/>' if SPACESHIP_OK else '<div style="font-size:20px;">🛸</div>'

bottom_html = f"""
<div id="bottom-car-bar">
  <div class="bottom-inner">
    <div style="display:flex; align-items:center; justify-content:space-between;">
      <div style="flex:1; margin-right:12px;">
        <div class="car-track">
          <div class="car-fill" style="width:{display_percent}%;"></div>
          <div class="car-icon" style="left:calc({display_percent}%); width:34px; height:34px;">
            {spaceship_html}
          </div>
          <div class="car-flag">🏁</div>
        </div>
        <div class="small-note">{display_label}</div>
      </div>
      <div style="width:160px; text-align:right;">
        <div style="font-size:12px;color:#9fbff7">Progreso</div>
      </div>
    </div>
  </div>
</div>
"""
st.markdown(bottom_html, unsafe_allow_html=True)

# ---------- Música espacial (controlada por botón; no forzamos autoplay) ----------
audio_src = ""
if os.path.exists(MUSIC_FILE):
    # usar archivo local si existe
    audio_src = f"file://{os.path.abspath(MUSIC_FILE)}"
else:
    # usar MUSIC_URL si está disponible (pixabay por defecto)
    audio_src = MUSIC_URL if MUSIC_OK else DEFAULT_MUSIC_URL

# Render audio element controlled by session_state
if audio_src:
    if st.session_state.music_playing:
        st.components.v1.html(f"""
            <audio id="bg-audio" src="{audio_src}" autoplay loop>
                Your browser does not support the audio element.
            </audio>
            <script>
            try{{ var a = document.getElementById('bg-audio'); a.volume = 0.28; a.play(); }}catch(e){{}}
            </script>
        """, height=0)
    else:
        # render paused audio element (so user can press ▶️ to toggle)
        st.components.v1.html(f"""
            <audio id="bg-audio" src="{audio_src}" loop>
                Your browser does not support the audio element.
            </audio>
            <script>
            try{{ var a = document.getElementById('bg-audio'); a.volume = 0.28; a.pause(); }}catch(e){{}}
            </script>
        """, height=0)

# ---------- FIN ----------
