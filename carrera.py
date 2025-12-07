# carrera.py — Integrado: feedback 3s + respuesta correcta + animación continuar + bloqueo multi-tab
import streamlit as st
import time
import pandas as pd
import os
import json
import secrets
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh

# ---------------------------
# Config
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")

QUESTION_TIME = 50  # segundos por pregunta (referencia)
CONTINUE_DELAY = 1
POINTS_PER_CORRECT = 10
ACTIVE_THRESHOLD = 6   # segundos para considerar "activo" en admin (y para bloqueo multi-tab)
AUTOREFRESH_MS = 500   # ms (auto-refresh)
FEEDBACK_SECONDS = 3   # segundos que se muestra el feedback antes de habilitar "Continuar"

# ---------------------------
# Preguntas
# ---------------------------
questions = [
    {"q":"¿Cuál es el propósito central de la inteligencia artificial según Russell y Norvig (2021)?",
     "options":["Reemplazar completamente al ser humano en todas las tareas",
                "Crear sistemas que imiten emociones humanas",
                "Construir agentes capaces de actuar racionalmente en un entorno",
                "Desarrollar máquinas con conciencia propia"],
     "correct":"Construir agentes capaces de actuar racionalmente en un entorno"},

    {"q":"Los sistemas cibernéticos se caracterizan principalmente por:",
     "options":["Procesos de control, retroalimentación y comunicación",
                "La capacidad de almacenar grandes volúmenes de datos",
                "La sustitución de tareas humanas por robots",
                "La creación de redes sociales digitales"],
     "correct":"Procesos de control, retroalimentación y comunicación"},

    {"q":"Según Brynjolfsson y McAfee (2016), uno de los principales riesgos de la automatización laboral es:",
     "options":["La reducción de costos operativos",
                "El aumento de la precisión en tareas repetitivas",
                "La mejora en la calidad de los servicios",
                "El desplazamiento de empleos tradicionales"],
     "correct":"El desplazamiento de empleos tradicionales"},

    {"q":"El sesgo algorítmico en la inteligencia artificial ocurre cuando:",
     "options":["Los sistemas carecen de supervisión humana",
                "Los algoritmos aprenden de datos históricos con prejuicios",
                "Se utilizan demasiados recursos computacionales",
                "Los usuarios no aceptan términos de privacidad"],
     "correct":"Los algoritmos aprenden de datos históricos con prejuicios"},

    {"q":"Castells (2013) afirma que en la sociedad contemporánea la comunicación en red es el espacio donde se construyen:",
     "options":["Exclusivamente vínculos económicos",
                "Relaciones de poder, identidad y participación social",
                "Procesos de automatización laboral",
                "Sistemas de retroalimentación tecnológica"],
     "correct":"Relaciones de poder, identidad y participación social"},

    {"q":"Tufekci (2015) sostiene que los algoritmos de redes sociales tienden a priorizar:",
     "options":["Contenidos que generan mayor interacción emocional",
                "Información científica y verificada",
                "Publicaciones neutrales y objetivas",
                "Mensajes institucionales regulados"],
     "correct":"Contenidos que generan mayor interacción emocional"},

    {"q":"Wardle y Derakhshan (2017) denominan al fenómeno de la desinformación digital como:",
     "options":["Fake news",
                "Data bias",
                "Information disorder",
                "Digital misinformation"],
     "correct":"Information disorder"},

    {"q":"Según la UNESCO (2021), para lograr una verdadera inclusión digital es necesario considerar:",
     "options":["La creación de más redes sociales globales",
                "La sustitución de docentes por plataformas digitales",
                "Exclusivamente la reducción de costos tecnológicos",
                "Alfabetización tecnológica, asequibilidad, conectividad y accesibilidad"],
     "correct":"Alfabetización tecnológica, asequibilidad, conectividad y accesibilidad"}
]
TOTAL_QUESTIONS = len(questions)

# ---------------------------
# Persistencia
# ---------------------------
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"inicio": None, "jugadores": [], "players_info": {}, "organizer": None}

def save_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error guardando state.json: {e}")

def load_answers():
    try:
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_answers(data):
    try:
        with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error guardando answers.json: {e}")

def append_answer(entry):
    answers = load_answers()
    answers.append(entry)
    save_answers(answers)

# ---------------------------
# Helpers
# ---------------------------
def ensure_player_structure(fs, name):
    fs.setdefault("players_info", {})
    pinfo = fs["players_info"].setdefault(name, {
        "points": 0,
        "aciertos": 0,
        "preg": 0,
        "fin": False,
        "tiempo": None,
        "joined": time.time(),
        "last_seen": time.time(),
        # session_token se añadirá cuando el jugador se registre
    })
    return pinfo

def format_seconds_to_mmss(s):
    try:
        s = int(s)
    except Exception:
        return "—"
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"

def barra_progreso(player_points, preguntas_respondidas):
    progreso = player_points / (POINTS_PER_CORRECT * TOTAL_QUESTIONS) if TOTAL_QUESTIONS>0 else 0
    progreso = min(1.0, max(0.0, progreso))
    left_percent = max(2, min(98, int(progreso*100)))
    # barra + contador numérico a la derecha
    html = f"""
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="flex:1;position:relative;height:40px;background:#111;border-radius:10px;padding:6px;overflow:hidden;border:1px solid #333;">
          <div style="position:absolute;left:0;top:0;height:100%;width:{progreso*100}%;background:rgba(34,197,94,0.18);border-radius:8px;transition:width .4s ease;"></div>
          <div style="position:absolute;left:{left_percent}%;top:4px;font-size:22px;transform:translateX(-50%);transition:left .4s ease;">🛸</div>
          <div style="position:absolute;right:10px;top:8px;font-size:18px;">🌕</div>
      </div>
      <div style="min-width:120px;text-align:right;font-weight:700;color:#cfe8d8;">
        {preguntas_respondidas} / {TOTAL_QUESTIONS}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Estilos / animación para botones (simple, afecta botones de Streamlit)
# ---------------------------
st.markdown(
    """
    <style>
    /* Pulso sutil para botones (continuar se verá animado) */
    .stButton>button {
      transition: transform .14s ease-in-out, box-shadow .14s ease-in-out;
      border-radius: 8px;
      padding: 8px 18px;
    }
    .stButton>button:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 10px 24px rgba(0,0,0,0.12);
    }
    /* animación de pulso (glow) */
    @keyframes pulseGlow {
      0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.35); }
      70% { box-shadow: 0 0 0 10px rgba(34,197,94,0); }
      100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }
    /* aplicamos glow al último botón en el contenedor .continue-area si existe */
    .continue-area .stButton>button {
      animation: pulseGlow 1.8s infinite;
      border: 2px solid rgba(34,197,94,0.12);
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------------------
# Inicialización
# ---------------------------
st.set_page_config(page_title="Formulario IA y Sistemas Cibernéticos", layout="wide")
st_autorefresh(interval=AUTOREFRESH_MS, key="auto_refresh")

# session_state seguros
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "show_next" not in st.session_state:
    st.session_state.show_next = False
if "selection" not in st.session_state:
    st.session_state.selection = None
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
# feedbacks por jugador: dict {player_name: {"last": "Correcto"/"Incorrecto", "time": ts, "correct_answer": ...}}
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}
if "my_token" not in st.session_state:
    st.session_state.my_token = None

# ---------------------------
# Sidebar: Admin
# ---------------------------
fs = load_state()
st.sidebar.header("Administrador")

if not st.session_state.admin_authenticated:
    admin_user = st.sidebar.text_input("Usuario (admin)")
    admin_pass = st.sidebar.text_input("Contraseña (admin)", type="password")
    if st.sidebar.button("Iniciar sesión como admin"):
        if admin_user == "Grupo5" and admin_pass == "2025":
            st.session_state.admin_authenticated = True
            st.sidebar.success("Autenticado como admin")
        else:
            st.sidebar.error("Credenciales incorrectas")
else:
    organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")

    st.sidebar.markdown("### 👥 Jugadores registrados")
    players_list = []
    for name, info in fs.get("players_info", {}).items():
        joined_ts = info.get("joined", None)
        joined_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(joined_ts)) if joined_ts else "—"
        last_seen = info.get("last_seen", 0)
        last_seen_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_seen)) if last_seen else "—"
        activo = (time.time() - last_seen) < ACTIVE_THRESHOLD
        players_list.append({
            "Jugador": name,
            "Estado": "🟢 Activo" if activo else "🔴 Desconectado",
            "Aciertos": info.get("aciertos", 0),
            "Puntos": info.get("points", 0),
            "Se unió": joined_str,
            "Última actividad": last_seen_str
        })

    if players_list:
        df_players = pd.DataFrame(players_list).sort_values(["Estado","Jugador"], ascending=[False, True])
        st.sidebar.dataframe(df_players, height=260)
        csv = df_players.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Exportar jugadores (CSV)", data=csv, file_name="jugadores.csv", mime="text/csv")
    else:
        st.sidebar.info("No hay jugadores registrados aún")

    if st.sidebar.button("🚀 Iniciar carrera (confirmar todos conectados)"):
        if not organizer.strip():
            st.sidebar.warning("Ingrese el nombre del organizador antes de iniciar.")
        else:
            fs_local = load_state()
            fs_local["inicio"] = time.time()
            fs_local["organizer"] = organizer
            save_state(fs_local)
            st.session_state.show_next = True
            st.session_state.current_question = 0
            st.session_state.selection = None
            st.sidebar.success("Carrera iniciada")

    if st.sidebar.button("🧹 Eliminar registro (RESET)"):
        save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
        save_answers([])
        st.session_state.current_question = 0
        st.session_state.show_next = False
        st.session_state.selection = None
        st.session_state.feedbacks = {}
        st.session_state.my_token = None
        st.sidebar.success("Registros eliminados")

    st.sidebar.markdown("### 🗂 Auditoría (respuestas)")
    answers = load_answers()
    if answers:
        df_a = pd.DataFrame(answers)
        if "timestamp" in df_a.columns:
            df_a = df_a.copy()
            df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
        cols = [c for c in ["hora","jugador","pregunta_idx","selected","correct"] if c in df_a.columns]
        st.sidebar.dataframe(df_a[cols].sort_values(by="hora", ascending=False).reset_index(drop=True), height=200)
        csv2 = df_a[cols].to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Exportar auditoría (CSV)", data=csv2, file_name="auditoria.csv", mime="text/csv")
    else:
        st.sidebar.info("No hay registros de auditoría aún.")

# ---------------------------
# Main: Jugador
# ---------------------------
st.header("Formulario de Inteligencia Artificial y Sistemas Cibernéticos")
nombre = st.text_input("Ingresa tu nombre para unirte:", key="player_name_input")

# Si el usuario ingresó nombre
if nombre and nombre.strip():
    nombre = nombre.strip()
    fs = load_state()

    # bloqueo multi-tab: si existe otra sesión activa para este nombre (last_seen reciente) y no coincide el token actual,
    # DENEGAR nueva sesión hasta que la anterior expire por inactividad.
    existing = fs.get("players_info", {}).get(nombre)
    now_ts = time.time()

    if existing:
        existing_token = existing.get("session_token")
        existing_last = existing.get("last_seen", 0)
        # si hay token y la última actividad es reciente y este cliente no tiene el mismo token => bloquear
        if existing_token and (now_ts - existing_last) < ACTIVE_THRESHOLD and st.session_state.get("my_token") != existing_token:
            st.warning("⚠️ Ya hay otra sesión activa con ese nombre. Espere a que termine o use otro nombre.")
            st.stop()  # detenemos para que no se muestre la UI del jugador
    # Si llegamos aquí, podemos registrar/actualizar la sesión del jugador
    # asignar token si no existe en session_state (esto distingue pestañas)
    if not st.session_state.get("my_token"):
        st.session_state.my_token = secrets.token_hex(16)  # token de sesión local

    # asegurar estructura del jugador en el JSON
    if nombre not in fs.get("jugadores", []):
        fs.setdefault("jugadores", []).append(nombre)
    pinfo = ensure_player_structure(fs, nombre)

    # registrar/actualizar token en estado persistente
    pinfo["session_token"] = st.session_state.my_token
    # actualizar last_seen (heartbeat)
    pinfo["last_seen"] = now_ts
    fs["players_info"][nombre] = pinfo
    save_state(fs)

    inicio_global = fs.get("inicio", None)
    jugador = fs["players_info"][nombre]

    # asegurar valores en st.session_state
    if "player_name" not in st.session_state:
        st.session_state.player_name = nombre

    # preparar show_next según progreso guardado
    if inicio_global and not jugador.get("fin", False):
        if not st.session_state.show_next:
            st.session_state.current_question = jugador.get("preg", 0)
            st.session_state.show_next = True
            st.session_state.selection = None

    # recalcular estado por seguridad
    fs_main = load_state()
    inicio_global = fs_main.get("inicio", None)

    # mostrar barra UNA sola vez (arriba)
    barra_progreso(jugador.get("points", 0), jugador.get("preg", 0))

    # -------------------------
    # Lógica de preguntas / feedback
    # -------------------------
    if inicio_global and not jugador.get("fin", False):
        idx = st.session_state.current_question
        # proteger índice
        if idx < 0:
            idx = 0
        if idx >= TOTAL_QUESTIONS:
            idx = TOTAL_QUESTIONS - 1
        qdata = questions[idx]

        # MODO: mostrar pregunta activa
        if st.session_state.show_next:
            st.subheader(f"Pregunta #{idx+1} / {TOTAL_QUESTIONS}")
            st.write(qdata["q"])
            radio_key = f"radio_{nombre}_{idx}"
            st.session_state.selection = st.radio("Selecciona una opción:", qdata["options"], key=radio_key)

            submit_key = f"submit_{nombre}_{idx}"
            if st.button("Enviar respuesta", key=submit_key):
                selected = st.session_state.get("selection", None)
                if selected is None:
                    st.warning("Seleccione una opción antes de enviar.")
                else:
                    correcto = (selected == qdata["correct"])
                    entry = {
                        "timestamp": int(time.time()),
                        "jugador": nombre,
                        "pregunta_idx": idx,
                        "selected": selected,
                        "correct": correcto
                    }
                    append_answer(entry)

                    # actualizar jugador local y persistir
                    fs_upd = load_state()
                    p = fs_upd["players_info"].get(nombre, {})
                    if correcto:
                        p["points"] = p.get("points", 0) + POINTS_PER_CORRECT
                        p["aciertos"] = p.get("aciertos", 0) + 1
                    # incrementar pregunta contestada
                    p["preg"] = p.get("preg", 0) + 1
                    # si terminó
                    if p["preg"] >= TOTAL_QUESTIONS:
                        p["fin"] = True
                        p["tiempo"] = int(time.time() - fs_upd.get("inicio", time.time()))
                    # guardar cambios
                    fs_upd["players_info"][nombre] = p
                    save_state(fs_upd)

                    # Guardar feedback por jugador en session_state (incluye respuesta correcta para mostrar si falla)
                    st.session_state.feedbacks[nombre] = {
                        "last": "Correcto" if correcto else "Incorrecto",
                        "time": time.time(),
                        "correct_answer": qdata["correct"]
                    }

                    # Ocultar pregunta y entrar en modo feedback con temporizador
                    st.session_state.show_next = False

        else:
            # Modo feedback: obtener feedback y calcular tiempo restante
            fb = st.session_state.feedbacks.get(nombre, None)
            if fb:
                elapsed = time.time() - fb.get("time", 0)
                remaining = max(0, FEEDBACK_SECONDS - int(elapsed))

                # Mostrar feedback principal
                if fb.get("last") == "Correcto":
                    st.success("✅ Correcto (+10 pts)")
                else:
                    st.error("❌ Incorrecto")
                    # Mostrar cuál era la respuesta correcta
                    st.info(f"Respuesta correcta: **{fb.get('correct_answer','—')}**")

                # Mostrar contador de espera (si elegiste 2/3 segundos)
                if remaining > 0:
                    st.info(f"Continuando en {remaining} s...")  # mensaje visible durante la espera
                else:
                    # Mostrar botón CONTINUAR (con efecto visual por CSS)
                    # lo ponemos dentro de un contenedor con clase 'continue-area' para aplicar pulso glow
                    container = st.container()
                    container.markdown('<div class="continue-area"></div>', unsafe_allow_html=True)
                    if container.button("Continuar a la siguiente pregunta"):
                        # Avanzar a la pregunta guardada
                        fs_adv = load_state()
                        p = fs_adv["players_info"].get(nombre, {})
                        st.session_state.current_question = p.get("preg", st.session_state.current_question)
                        if not p.get("fin", False):
                            st.session_state.show_next = True
                            st.session_state.selection = None
                        # limpiar feedback guardado
                        if nombre in st.session_state.feedbacks:
                            del st.session_state.feedbacks[nombre]

            else:
                # No hay feedback (caso raro), mostrar continuar de todos modos
                if st.button("Continuar a la siguiente pregunta"):
                    fs_adv = load_state()
                    p = fs_adv["players_info"].get(nombre, {})
                    st.session_state.current_question = p.get("preg", st.session_state.current_question)
                    if not p.get("fin", False):
                        st.session_state.show_next = True
                        st.session_state.selection = None

    elif nombre and jugador.get("fin", False):
        # Mostrar pantalla final (sin duplicar la barra arriba)
        st.success("Has terminado la carrera. ¡Buen trabajo!")
        if jugador.get("tiempo") is not None:
            st.info(f"Tiempo total: {format_seconds_to_mmss(jugador.get('tiempo'))}")
    else:
        st.info("⏳ Esperando que el organizador inicie la carrera...")

st.caption("Nota: El panel administrador requiere iniciar sesión")
st.caption("Desarrollado por Kendall Quirós Hernández — versión con mejoras (2025)")
