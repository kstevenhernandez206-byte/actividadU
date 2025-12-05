# carrera.py — Versión completa con 8 preguntas, botón "Continuar" y barra 🛸🌕

import streamlit as st
import time
import pandas as pd
import os
import json

# ---------------------------
# Archivos persistentes
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")

def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"inicio": None, "jugadores": [], "players_info": {}, "organizer": None}

def save_state(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_answers():
    try:
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_answers(data):
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_answer(entry):
    answers = load_answers()
    answers.append(entry)
    save_answers(answers)

# ---------------------------
# Preguntas (8)
# ---------------------------
questions = [
    {
        "q": "¿Cuál es el propósito central de la inteligencia artificial según Russell y Norvig (2021)?",
        "options": [
            "Reemplazar completamente al ser humano en todas las tareas",
            "Crear sistemas que imiten emociones humanas",
            "Construir agentes capaces de actuar racionalmente en un entorno",
            "Desarrollar máquinas con conciencia propia"
        ],
        "correct": "Construir agentes capaces de actuar racionalmente en un entorno"
    },
    {
        "q": "Los sistemas cibernéticos se caracterizan principalmente por:",
        "options": [
            "Procesos de control, retroalimentación y comunicación",
            "La capacidad de almacenar grandes volúmenes de datos",
            "La sustitución de tareas humanas por robots",
            "La creación de redes sociales digitales"
        ],
        "correct": "Procesos de control, retroalimentación y comunicación"
    },
    {
        "q": "Según Brynjolfsson y McAfee (2016), uno de los principales riesgos de la automatización laboral es:",
        "options": [
            "La reducción de costos operativos",
            "El aumento de la precisión en tareas repetitivas",
            "La mejora en la calidad de los servicios",
            "El desplazamiento de empleos tradicionales"
        ],
        "correct": "El desplazamiento de empleos tradicionales"
    },
    {
        "q": "El sesgo algorítmico en la inteligencia artificial ocurre cuando:",
        "options": [
            "Los sistemas carecen de supervisión humana",
            "Los algoritmos aprenden de datos históricos con prejuicios",
            "Se utilizan demasiados recursos computacionales",
            "Los usuarios no aceptan términos de privacidad"
        ],
        "correct": "Los algoritmos aprenden de datos históricos con prejuicios"
    },
    {
        "q": "Castells (2013) afirma que en la sociedad contemporánea la comunicación en red es el espacio donde se construyen:",
        "options": [
            "Exclusivamente vínculos económicos",
            "Relaciones de poder, identidad y participación social",
            "Procesos de automatización laboral",
            "Sistemas de retroalimentación tecnológica"
        ],
        "correct": "Relaciones de poder, identidad y participación social"
    },
    {
        "q": "Tufekci (2015) sostiene que los algoritmos de redes sociales tienden a priorizar:",
        "options": [
            "Contenidos que generan mayor interacción emocional",
            "Información científica y verificada",
            "Publicaciones neutrales y objetivas",
            "Mensajes institucionales regulados"
        ],
        "correct": "Contenidos que generan mayor interacción emocional"
    },
    {
        "q": "Wardle y Derakhshan (2017) denominan al fenómeno de la desinformación digital como:",
        "options": [
            "Fake news",
            "Data bias",
            "Information disorder",
            "Digital misinformation"
        ],
        "correct": "Information disorder"
    },
    {
        "q": "Según la UNESCO (2021), para lograr una verdadera inclusión digital es necesario considerar:",
        "options": [
            "La creación de más redes sociales globales",
            "La sustitución de docentes por plataformas digitales",
            "Exclusivamente la reducción de costos tecnológicos",
            "Alfabetización tecnológica, asequibilidad, conectividad y accesibilidad"
        ],
        "correct": "Alfabetización tecnológica, asequibilidad, conectividad y accesibilidad"
    }
]

# ---------------------------
# Parámetros
# ---------------------------
QUESTION_TIME = 50  # segundos por pregunta
WAIT_TIME = 10      # segundos entre preguntas
POINTS_PER_CORRECT = 10
TOTAL_QUESTIONS = len(questions)

# ---------------------------
# Helpers
# ---------------------------
def format_seconds_to_mmss(s):
    try:
        s = int(s)
    except:
        return "—"
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"

def ensure_state_keys(fs):
    fs.setdefault("inicio", None)
    fs.setdefault("jugadores", [])
    fs.setdefault("players_info", {})
    fs.setdefault("organizer", None)
    return fs

def barra_carretera_html(progreso, width="100%"):
    porcentaje = max(0.0, min(1.0, float(progreso))) * 100
    left_percent = max(2, min(98, porcentaje))  # mantener visible el 🚀
    html = f"""
    <div style="position:relative;width:{width};height:36px;background:#222;border-radius:10px;padding:4px;overflow:hidden;">
        <div style="position:absolute;left:0;top:0;height:100%;width:{porcentaje}%;background:rgba(34,197,94,0.18);border-radius:8px;"></div>
        <div style="position:absolute;left:{left_percent}%;top:3px;font-size:22px;transform:translateX(-50%);transition:left .4s ease;">🛸</div>
        <div style="position:absolute;right:8px;top:6px;font-size:18px;">🌕</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Estado session
# ---------------------------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = {}  # {jugador_idx: True/False}
if "wait_continue" not in st.session_state:
    st.session_state.wait_continue = {}  # {jugador_idx: True/False}

# ---------------------------
# Registrar jugador
# ---------------------------
def add_player(name):
    name = name.strip()
    if not name:
        return
    fs = ensure_state_keys(load_state())
    if name not in fs["jugadores"]:
        fs["jugadores"].append(name)
    fs["players_info"].setdefault(name, {
        "points": 0,
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
    st.session_state.answers = {}
    st.session_state.show_feedback = {}
    st.session_state.wait_continue = {}

# ---------------------------
# Página
# ---------------------------
st.set_page_config(page_title="Formulario de Inteligencia Artificial y Sistemas Cibernéticos", layout="wide")
st.header("Formulario de Inteligencia Artificial y Sistemas Cibernéticos")

# ---------- Auto-refresh cada 0.5 s ----------
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=500, key="refresher")

# ---------- Admin sin checkbox ----------
st.sidebar.header("Administrador")
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

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
    fs = ensure_state_keys(load_state())

    # Organizer name
    organizer = st.sidebar.text_input("Nombre del organizador:", value=fs.get("organizer") or "")
    if st.sidebar.button("🚀 Iniciar carrera"):
        if not organizer.strip():
            st.sidebar.warning("Ingrese el nombre del organizador antes de iniciar.")
        else:
            fs["inicio"] = time.time()
            fs["organizer"] = organizer
            save_state(fs)
            st.sidebar.success("Carrera iniciada")

    # Tabla de jugadores conectados
    st.sidebar.markdown("### 👥 Jugadores conectados")
    players_list = []
    for name, info in fs.get("players_info", {}).items():
        joined_ts = info.get("joined", None)
        joined_str = time.strftime("%H:%M:%S", time.localtime(joined_ts)) if joined_ts else "—"
        players_list.append({
            "Jugador": name,
            "Puntos": info.get("points", 0),
            "Preg": info.get("preg", 0),
            "Conectado": joined_str
        })
    if players_list:
        st.sidebar.dataframe(pd.DataFrame(players_list).sort_values("Conectado"))
    else:
        st.sidebar.info("No hay jugadores conectados")

    # Auditoría
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗂 Auditoría (respuestas)")
    answers = load_answers()
    if answers:
        nombres = sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")}))
        selected = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + nombres)
        df_a = pd.DataFrame(answers)
        if "timestamp" in df_a.columns:
            df_a = df_a.copy()
            df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
        if selected != "(Todos)":
            df_a = df_a[df_a["jugador"] == selected]
        cols_to_show = ["hora","jugador","pregunta_idx","selected","correct"] if "hora" in df_a.columns else ["jugador","pregunta_idx","selected","correct"]
        st.sidebar.dataframe(df_a[cols_to_show].sort_values(by="hora", ascending=False))
        csv = df_a[cols_to_show].to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Exportar auditoría (CSV)", data=csv, file_name="auditoria.csv", mime="text/csv")
    else:
        st.sidebar.info("No hay registros de auditoría aún.")

# ---------- Main (Jugador) ----------
nombre = st.text_input("Ingresa tu nombre:", key="player_name_input")
if nombre and nombre.strip():
    add_player(nombre.strip())

fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)

# Info global
if inicio_global:
    tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
    tiempo_pasado = int(time.time() - inicio_global)
    tiempo_rest = max(0, tiempo_total - tiempo_pasado)
    st.info(f"⏳ Tiempo global restante: {tiempo_rest} s")
else:
    st.info("⏳ Esperando que el organizador inicie la carrera...")

# ------------------ Quiz principal ------------------
if nombre and nombre.strip():
    jugador = st.session_state.jugadores.get(nombre.strip())
    if jugador and not jugador.get("fin", False) and inicio_global:

        idx = jugador.get("preg", 0)
        if idx >= TOTAL_QUESTIONS:
            jugador["fin"] = True
            st.session_state.jugadores[nombre]["fin"] = True
            st.success("🏁 Has completado todas las preguntas")
        else:
            key_idx = f"{nombre}_{idx}"

            if key_idx not in st.session_state.wait_continue or not st.session_state.wait_continue[key_idx]:
                # Mostrar pregunta
                qdata = questions[idx]
                st.subheader(f"Pregunta #{idx+1}")
                st.write(qdata["q"])
                selection = st.radio("Selecciona una opción:", qdata["options"], key=f"radio_{key_idx}")

                if st.button("Enviar respuesta", key=f"submit_{key_idx}"):
                    correcto = selection == qdata["correct"]
                    entry = {
                        "timestamp": int(time.time()),
                        "jugador": nombre,
                        "pregunta_idx": idx,
                        "selected": selection,
                        "correct": correcto
                    }
                    append_answer(entry)

                    if correcto:
                        jugador["points"] += POINTS_PER_CORRECT
                        st.session_state.show_feedback[key_idx] = "✅ Correcto"
                    else:
                        st.session_state.show_feedback[key_idx] = "❌ Incorrecto"

                    st.session_state.wait_continue[key_idx] = True
                    st.session_state.jugadores[nombre] = jugador

            # Mostrar feedback y botón continuar
            if st.session_state.wait_continue.get(key_idx, False):
                st.info(st.session_state.show_feedback.get(key_idx, ""))
                if st.button("Continuar", key=f"continue_{key_idx}"):
                    jugador["preg"] += 1
                    st.session_state.jugadores[nombre] = jugador
                    st.session_state.wait_continue[key_idx] = False

        # Barra de progreso
        progreso = min(jugador.get("preg",0)/TOTAL_QUESTIONS,1.0)
        barra_carretera_html(progreso)

    elif jugador.get("fin", False):
        st.success("🏁 Has terminado la carrera")
        if jugador.get("tiempo"):
            st.info(f"Tiempo total: {format_seconds_to_mmss(jugador.get('tiempo'))}")
    else:
        st.warning("La carrera no ha iniciado aún o tiempo global finalizado")
# ------------------ Barra de progreso por puntos ------------------
