# carrera.py — Formulario Inteligencia Artificial y Sistema Cibernéticos
# Requisitos:
#   pip install streamlit streamlit-autorefresh pandas requests

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json
import requests

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Formulario IA y Sistemas Cibernéticos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")
SPACESHIP_URL = "https://pngimg.com/uploads/spaceship/spaceship_PNG52.png"

# ---------- PREGUNTAS ----------
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
QUESTION_TIME = 50  # 50 segundos por pregunta
CONTINUE_TIME = 10   # 10 segundos pantalla continuar
POINTS_PER_CORRECT = 10
MAX_POINTS = POINTS_PER_CORRECT * TOTAL_QUESTIONS

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

def ensure_state_keys(fs):
    fs.setdefault("inicio", None)
    fs.setdefault("jugadores", [])
    fs.setdefault("players_info", {})
    fs.setdefault("organizer", None)
    return fs

def format_seconds_to_mmss(s):
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"

# ---------- Session init ----------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "last_answer_time" not in st.session_state:
    st.session_state.last_answer_time = {}
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "admin_name" not in st.session_state:
    st.session_state.admin_name = ""

# ---------- ADMIN ----------
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")
if show_admin:
    st.sidebar.header("Administrador")
    if not st.session_state.admin_authenticated:
        admin_user = st.sidebar.text_input("Usuario (admin)")
        admin_pass = st.sidebar.text_input("Contraseña (admin)", type="password")
        if st.sidebar.button("Iniciar sesión como admin"):
            if admin_user == "Grupo5" and admin_pass == "2025":
                st.session_state.admin_authenticated = True
                st.session_state.admin_name = admin_user
                st.sidebar.success("Autenticado")
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        fs = ensure_state_keys(load_state())
        organizer = st.sidebar.text_input("Nombre del organizador:", value=fs.get("organizer") or "")
        st.sidebar.markdown("**Jugadores conectados**")
        players_list = []
        for n, info in fs.get("players_info", {}).items():
            joined_str = time.strftime("%H:%M:%S", time.localtime(info.get("joined",0))) if info.get("joined") else "—"
            players_list.append({"Jugador": n, "Aciertos": info.get("aciertos",0), "Puntos": info.get("points",0), "Conectado": joined_str})
        if players_list:
            st.sidebar.dataframe(pd.DataFrame(players_list).sort_values("Conectado"), height=220)
        else:
            st.sidebar.info("No hay jugadores conectados")
        st.sidebar.markdown("---")
        cols = st.sidebar.columns([1,1])
        if cols[0].button("🚀 Iniciar carrera"):
            if not organizer.strip():
                st.sidebar.warning("Ingrese el nombre del organizador")
            else:
                fs["inicio"] = time.time()
                fs["organizer"] = organizer
                save_state(fs)
                st.sidebar.success("Carrera iniciada")
        if cols[1].button("🧹 Limpiar TODO"):
            save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
            save_answers([])
            st.session_state.jugadores = {}
            st.session_state.answers = []
            st.session_state.last_answer_time = {}
            st.session_state.admin_authenticated = False
            st.session_state.admin_name = ""
            st.sidebar.success("Sistema reiniciado")
        # Auditoría: descargar CSV
        answers = load_answers()
        if answers:
            df = pd.DataFrame(answers)
            df["admin"] = st.session_state.admin_name
            csv = df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button("📥 Descargar Auditoría", data=csv, file_name="auditoria.csv", mime="text/csv")
        else:
            st.sidebar.info("Sin registros de auditoría")

# ---------- MAIN (jugador) ----------
st.title("Formulario de Inteligencia Artificial y Sistemas Cibernéticos")
player_name = st.text_input("Ingresa tu nombre:")
if player_name and st.button("Ingresar"):
    fs = ensure_state_keys(load_state())
    if player_name not in fs["jugadores"]:
        fs["jugadores"].append(player_name)
    fs.setdefault("players_info", {})
    fs["players_info"].setdefault(player_name, {"points":0,"aciertos":0,"preg":0,"fin":False,"tiempo":None,"joined":time.time()})
    save_state(fs)
    st.session_state.jugadores[player_name] = fs["players_info"][player_name]

# No avanzar hasta que admin inicie carrera
fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)
if not inicio_global:
    st.info("⏳ Esperando al organizador para iniciar la carrera...")
    st.stop()

# Cargar jugador
player = st.session_state.jugadores.get(player_name)
if not player:
    st.warning("Registro pendiente; recarga la página.")
    st.stop()

# Refresco rápido
st_autorefresh(interval=700, key="auto_refresh")

# Mostrar tiempo global restante
tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
pasado = int(time.time() - inicio_global)
tiempo_restante = max(0, tiempo_total - pasado)
st.info(f"⏳ Tiempo global restante: {format_seconds_to_mmss(tiempo_restante)}")

# ---------- PREGUNTA / CONTINUAR ----------
preg_idx = player.get("preg", 0)
if preg_idx >= TOTAL_QUESTIONS:
    player["fin"] = True
    player["tiempo"] = int(time.time() - inicio_global)
    fs_main["players_info"][player_name] = player
    save_state(fs_main)
    st.success("Has terminado la carrera.")
else:
    last_t = st.session_state.last_answer_time.get(player_name, 0)
    in_continue = last_t and (time.time()-last_t < CONTINUE_TIME)
    if in_continue:
        # Pantalla continuar
        st.success("Resultado registrado ✅")
        last_ans = [a for a in load_answers() if a.get("jugador")==player_name][-1]
        if last_ans.get("correct"):
            st.success("Respuesta correcta +10 pts")
        else:
            st.error("Respuesta incorrecta")
        if st.button(f"Continuar → Pregunta {preg_idx+1}"):
            st.session_state.last_answer_time[player_name] = None
            st.rerun()
    else:
        # Mostrar pregunta
        qobj = questions[preg_idx]
        st.markdown(f"**Pregunta #{preg_idx+1}:** {qobj['q']}")
        selection = st.radio("", qobj["options"], key=f"radio_{player_name}_{preg_idx}", label_visibility="collapsed")
        if st.button("Enviar respuesta", key=f"send_{player_name}_{preg_idx}"):
            correcto = (selection == qobj["correct"])
            append_answer({"timestamp":int(time.time()), "jugador":player_name, "pregunta_idx":preg_idx, "selected":selection, "correct":correcto, "admin":st.session_state.admin_name})
            if correcto:
                player["points"] += POINTS_PER_CORRECT
                player["aciertos"] +=1
            player["preg"] +=1
            if player["preg"] >= TOTAL_QUESTIONS:
                player["fin"] = True
                player["tiempo"] = int(time.time() - inicio_global)
            fs_main["players_info"][player_name] = player
            save_state(fs_main)
            st.session_state.last_answer_time[player_name] = time.time()
            st.rerun()

# ---------- BARRA DE PROGRESO ----------
display_progress = player.get("points",0)/MAX_POINTS if MAX_POINTS>0 else 0.0
display_percent = max(0.0,min(1.0,display_progress))*100
spaceship_html = f'<img src="{SPACESHIP_URL}" style="width:34px;height:34px;object-fit:contain"/>' 

st.markdown(f"""
<div style="position:fixed; bottom:0; left:0; width:100%; background:#000; padding:6px 12px;">
    <div style="background:#111; height:24px; border-radius:4px; position:relative;">
        <div style="background:#00d0ff; width:{display_percent}%; height:100%; border-radius:4px;"></div>
        <div style="position:absolute; left:calc({display_percent}% - 17px); top:0;">{spaceship_html}</div>
    </div>
    <div style="text-align:center; font-size:14px; color:#fff;">
        Puntos: {player.get("points",0)} — Pregunta {min(player.get('preg',0)+1,TOTAL_QUESTIONS)}/{TOTAL_QUESTIONS}
    </div>
</div>
""", unsafe_allow_html=True)
