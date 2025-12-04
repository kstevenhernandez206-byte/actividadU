# carrera.py — Versión final (12 preguntas) — Opción C
# Panel Admin (sidebar): controles, lista conectados, Top 3 y progreso global
# Pantalla Jugador: ingreso, preguntas, progreso individual (carro animado)
# Tiempo por pregunta = 20s
# Guardado inmediato en state.json y answers.json

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
# Preguntas (12) y respuestas
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

# ---------------------------
# Parámetros de la carrera
# ---------------------------
QUESTION_TIME = 20  # segundos
POINTS_PER_CORRECT = 10
POINTS_TO_FINISH = 50  # meta

# ---------------------------
# Estado en session
# ---------------------------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "inicio" not in st.session_state:
    st.session_state.inicio = load_state().get("inicio")

# ---------------------------
# Funciones utilitarias
# ---------------------------
def add_player(name):
    name = name.strip()
    if not name:
        return
    fs = load_state()
    if name not in fs.get("jugadores", []):
        fs.setdefault("jugadores", []).append(name)
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
    # sincronizar session_state
    st.session_state.jugadores.setdefault(name, fs["players_info"][name])

def reset_all():
    save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
    save_answers([])
    st.session_state.jugadores = {}
    st.session_state.answers = []
    st.session_state.inicio = None

# HTML simple (no librerías) para pista y coche
def barra_carretera_html(progreso, width="100%"):
    # progreso: 0.0 - 1.0
    porcentaje = max(0.0, min(1.0, progreso)) * 100
    coche_pos = porcentaje
    # HTML: contenedor gris, segmento verde de fondo y emoji coche en posición proporcional
    html = f"""
    <div style="position: relative; width: {width}; height: 36px; background: #2b2b2b; border-radius: 10px; padding:4px; overflow:hidden;">
        <div style="position:absolute; left:0; top:0; height:100%; width:{porcentaje}%; background: rgba(34,197,94,0.2); border-radius:10px;"></div>
        <div style="position:absolute; left:{max(0,min(92,coche_pos))}%; top:3px; font-size:22px; transform:translateX(-50%); transition:left 0.4s ease;">🚗</div>
        <div style="position:absolute; right:6px; top:6px; font-size:18px;">🏁</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Configuración de página
# ---------------------------
st.set_page_config(page_title="Carrera en vivo", layout="wide")
st.title("🏁 Carrera en vivo")

# ---------------------------
# PANEL ADMIN (Sidebar)
# ---------------------------
st.sidebar.subheader("🔐 Administrador")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    user_input = st.sidebar.text_input("Usuario")
    pass_input = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        # Cambia aquí credenciales si lo requieres
        if user_input == "Grupo5" and pass_input == "2025":
            st.session_state.admin_authenticated = True
            st.sidebar.success("Autenticado como admin")
        else:
            st.sidebar.error("Credenciales incorrectas")
else:
    fs = load_state()
    # organizer input
    organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")
    # Mostrar jugadores conectados como tabla
    st.sidebar.markdown("### 👥 Jugadores conectados")
    players_list = []
    for name, info in fs.get("players_info", {}).items():
        players_list.append({
            "Jugador": name,
            "Aciertos": info.get("aciertos", 0),
            "Puntos": info.get("points", 0),
            "Conectado": time.strftime("%H:%M:%S", time.localtime(info.get("joined", time.time())))
        })
    if players_list:
        df_players = pd.DataFrame(players_list).sort_values("Conectado")
        st.sidebar.dataframe(df_players, height=220)
    else:
        st.sidebar.info("Sin jugadores conectados aún.")

    st.sidebar.markdown("---")
    # Iniciar carrera
    if st.sidebar.button("🚀 Iniciar carrera (confirmar todos conectados)"):
        if not organizer.strip():
            st.sidebar.warning("Ingresa el nombre del organizador antes de iniciar.")
        else:
            fs["inicio"] = time.time()
            fs["organizer"] = organizer
            save_state(fs)
            st.session_state.inicio = fs["inicio"]
            st.sidebar.success("Carrera iniciada")

    # Limpiar registros
    if st.sidebar.button("🧹 Limpiar TODOS los registros"):
        reset_all()
        st.sidebar.success("Todos los registros limpiados")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🏆 Top 3 (global)")
    # Top3 en sidebar
    # sincronizar session_state con estado persistente antes de mostrar
    fs2 = load_state()
    ranking_arr = []
    for n, info in fs2.get("players_info", {}).items():
        ranking_arr.append({
            "Jugador": n,
            "Puntos": info.get("points", 0),
            "Aciertos": info.get("aciertos", 0),
            "Tiempo": info.get("tiempo", None) or 999999
        })
    if ranking_arr:
        df_r = pd.DataFrame(ranking_arr)
        df_r = df_r.sort_values(by=["Puntos", "Tiempo"], ascending=[False, True]).reset_index(drop=True)
        # mostrar sólo top 3
        st.sidebar.table(df_r.head(3))
    else:
        st.sidebar.info("No hay ranking aún.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🌍 Progreso global")
    # Progreso global: mostrar barra por jugador en sidebar
    if ranking_arr:
        for row in df_r.itertuples(index=False):
            nombre = row.Jugador
            puntos = int(row.Puntos)
            progreso = min(puntos / POINTS_TO_FINISH, 1.0) if POINTS_TO_FINISH > 0 else 0
            st.sidebar.write(f"**{nombre}** — {puntos} pts")
            barra_carretera_html(progreso, width="100%")
    else:
        st.sidebar.info("No hay jugadores para mostrar progreso.")

# ---------------------------
# PANEL JUGADOR (principal derecha)
# ---------------------------
st.subheader("🔹 Área de jugador")
nombre = st.text_input("Ingresa tu nombre para unirte:", key="player_name_input")

if nombre and nombre.strip():
    add_player(nombre.strip())

# Mostrar estado global y tiempo restante
fs_main = load_state()
inicio_global = fs_main.get("inicio")

if inicio_global:
    tiempo_restante_global = max(0, QUESTION_TIME * len(questions) - int(time.time() - inicio_global))
    st.info(f"⏰ Tiempo global restante: {tiempo_restante_global} s")
else:
    st.info("⏳ Esperando que el organizador inicie la carrera...")

# Si jugador ingresó su nombre, mostrar interacción
if nombre and nombre.strip():
    jugador = st.session_state.jugadores.get(nombre.strip(), None)
    if not jugador:
        st.warning("Tu registro aún no se ha sincronizado; intenta refrescar.")
    else:
        # Mostrar progreso individual y preguntas solo si la carrera inició
        if inicio_global and tiempo_restante_global > 0 and not jugador.get("fin", False):
            idx = jugador.get("preg", 0) % len(questions)
            qdata = questions[idx]
            st.markdown(f"### ❓ Pregunta #{idx+1}")
            st.write(qdata["q"])
            opciones = qdata["options"]
            key_radio = f"radio_{nombre.strip()}_{idx}"
            seleccion = st.radio("Selecciona una opción:", opciones, key=key_radio)
            submit_key = f"submit_{nombre.strip()}_{idx}"
            if st.button("Enviar respuesta", key=submit_key):
                correcto = seleccion == qdata["correct"]
                entry = {
                    "timestamp": int(time.time()),
                    "jugador": nombre.strip(),
                    "pregunta_idx": idx,
                    "selected": seleccion,
                    "correct": correcto
                }
                append_answer(entry)
                if correcto:
                    st.success("✅ ¡Correcto! +10 puntos")
                    jugador["points"] = jugador.get("points", 0) + POINTS_PER_CORRECT
                    jugador["aciertos"] = jugador.get("aciertos", 0) + 1
                else:
                    st.error("❌ Incorrecto")
                jugador["preg"] = jugador.get("preg", 0) + 1
                # revisar meta
                if jugador.get("points", 0) >= POINTS_TO_FINISH:
                    jugador["fin"] = True
                    jugador["tiempo"] = int(time.time() - inicio_global)
                    st.balloons()
                    st.success("🏁 ¡Llegaste a la meta!")
                # guardar en state persistente
                fs_p = load_state()
                fs_p.setdefault("players_info", {})
                fs_p["players_info"][nombre.strip()] = jugador
                save_state(fs_p)
        else:
            if not inicio_global:
                st.info("La carrera no ha iniciado. Espera al organizador.")
            elif jugador.get("fin", False):
                st.success("Has terminado la carrera. ¡Buen trabajo!")
            else:
                st.warning("Tiempo global finalizado o no disponible.")

        # Progreso individual (siempre visible)
        st.markdown("### 🚗 Tu progreso")
        puntos_actuales = jugador.get("points", 0)
        progreso_local = min(puntos_actuales / POINTS_TO_FINISH, 1.0) if POINTS_TO_FINISH > 0 else 0
        st.write(f"Puntos: {puntos_actuales} — Aciertos: {jugador.get('aciertos', 0)}")
        barra_carretera_html(progreso_local, width="100%")

# ---------------------------
# RANKING Y PROGRESO GLOBAL (zona principal)
# ---------------------------
# Mostrar top 3 y progreso global en área principal también (más grande)
st.markdown("---")
st.markdown("## 🏆 Top 3 global (zona principal)")
fs_final = load_state()
ranking_main = []
for n, info in fs_final.get("players_info", {}).items():
    ranking_main.append({
        "Jugador": n,
        "Puntos": info.get("points", 0),
        "Aciertos": info.get("aciertos", 0),
        "Tiempo": info.get("tiempo", None) or 999999
    })

if ranking_main:
    df_main = pd.DataFrame(ranking_main)
    df_main = df_main.sort_values(by=["Puntos", "Tiempo"], ascending=[False, True]).reset_index(drop=True)
    st.table(df_main.head(3))

    st.markdown("## 🌍 Progreso de todos los jugadores (zona principal)")
    for row in df_main.itertuples(index=False):
        nombre_row = row.Jugador
        puntos_row = int(row.Puntos)
        progreso_row = min(puntos_row / POINTS_TO_FINISH, 1.0) if POINTS_TO_FINISH > 0 else 0
        st.write(f"**{nombre_row}** — {puntos_row} pts")
        barra_carretera_html(progreso_row, width="100%")
else:
    st.info("Aún no hay jugadores registrados para mostrar ranking.")
# Fin de carrera.py