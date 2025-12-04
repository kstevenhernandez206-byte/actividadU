# carrera.py — Versión final (12 preguntas) — Opción C corregida
# Panel Admin: controles, lista conectados, Top 3 y progreso global
# Jugador: preguntas + progreso + tiempo
# Tiempo se muestra solo cuando el jugador termina

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
# 12 PREGUNTAS
# ---------------------------
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
        "q": "Las redes sociales funcionan como sistemas cibernéticos porque:",
        "options": [
            "Sustituyen totalmente la interacción presencial",
            "Garantizan siempre información verificada",
            "Son espacios de ocio digital",
            "Operan mediante retroalimentación entre usuarios, algoritmos e información"
        ],
        "correct": "Operan mediante retroalimentación entre usuarios, algoritmos e información"
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
    },
    {
        "q": "Wardle y Derakhshan (2017) denominan al fenómeno de la desinformación digital como:",
        "options": [
            "Fake news",
            "Crisis comunicacional",
            "Infoxicación",
            "Manipulación informativa"
        ],
        "correct": "Fake news"
    },
    {
        "q": "La UNESCO (2021) señala que la brecha digital afecta principalmente a:",
        "options": [
            "Adultos mayores, comunidades rurales y personas en pobreza",
            "Empresas multinacionales",
            "Estudiantes universitarios de ciencias sociales",
            "Comunidades urbanas con alto acceso tecnológico"
        ],
        "correct": "Adultos mayores, comunidades rurales y personas en pobreza"
    },
    {
        "q": "Una estrategia clave para reducir la vulnerabilidad frente a la desinformación es:",
        "options": [
            "Aumentar la velocidad de internet",
            "Crear más plataformas de entretenimiento",
            "Reducir el acceso a dispositivos móviles",
            "Promover programas educativos de pensamiento crítico"
        ],
        "correct": "Promover programas educativos de pensamiento crítico"
    }
]

QUESTION_TIME = 20
POINTS_PER_CORRECT = 10
POINTS_TO_FINISH = 50

# ---------------------------
# Estado en session
# ---------------------------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}

# ---------------------------
# Registrar jugador
# ---------------------------
def add_player(name):
    name = name.strip()
    if not name:
        return
    fs = load_state()
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

# ---------------------------
# Reset total
# ---------------------------
def reset_all():
    save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
    save_answers([])
    st.session_state.jugadores = {}

# ---------------------------
# Barra de progreso HTML
# ---------------------------
def barra_carretera_html(p):
    porcentaje = max(0, min(1, p)) * 100
    coche = porcentaje
    html = f"""
    <div style="position:relative;width:100%;height:36px;background:#2b2b2b;border-radius:10px;padding:4px;">
        <div style="position:absolute;height:100%;width:{porcentaje}%;background:rgba(34,197,94,0.3);border-radius:8px;"></div>
        <div style="position:absolute;left:{coche}%;top:4px;font-size:22px;transform:translateX(-50%);">🚗</div>
        <div style="position:absolute;right:6px;top:6px;">🏁</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Configuración
# ---------------------------
st.set_page_config(page_title="Carrera", layout="wide")
st.title("🏁 Carrera en vivo")

# ---------------------------
# PANEL ADMIN
# ---------------------------
st.sidebar.header("🔐 Administrador")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    u = st.sidebar.text_input("Usuario")
    p = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if u == "Grupo5" and p == "2025":
            st.session_state.admin_authenticated = True
            st.sidebar.success("Acceso concedido")
        else:
            st.sidebar.error("Incorrecto")
else:
    fs = load_state()

    organizer = st.sidebar.text_input("Nombre del organizador:", value=fs.get("organizer") or "")

    st.sidebar.subheader("👥 Jugadores conectados")
    tabla_admin = []
    for name, info in fs["players_info"].items():
        tabla_admin.append({
            "Jugador": name,
            "Aciertos": info["aciertos"],
            "Puntos": info["points"],
            "Conectado": time.strftime("%H:%M:%S", time.localtime(info["joined"]))
        })

    if tabla_admin:
        df_admin = pd.DataFrame(tabla_admin)
        st.sidebar.dataframe(df_admin, height=230)
    else:
        st.sidebar.info("Sin jugadores")

    if st.sidebar.button("🚀 Iniciar carrera"):
        if not organizer.strip():
            st.sidebar.warning("Debe ingresar organizador")
        else:
            fs["inicio"] = time.time()
            fs["organizer"] = organizer
            save_state(fs)
            st.sidebar.success("Carrera iniciada")

    if st.sidebar.button("🧹 Limpiar todo"):
        reset_all()
        st.sidebar.success("Sistema limpiado")

    st.sidebar.markdown("## 🏆 Top 3")
    ranking = []
    fs2 = load_state()
    for n, info in fs2.get("players_info", {}).items():
        t = info.get("tiempo", None)
        ranking.append({
            "Jugador": n,
            "Puntos": info["points"],
            "Aciertos": info["aciertos"],
            "Tiempo": t if t is not None else "—"
        })

    if ranking:
        df_r = pd.DataFrame(ranking)

        df_r = df_r.sort_values(
            by=["Puntos", "Tiempo"],
            ascending=[False, True],
            key=lambda c: c.map(lambda x: x if isinstance(x, int) else 999999)
        )

        st.sidebar.table(df_r.head(3))

        st.sidebar.markdown("## 🌍 Progreso global")
        for row in df_r.itertuples():
            st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
            p = min(row.Puntos / 50, 1)
            barra_carretera_html(p)

# ---------------------------
# PANEL JUGADOR
# ---------------------------
st.subheader("Jugador")
nombre = st.text_input("Ingresa tu nombre:")

if nombre:
    add_player(nombre)

fs_main = load_state()
inicio = fs_main.get("inicio")

if inicio:
    tiempo_rest = max(0, QUESTION_TIME * len(questions) - int(time.time() - inicio))
    st.info(f"⏳ Tiempo restante: {tiempo_rest}s")
else:
    st.info("Esperando al organizador...")

if nombre and nombre in st.session_state.jugadores:
    jugador = st.session_state.jugadores[nombre]

    if inicio and tiempo_rest > 0 and not jugador["fin"]:
        idx = jugador["preg"] % len(questions)
        q = questions[idx]

        st.markdown(f"### Pregunta {idx+1}")
        st.write(q["q"])

        r = st.radio("Elige:", q["options"], key=f"{nombre}_{idx}")

        if st.button("Enviar", key=f"btn_{nombre}_{idx}"):
            correcto = r == q["correct"]
            append_answer({
                "timestamp": int(time.time()),
                "jugador": nombre,
                "pregunta": idx,
                "respuesta": r,
                "correct": correcto
            })
            if correcto:
                st.success("Correcto +10 pts")
                jugador["points"] += 10
                jugador["aciertos"] += 1
            else:
                st.error("Incorrecto")

            jugador["preg"] += 1

            if jugador["points"] >= 50:
                jugador["fin"] = True
                jugador["tiempo"] = int(time.time() - inicio)
                st.balloons()
                st.success("🏁 ¡Meta alcanzada!")

            fs_p = load_state()
            fs_p["players_info"][nombre] = jugador
            save_state(fs_p)

    st.markdown("### 🚗 Tu progreso")
    p_local = min(jugador["points"] / 50, 1)
    barra_carretera_html(p_local)

# ---------------------------
# RANKING GENERAL - Zona principal
# ---------------------------
st.markdown("---")
st.markdown("## 🏆 Top 3 global")

ranking2 = []
fs_end = load_state()

for n, info in fs_end.get("players_info", {}).items():
    ranking2.append({
        "Jugador": n,
        "Puntos": info["points"],
        "Aciertos": info["aciertos"],
        "Tiempo": info["tiempo"] if info["tiempo"] is not None else "—"
    })

if ranking2:
    df_end = pd.DataFrame(ranking2)
    df_end = df_end.sort_values(
        by=["Puntos", "Tiempo"],
        ascending=[False, True],
        key=lambda c: c.map(lambda x: x if isinstance(x, int) else 999999)
    )

    st.table(df_end.head(3))

    st.markdown("## 🌍 Progreso global")
    for row in df_end.itertuples():
        st.write(f"**{row.Jugador}** — {row.Puntos} pts")
        barra_carretera_html(min(row.Puntos / 50, 1))
else:
    st.info("Aún sin jugadores.")
# ---------------------------