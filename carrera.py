# carrera.py — versión mejorada y optimizada

import streamlit as st
import random
import time
import pandas as pd
import os
import json

# Archivos persistentes
BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, 'state.json')
ANSWERS_FILE = os.path.join(BASE_DIR, 'answers.json')

# Cargar estado global
def load_state():
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'inicio': None, 'jugadores': [], 'players_info': {}, 'organizer': None}

# Guardar estado global
def save_state(data):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Cargar respuestas
def load_answers():
    try:
        with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# Guardar respuestas
def save_answers(data):
    with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Añadir respuesta
def append_answer(a):
    ans = load_answers()
    ans.append(a)
    save_answers(ans)
    return len(ans) - 1

# Preguntas de ejemplo (puedes sustituirlas)
questions = [
    {
        "q": "¿Qué es la sociedad red?",
        "options": ["Un sitio web", "Una red de autopistas", "Un sistema de relaciones sociales conectadas", "Un antivirus"],
        "correct": "Un sistema de relaciones sociales conectadas"
    },
    {
        "q": "La ética en IA busca:",
        "options": ["Hacer IA más rápida", "Regular decisiones justas", "Eliminar humanos", "Ninguna"],
        "correct": "Regular decisiones justas"
    },
]

# Tiempo por pregunta → 20 s (pedido por el usuario)
QUESTION_TIME = 20
TIEMPO_LIMITE = QUESTION_TIME * len(questions)

# Estado de sesión
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "inicio" not in st.session_state:
    st.session_state.inicio = load_state().get("inicio")

# Registrar jugador
def add_player(name):
    fs = load_state()

    # Si no existe en el archivo global
    if name not in fs["jugadores"]:
        fs["jugadores"].append(name)

    # Info del jugador
    fs["players_info"].setdefault(
        name,
        {"points": 0, "aciertos": 0, "preg": 0, "fin": False, "tiempo": None, "joined": time.time()}
    )

    save_state(fs)
    st.session_state.jugadores.setdefault(name, fs["players_info"][name])

# Barra tipo pista con HTML
def barra_carretera_html(progreso):
    porcentaje = progreso * 100
    coche_pos = max(0, min(92, porcentaje))  # límite visual del emoji para evitar que salga del cuadro

    html = f"""
    <div style="position: relative; width: 100%; height: 35px; background: #e5e5e5; border-radius: 15px; margin-bottom:10px;">
        <div style="
            position:absolute;
            left:{coche_pos}%;
            top:3px;
            font-size:25px;
            transition:left 0.5s ease;">
            🚗
        </div>

        <div style="position:absolute; right:5px; top:3px; font-size:25px;">🏁</div>

        <div style="
            position:absolute;
            width:{porcentaje}%;
            height: 35px;
            background:#22c55e;
            opacity:0.35;
            border-radius:15px;">
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ================================
st.set_page_config(page_title="Carrera en vivo", layout="wide")
st.title("🏁 Carrera en vivo")

# ================================
# PANEL DE ADMINISTRACIÓN
# ================================
st.sidebar.subheader("🔐 Administrador")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Si NO está autenticado → pedir login
if not st.session_state.admin_authenticated:
    u = st.sidebar.text_input("Usuario")
    p = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
        if u == "Grupo5" and p == "2025":
            st.session_state.admin_authenticated = True
            st.sidebar.success("Acceso permitido")
        else:
            st.sidebar.error("Credenciales incorrectas")

# Si ya está autenticado → mostrar panel completo
else:
    fs = load_state()

    # Nombre del organizador
    organizer = st.sidebar.text_input("Nombre de quien inicia el programa:")

    # Mostrar jugadores conectados
    st.sidebar.markdown("### 👥 Jugadores conectados")
    jugadores_tabla = []

    for j in fs["players_info"]:
        info = fs["players_info"][j]
        jugadores_tabla.append({
            "Jugador": j,
            "Aciertos": info["aciertos"],
            "Puntos": info["points"],
            "Conectado": time.strftime("%H:%M:%S", time.localtime(info.get("joined", time.time())))
        })

    if jugadores_tabla:
        df_j = pd.DataFrame(jugadores_tabla).sort_values("Conectado")
        st.sidebar.dataframe(df_j, height=230)
    else:
        st.sidebar.info("Ningún jugador conectado.")

    # Iniciar carrera
    if st.sidebar.button("🚀 Iniciar carrera"):
        if not organizer.strip():
            st.sidebar.error("Debe ingresar el nombre del organizador.")
        else:
            fs["inicio"] = time.time()
            fs["organizer"] = organizer
            save_state(fs)
            st.session_state.inicio = fs["inicio"]
            st.sidebar.success("Carrera iniciada")

    # Limpiar todo
    if st.sidebar.button("🧹 Limpiar TODOS los registros"):
        save_state({'inicio': None, 'jugadores': [], 'players_info': {}, 'organizer': None})
        save_answers([])
        st.session_state.jugadores = {}
        st.session_state.answers = []
        st.session_state.inicio = None
        st.sidebar.success("Sistema limpiado correctamente")

# ================================
# SECCIÓN DEL JUGADOR
# ================================
st.subheader("Ingresa para participar en la carrera")

nombre = st.text_input("Tu nombre:")

if nombre:
    add_player(nombre)

    jugador = st.session_state.jugadores[nombre]
    fs = load_state()
    inicio = fs["inicio"]

    # Tiempo global
    if inicio:
        tiempo_rest = max(0, TIEMPO_LIMITE - int(time.time() - inicio))
        st.info(f"⏳ Tiempo restante: {tiempo_rest} s")
    else:
        st.warning("La carrera aún no inicia.")

    # Mostrar preguntas si ya inició la carrera
    if inicio and tiempo_rest > 0 and not jugador["fin"]:

        idx = jugador["preg"] % len(questions)
        q = questions[idx]

        st.markdown(f"### ❓ Pregunta #{idx+1}")
        st.write(q["q"])

        r = st.radio("Selecciona una opción:", q["options"], key=f"{nombre}_r_{idx}")

        if st.button("Enviar respuesta", key=f"{nombre}_btn_{idx}"):

            correcto = r == q["correct"]

            # Guardar en auditoría
            entry = {
                "timestamp": int(time.time()),
                "jugador": nombre,
                "pregunta_idx": idx,
                "selected": r,
                "correct": correcto
            }
            append_answer(entry)

            # Aciertos y puntos
            if correcto:
                st.success("¡Correcto! +10 puntos 🚗💨")
                jugador["points"] += 10
                jugador["aciertos"] += 1
            else:
                st.error("Incorrecto 😞")

            jugador["preg"] += 1

            # Si llegó a la meta
            if jugador["points"] >= 50:
                jugador["fin"] = True
                jugador["tiempo"] = int(time.time() - inicio)
                st.balloons()
                st.success("🏆 ¡Llegaste a la meta!")

            fs["players_info"][nombre] = jugador
            save_state(fs)

    # Progreso del jugador actual
    st.markdown("### 🚗 Tu progreso")
    progreso = min(jugador["points"] / 50, 1)
    barra_carretera_html(progreso)

# ================================
# RANKING GLOBAL
# ================================
st.markdown("## 🏆 Top 3 global")

tabla = []
for j, info in st.session_state.jugadores.items():
    tabla.append({
        "Jugador": j,
        "Puntos": info["points"],
        "Aciertos": info["aciertos"],
        "Tiempo": info.get("tiempo", 9999)
    })

if tabla:
    df = pd.DataFrame(tabla).sort_values(["Puntos", "Tiempo"], ascending=[False, True])
    st.table(df.head(3))

    st.markdown("## 🌍 Progreso de todos los jugadores")
    for row in df.itertuples():
        st.write(f"### 👤 {row.Jugador} — {row.Puntos} pts")
        barra_carretera_html(min(row.Puntos / 50, 1))
