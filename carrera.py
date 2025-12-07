# carrera.py — Versión final: Mostrar feedback + botón "Continuar" inmediato
import streamlit as st
import time
import pandas as pd
import os
import json
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
ACTIVE_THRESHOLD = 6   # segundos para considerar "activo" en admin
AUTOREFRESH_MS = 500   # ms
# FEEDBACK_SECONDS removed because we show Continue immediately

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
        "last_seen": time.time()
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
      <div style="flex:1;position:relative;height:36px;background:#111;border-radius:10px;padding:4px;overflow:hidden;border:1px solid #333;">
          <div style="position:absolute;left:0;top:0;height:100%;width:{progreso*100}%;background:rgba(34,197,94,0.18);border-radius:8px;transition:width .4s ease;"></div>
          <div style="position:absolute;left:{left_percent}%;top:2px;font-size:20px;transform:translateX(-50%);transition:left .4s ease;">🛸</div>
          <div style="position:absolute;right:8px;top:6px;font-size:18px;">🌕</div>
      </div>
      <div style="min-width:120px;text-align:right;font-weight:600;color:#cfe8d8;">
        {preguntas_respondidas} / {TOTAL_QUESTIONS}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

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
# feedbacks por jugador: dict {player_name: {"last": "Correcto"/"Incorrecto", "time": ts}}
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}

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

if nombre and nombre.strip():
    nombre = nombre.strip()
    fs = load_state()
    if nombre not in fs.get("jugadores", []):
        fs.setdefault("jugadores", []).append(nombre)
    pinfo = ensure_player_structure(fs, nombre)

    # actualizar last_seen (heartbeat)
    pinfo["last_seen"] = time.time()
    fs["players_info"][nombre] = pinfo
    save_state(fs)

    inicio_global = fs.get("inicio", None)
    jugador = fs["players_info"][nombre]

    if "player_name" not in st.session_state:
        st.session_state.player_name = nombre

    # si la carrera inició, preparar show_next para el jugador según su progreso guardado
    if inicio_global and not jugador.get("fin", False):
        if not st.session_state.show_next:
            st.session_state.current_question = jugador.get("preg", 0)
            st.session_state.show_next = True
            st.session_state.selection = None

    # recalcular estado
    fs_main = load_state()
    inicio_global = fs_main.get("inicio", None)

    # -------------------------
    # Mostrar barra UNA sola vez (siempre durante la interacción del jugador)
    # -------------------------
    # usamos el número de preguntas respondidas = jugador["preg"]
    barra_progreso(jugador.get("points", 0), jugador.get("preg", 0))

    # -------------------------
    # Lógica de preguntas / feedback (submit oculta pregunta, muestra feedback y CONTINUAR)
    # -------------------------
    if inicio_global and not jugador.get("fin", False):
        idx = st.session_state.current_question
        # proteger índice
        if idx < 0:
            idx = 0
        if idx >= TOTAL_QUESTIONS:
            idx = TOTAL_QUESTIONS - 1
        qdata = questions[idx]

        # Si estamos en modo "mostrar pregunta"
        if st.session_state.show_next:
            st.subheader(f"Pregunta #{idx+1} / {TOTAL_QUESTIONS}")
            st.write(qdata["q"])
            radio_key = f"radio_{nombre}_{idx}"
            # si existe selección previa en session_state, la mantiene; si no, queda None
            st.session_state.selection = st.radio("Selecciona una opción:", qdata["options"], key=radio_key)

            submit_key = f"submit_{nombre}_{idx}"
            if st.button("Enviar respuesta", key=submit_key):
                # validar selección existente
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

                    # Guardar feedback por jugador en session_state (no bloquear)
                    st.session_state.feedbacks[nombre] = {
                        "last": "Correcto" if correcto else "Incorrecto",
                        "time": time.time()
                    }

                    # Ocultar pregunta y entrar en modo feedback (mostrar CONTINUAR inmediatamente)
                    st.session_state.show_next = False
                    # Actualizar jugador variable local para que la barra muestre puntos actualizados
                    jugador = fs_upd["players_info"][nombre]

        else:
            # Modo feedback: mostrar feedback guardado para este jugador
            fb = st.session_state.feedbacks.get(nombre, None)
            if fb:
                if fb.get("last") == "Correcto":
                    st.success("✅ Correcto (+10 pts)")
                else:
                    st.error("❌ Incorrecto")

                st.write("")  # espacio

                # Mostrar botón CONTINUAR inmediatamente
                if st.button("Continuar a la siguiente pregunta"):
                    fs_adv = load_state()
                    p = fs_adv["players_info"].get(nombre, {})
                    # sincronizar current_question con lo guardado (p['preg'] ya fue incrementada al enviar)
                    st.session_state.current_question = p.get("preg", st.session_state.current_question)
                    if not p.get("fin", False):
                        st.session_state.show_next = True
                        st.session_state.selection = None
                        # limpiar feedback
                        if nombre in st.session_state.feedbacks:
                            del st.session_state.feedbacks[nombre]
                    else:
                        st.success("Has terminado la carrera. ¡Buen trabajo!")
            else:
                # si por alguna razón no hay feedback registrado, mostramos un botón para seguir
                if st.button("Continuar a la siguiente pregunta"):
                    fs_adv = load_state()
                    p = fs_adv["players_info"].get(nombre, {})
                    st.session_state.current_question = p.get("preg", st.session_state.current_question)
                    if not p.get("fin", False):
                        st.session_state.show_next = True
                        st.session_state.selection = None

    elif nombre and jugador.get("fin", False):
        # Mostrar pantalla final (sin volver a dibujar la barra anterior)
        st.success("Has terminado la carrera. ¡Buen trabajo!")
        if jugador.get("tiempo") is not None:
            st.info(f"Tiempo total: {format_seconds_to_mmss(jugador.get('tiempo'))}")
        # No volver a llamar a barra_progreso aquí (ya se mostró arriba)

    else:
        # si aún no inició la carrera
        st.info("⏳ Esperando que el organizador inicie la carrera...")

st.caption("Nota: El panel administrador requiere iniciar sesión")
st.caption("Desarrollado por Kendall Quirós Hernández — versión final (2025)")
