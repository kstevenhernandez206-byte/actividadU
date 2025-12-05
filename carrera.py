# carrera.py — Versión FINAL DEFINITIVA
# - Autorefresh 0.5s SIEMPRE
# - 8 preguntas, 60s por pregunta
# - Termina al responder 8 preguntas (NO por puntos)
# - Barra del carro por usuario
# - Botón "Continuar → Pregunta X", con avance automático a los 20s
# - Admin oculto con auditoría filtrable
# - Jugador no ve tiempo global si ya terminó
# - Requiere: pip install streamlit-autorefresh

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json

# =========================
# Auto-refresh
# =========================
st.set_page_config(page_title="Carrera", layout="wide")
st_autorefresh(interval=500, key="auto_refresh")   # 0.5s refresh

# =========================
# Archivos persistentes
# =========================
BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")

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

# =========================
# Preguntas (8)
# =========================
questions = [
    {
        "q": "¿Qué define Russell y Norvig (2021) como propósito central de la inteligencia artificial?",
        "options": [
            "Construir agentes capaces de actuar racionalmente",
            "Generar entretenimiento digital",
            "Sustituir totalmente al ser humano",
            "Crear máquinas que imiten emociones humanas"
        ],
        "correct": "Construir agentes capaces de actuar racionalmente"
    },
    {
        "q": "Según Wiener (2019), la cibernética estudia principalmente:",
        "options": [
            "La historia de la informática",
            "La programación de videojuegos",
            "La economía digital",
            "Los mecanismos de control en sistemas naturales y artificiales"
        ],
        "correct": "Los mecanismos de control en sistemas naturales y artificiales"
    },
    {
        "q": "¿Cuál es uno de los riesgos de los sistemas cibernéticos autónomos?",
        "options": [
            "Incremento de la creatividad humana",
            "Reducción de costos operativos",
            "Fallos en cascada y accesos no autorizados",
            "Mejora en diagnósticos médicos"
        ],
        "correct": "Fallos en cascada y accesos no autorizados"
    },
    {
        "q": "Brynjolfsson y McAfee (2016) señalan que la automatización laboral impulsa principalmente:",
        "options": [
            "La desaparición de la comunicación digital",
            "Incrementos en la eficiencia y productividad",
            "La eliminación de la ética en el trabajo",
            "La reducción de la alfabetización digital"
        ],
        "correct": "Incrementos en la eficiencia y productividad"
    },
    {
        "q": "Un desafío ético crítico en la inteligencia artificial es:",
        "options": [
            "La falta de creatividad en algoritmos",
            "La ausencia de hardware avanzado",
            "El sesgo algorítmico en la toma de decisiones",
            "La escasez de datos disponibles"
        ],
        "correct": "El sesgo algorítmico en la toma de decisiones"
    },
    {
        "q": "Según Jobin, Ienca y Vayena (2019), los marcos éticos internacionales coinciden en la importancia de:",
        "options": [
            "Innovación, velocidad y competitividad",
            "Transparencia, justicia y responsabilidad",
            "Exclusividad, privacidad y lucro",
            "Entretenimiento y diseño"
        ],
        "correct": "Transparencia, justicia y responsabilidad"
    },
    {
        "q": "Castells (2013) afirma que la comunicación en red es el espacio donde se construyen:",
        "options": [
            "Estrategias de marketing empresarial",
            "Juegos interactivos en línea",
            "Relaciones de poder, identidad y participación social",
            "Programas de entretenimiento digital"
        ],
        "correct": "Relaciones de poder, identidad y participación social"
    },
    {
        "q": "Tufekci (2015) advierte que los algoritmos de redes sociales tienden a priorizar:",
        "options": [
            "Información científica verificada",
            "Noticias oficiales de gobiernos",
            "Contenidos académicos",
            "Contenidos que generan respuestas emocionales intensas"
        ],
        "correct": "Contenidos que generan respuestas emocionales intensas"
    }
]

QUESTION_TIME = 60       # tiempo por pregunta
AUTO_CONTINUE_TIME = 20 # tiempo para avanzar si no presiona continuar

# =========================
# Utilidades
# =========================
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

def barra_carretera_html(progreso):
    """Barra individual por jugador (más pequeña y separada)."""
    porcentaje = max(0.0, min(1.0, progreso)) * 100
    left = max(3, min(97, porcentaje))
    html = f"""
    <div style="margin-top:15px;margin-bottom:25px;">
        <div style="position:relative;width:100%;height:28px;background:#222;
                    border-radius:10px;padding:3px;overflow:hidden;">
            <div style="position:absolute;left:0;top:0;height:100%;
                        width:{porcentaje}%;background:rgba(34,197,94,0.25);
                        border-radius:10px;"></div>

            <div style="position:absolute;left:{left}%;top:2px;
                        font-size:20px;transform:translateX(-50%);
                        transition:left .35s ease;">🚗</div>

            <div style="position:absolute;right:6px;top:4px;font-size:16px;">🏁</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================
# Estado local
# =========================
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}

if "answers" not in st.session_state:
    st.session_state.answers = load_answers()

# almacenar timestamp de respuesta para control de botón continuar
if "last_answer_time" not in st.session_state:
    st.session_state.last_answer_time = {}

# =========================
# Funciones principales
# =========================
def add_player(name):
    name = name.strip()
    if not name:
        return
    fs = ensure_state_keys(load_state())

    if name not in fs["jugadores"]:
        fs["jugadores"].append(name)

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

# =========================
# Sidebar: Admin oculto
# =========================
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")

if show_admin:
    st.sidebar.header("Administrador")

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        u = st.sidebar.text_input("Usuario (admin)")
        p = st.sidebar.text_input("Contraseña (admin)", type="password")
        if st.sidebar.button("Ingresar"):
            if u == "Grupo5" and p == "2025":
                st.session_state.admin_authenticated = True
                st.sidebar.success("Acceso concedido")
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        fs = ensure_state_keys(load_state())

        org = st.sidebar.text_input("Organizador:", value=fs.get("organizer") or "")

        st.sidebar.markdown("### Jugadores conectados")
        players_list = []
        for name, info in fs["players_info"].items():
            players_list.append({
                "Jugador": name,
                "Aciertos": info.get("aciertos", 0),
                "Puntos": info.get("points", 0),
                "Conectado": time.strftime("%H:%M:%S", time.localtime(info.get("joined", 0)))
            })
        if players_list:
            st.sidebar.dataframe(pd.DataFrame(players_list), height=220)
        else:
            st.sidebar.info("No hay jugadores conectados aún.")

        st.sidebar.markdown("---")
        if st.sidebar.button("🚀 Iniciar carrera"):
            fs["inicio"] = time.time()
            fs["organizer"] = org
            save_state(fs)
            st.sidebar.success("Carrera iniciada")

        if st.sidebar.button("🧹 Limpiar TODO"):
            reset_all()
            st.sidebar.success("Sistema reiniciado")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### Auditoría")
        answers = load_answers()

        if answers:
            df_a = pd.DataFrame(answers)
            df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%H:%M:%S")

            jugadores_a = sorted(df_a["jugador"].unique())
            sel = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + jugadores_a)

            if sel != "(Todos)":
                df_a = df_a[df_a["jugador"] == sel]

            st.sidebar.dataframe(df_a[["hora", "jugador", "pregunta_idx", "selected", "correct"]], height=220)
        else:
            st.sidebar.info("Sin registros.")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏆 Top 3 global")

        ranking = []
        for n, info in fs["players_info"].items():
            ranking.append({
                "Jugador": n,
                "Puntos": info.get("points", 0),
                "Aciertos": info.get("aciertos", 0),
                "Tiempo_raw": info.get("tiempo")
            })

        if ranking:
            df_r = pd.DataFrame(ranking)
            df_r = df_r.sort_values(
                by=["Puntos", "Tiempo_raw"],
                ascending=[False, True],
                key=lambda col: col.map(lambda x: x if isinstance(x, (int, float)) else 999999)
            )
            df_r["Tiempo"] = df_r["Tiempo_raw"].apply(lambda t: format_seconds_to_mmss(t) if t else "—")
            st.sidebar.table(df_r[["Jugador", "Puntos", "Aciertos", "Tiempo"]].head(3))

            st.sidebar.markdown("### 🌍 Progreso global")
            for row in df_r.itertuples():
                progreso = (row.Puntos / 80)  # 8 preguntas → 80 pts máx
                st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
                barra_carretera_html(progreso)

# =========================
# Main del jugador
# =========================
st.header("Jugador")

nombre = st.text_input("Ingresa tu nombre:")

if nombre and nombre.strip():
    add_player(nombre.strip())

fs = ensure_state_keys(load_state())
inicio = fs.get("inicio")
player = st.session_state.jugadores.get(nombre.strip()) if nombre else None

# Tiempo global
if inicio:
    tiempo_pasado = int(time.time() - inicio)
    tiempo_rest = max(0, 60 * len(questions) - tiempo_pasado)
else:
    tiempo_rest = None

if player:
    # --------------------------
    # Si ya terminó
    # --------------------------
    if player.get("fin"):
        st.success("Has terminado la carrera. ¡Buen trabajo!")

        if player.get("tiempo"):
            st.info(f"Tiempo total: {format_seconds_to_mmss(player['tiempo'])}")

        # No mostrar tiempo global (opción A)
    else:
        # ------------------------------------
        # Carrera aún no iniciada
        # ------------------------------------
        if not inicio:
            st.info("⏳ Esperando al organizador...")
        else:
            st.info(f"⏳ Tiempo global restante: {tiempo_rest}s")

            # ======================================
            # Mostrar pregunta o pantalla de siguiente
            # ======================================
            preg_idx = player["preg"]

            # TERMINA SI YA RESPONDIÓ LAS 8
            if preg_idx >= 8:
                player["fin"] = True
                player["tiempo"] = int(time.time() - inicio)
                fs["players_info"][nombre.strip()] = player
                save_state(fs)
                st.experimental_rerun()

            # Si el jugador acaba de responder y está esperando "Continuar"
            last_t = st.session_state.last_answer_time.get(nombre, None)
            if last_t and time.time() - last_t < AUTO_CONTINUE_TIME:
                # Mostrar pantalla intermedia
                siguiente = preg_idx + 1
                if st.button(f"Continuar → Pregunta {siguiente}"):
                    st.session_state.last_answer_time[nombre] = None
                    st.experimental_rerun()

                # Si pasan 20s, avanzar solo
                if time.time() - last_t >= AUTO_CONTINUE_TIME:
                    st.session_state.last_answer_time[nombre] = None
                    st.experimental_rerun()

                # Mostrar barra de progreso SOLO de este jugador
                progreso = player["points"] / 80
                barra_carretera_html(progreso)

                st.stop()

            # =====================
            # Mostrar pregunta
            # =====================
            q = questions[preg_idx]
            st.subheader(f"Pregunta #{preg_idx+1}")
            st.write(q["q"])

            sel = st.radio("Selecciona una opción:", q["options"], key=f"opt_{preg_idx}")

            if st.button("Enviar respuesta", key=f"send_{preg_idx}"):
                correcto = (sel == q["correct"])

                append_answer({
                    "timestamp": int(time.time()),
                    "jugador": nombre,
                    "pregunta_idx": preg_idx,
                    "selected": sel,
                    "correct": correcto
                })

                if correcto:
                    st.success("¡Correcto! +10 pts")
                    player["points"] += 10
                    player["aciertos"] += 1
                else:
                    st.error("Incorrecto")

                player["preg"] += 1

                fs["players_info"][nombre] = player
                save_state(fs)

                st.session_state.last_answer_time[nombre] = time.time()
                st.experimental_rerun()

            # ---------------------------
            # Mostrar barra SOLO del jugador
            # ---------------------------
            progreso = player["points"] / 80   # 8 preguntas → 80 pts máx
            barra_carretera_html(progreso)

# Mensaje final
st.caption("El panel administrador está oculto. Actívelo desde la barra lateral para administrar la carrera.")
