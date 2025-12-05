# carrera.py — Correcciones finales
# - Una sola barra en la parte inferior (por jugador)
# - Usa la imagen externa para el coche (fallback emoji)
# - Evita NoneType error al leer 'player'
# - 8 preguntas, 60s por pregunta, autorefresh 0.5s
# Requiere: pip install streamlit streamlit-autorefresh pandas

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json
import requests

# ---------- CONFIG ----------
st.set_page_config(page_title="Carrera", layout="wide")
st_autorefresh(interval=500, key="auto_refresh")  # 0.5s refresh

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")

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

# ---------- Preguntas (8) ----------
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

TOTAL_QUESTIONS = len(questions)  # 8
QUESTION_TIME = 60
AUTO_CONTINUE_TIME = 20
POINTS_PER_CORRECT = 10
MAX_POINTS = POINTS_PER_CORRECT * TOTAL_QUESTIONS  # 80

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

# Try to prefetch car image to check availability (user provided URL)
CAR_IMAGE_URL = "https://banner2.cleanpng.com/20190827/qtz/transparent-motor-vehicle-vehicle-yellow-car-automotive-design-5d6ad8c1069ec5.5128779815672833930271.jpg"
def car_image_available(url=CAR_IMAGE_URL, timeout=2):
    try:
        r = requests.head(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

CAR_IMG_OK = car_image_available()

# CSS: fixed bottom bar container (one only)
st.markdown("""
<style>
/* Center main content */
.player-wrapper { max-width:820px; margin-left:auto; margin-right:auto; padding:14px; }

/* Fixed bottom bar for the single player's progress */
#bottom-car-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  pointer-events: none; /* prevents clicks blocking page; controls visible via buttons above */
}
.bottom-inner {
  width: 90%;
  max-width: 920px;
  background: rgba(16,18,20,0.95);
  padding: 8px 12px;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 -6px 18px rgba(0,0,0,0.35);
  pointer-events: auto;
}
.car-fill {
  height: 36px;
  background: linear-gradient(90deg,#00c6ff,#0072ff);
  border-radius: 18px;
  transition: width 0.35s ease;
}
.car-track {
  height: 44px;
  background:#0f1113;
  border-radius:22px;
  padding:4px;
  position:relative;
  overflow:hidden;
}
.car-icon {
  position:absolute;
  top:4px;
  width:32px;
  height:32px;
  transition:left 0.35s ease;
}
.car-flag {
  position:absolute;
  right:12px;
  top:9px;
  font-size:18px;
  color:#cfe9ff;
}
.small-note { font-size:12px; color:#bfcbdc; margin-top:6px; }
</style>
""", unsafe_allow_html=True)

# ---------- Session init ----------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "last_answer_time" not in st.session_state:
    st.session_state.last_answer_time = {}
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

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

# ---------- Sidebar (admin hidden) ----------
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")
if show_admin:
    st.sidebar.header("Administrador")
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
        organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")
        st.sidebar.markdown("### Jugadores conectados")
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
        if st.sidebar.button("🚀 Iniciar carrera (confirmar todos conectados)"):
            if not organizer.strip():
                st.sidebar.warning("Ingrese el nombre del organizador")
            else:
                fs["inicio"] = time.time()
                fs["organizer"] = organizer
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
            if "timestamp" in df_a.columns:
                df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            players_a = sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")}))
            sel = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + players_a)
            if sel != "(Todos)":
                df_a = df_a[df_a["jugador"] == sel]
            cols = []
            if "hora" in df_a.columns:
                cols.append("hora")
            for c in ["jugador","pregunta_idx","selected","correct"]:
                if c in df_a.columns:
                    cols.append(c)
            if cols:
                st.sidebar.dataframe(df_a[cols].sort_values(by="hora", ascending=False).reset_index(drop=True), height=220)
                csv = df_a[cols].to_csv(index=False).encode("utf-8")
                st.sidebar.download_button("Exportar auditoría (CSV)", data=csv, file_name="auditoria.csv", mime="text/csv")
        else:
            st.sidebar.info("Sin registros de auditoría")
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🏆 Top 3")
        ranking = []
        fs_cur = ensure_state_keys(load_state())
        for n, info in fs_cur.get("players_info", {}).items():
            ranking.append({"Jugador": n, "Puntos": info.get("points",0), "Aciertos": info.get("aciertos",0), "Tiempo_raw": info.get("tiempo")})
        if ranking:
            df_r = pd.DataFrame(ranking)
            df_r = df_r.sort_values(by=["Puntos","Tiempo_raw"], ascending=[False,True], key=lambda col: col.map(lambda x: x if isinstance(x,(int,float)) else 999999))
            df_r["Tiempo"] = df_r["Tiempo_raw"].apply(lambda t: format_seconds_to_mmss(t) if (t is not None) else "—")
            st.sidebar.table(df_r[["Jugador","Puntos","Aciertos","Tiempo"]].head(3))
            st.sidebar.markdown("## 🌍 Progreso global")
            for row in df_r.itertuples(index=False):
                progreso = min(row.Puntos / MAX_POINTS, 1.0) if MAX_POINTS>0 else 0
                st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
                # mostrar barra admin (reutilizamos markup)
                html_admin = f"""
                <div style='margin-bottom:12px;'>
                  <div style='width:100%;max-width:400px;background:#0f1113;border-radius:16px;padding:6px;'>
                    <div style='height:18px;width:{min(100,progreso*100)}%;background:linear-gradient(90deg,#00c6ff,#0072ff);border-radius:12px;'></div>
                  </div>
                </div>
                """
                st.sidebar.markdown(html_admin, unsafe_allow_html=True)
        else:
            st.sidebar.info("No hay ranking aún")

# ---------- MAIN (jugador centrado) ----------
st.markdown("<div class='player-wrapper'>", unsafe_allow_html=True)
st.header("Jugador")
player_name = st.text_input("Ingresa tu nombre:", key="player_name_input")

if player_name and player_name.strip():
    add_player(player_name.strip())

fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)

# Mostrar tiempo global si inició
if inicio_global:
    tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
    pasado = int(time.time() - inicio_global)
    tiempo_restante = max(0, tiempo_total - pasado)
    st.info(f"⏳ Tiempo global restante: {tiempo_restante} s")
else:
    st.info("⏳ Esperando al organizador para iniciar la carrera...")

# Si no puso nombre, detener para evitar errores
if not player_name or not player_name.strip():
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# cargar datos del jugador; proteger si aún no está sincronizado
player = st.session_state.jugadores.get(player_name.strip())
if player is None:
    # intentar sincronizar desde state.json una vez
    fs_try = ensure_state_keys(load_state())
    if player_name.strip() in fs_try.get("players_info", {}):
        st.session_state.jugadores[player_name.strip()] = fs_try["players_info"][player_name.strip()]
        player = st.session_state.jugadores.get(player_name.strip())
    else:
        st.warning("Registro pendiente; espera un momento o recarga la página.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# Si jugador terminó
if player.get("fin", False):
    st.success("Has terminado la carrera. ¡Buen trabajo!")
    if player.get("tiempo") is not None:
        st.info(f"Tiempo total: {format_seconds_to_mmss(player.get('tiempo'))}")
    # No mostrar tiempo global tras finalizar (OPCIÓN A)
    st.markdown("</div>", unsafe_allow_html=True)
    # La barra en la parte inferior seguirá mostrando el progreso final
else:
    # Si la carrera no ha iniciado
    if not inicio_global:
        st.info("La carrera aún no ha iniciado. Espera al organizador.")
        progreso_temp = player.get("points",0) / MAX_POINTS if MAX_POINTS>0 else 0
        # mostrar barra (aunque no iniciado)
        pass
    else:
        # calcular tiempo restante total
        tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
        pasado = int(time.time() - inicio_global)
        tiempo_restante = max(0, tiempo_total - pasado)
        st.info(f"⏳ Tiempo global restante: {tiempo_restante} s")

    # Lógica de pantalla "continuar" y preguntas
    preg_idx = player.get("preg", 0)

    # Si ya completó todas las preguntas -> marcar fin y guardar tiempo
    if preg_idx >= TOTAL_QUESTIONS:
        player["fin"] = True
        player["tiempo"] = int(time.time() - inicio_global) if inicio_global else None
        fs_update = ensure_state_keys(load_state())
        fs_update["players_info"][player_name.strip()] = player
        save_state(fs_update)
        st.experimental_rerun()

    # comprobar pantalla "continuar"
    last_t = st.session_state.last_answer_time.get(player_name.strip(), None)
    in_continue = False
    if last_t:
        elapsed = time.time() - last_t
        if elapsed < AUTO_CONTINUE_TIME:
            in_continue = True
        else:
            # limpiar y recargar para avanzar automáticamente
            st.session_state.last_answer_time[player_name.strip()] = None
            st.experimental_rerun()

    if in_continue:
        siguiente = preg_idx + 1
        st.markdown("### Resultado registrado ✅")
        # mostrar última respuesta de auditoría
        answers = load_answers()
        last_answers = [a for a in answers if a.get("jugador")==player_name.strip()]
        if last_answers:
            last = last_answers[-1]
            if last.get("correct"):
                st.success("Respuesta correcta. +10 pts")
            else:
                st.error("Respuesta incorrecta.")
        st.write("")
        if st.button(f"Continuar → Pregunta {siguiente}"):
            st.session_state.last_answer_time[player_name.strip()] = None
            st.experimental_rerun()
        # barra individual (se mostrará en bottom también)
        progreso_local = player.get("points",0) / MAX_POINTS if MAX_POINTS>0 else 0
        st.markdown("</div>", unsafe_allow_html=True)
        # dejar que bottom bar muestre progreso
        # no detener (st.stop) para que bottom bar se aplique
    else:
        # mostrar pregunta actual
        qobj = questions[preg_idx]
        st.subheader(f"Pregunta #{preg_idx+1}")
        st.write(qobj["q"])
        radio_key = f"radio_{player_name.strip()}_{preg_idx}"
        try:
            selection = st.radio("Selecciona una opción:", qobj["options"], key=radio_key)
        except Exception:
            selection = qobj["options"][0]
        send_key = f"send_{player_name.strip()}_{preg_idx}"
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
                # si completó todas, marcar fin y tiempo
                if player["preg"] >= TOTAL_QUESTIONS:
                    player["fin"] = True
                    player["tiempo"] = int(time.time() - inicio_global) if inicio_global else None
                fs_save = ensure_state_keys(load_state())
                fs_save.setdefault("players_info", {})
                fs_save["players_info"][player_name.strip()] = player
                if player_name.strip() not in fs_save.get("jugadores", []):
                    fs_save.setdefault("jugadores", []).append(player_name.strip())
                save_state(fs_save)
                # marcar tiempo para pantalla continuar
                st.session_state.last_answer_time[player_name.strip()] = time.time()
                st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Bottom fixed single bar (visible always, shows only this player's progress)
# ---------------------------
# Determine progress for bottom bar (if player exists)
display_progress = 0.0
display_label = ""
if player is not None:
    display_progress = player.get("points",0) / MAX_POINTS if MAX_POINTS>0 else 0.0
    display_label = f"{player.get('points',0)} pts — Pregunta {min(player.get('preg',0)+1, TOTAL_QUESTIONS)} / {TOTAL_QUESTIONS}"

# Ensure percent
display_percent = max(0.0, min(1.0, display_progress)) * 100

# Render bottom bar HTML (single)
car_img_html = f'<img src="{CAR_IMAGE_URL}" style="width:32px;height:32px;border-radius:4px;"/>'
if not CAR_IMG_OK:
    car_img_html = '<div style="font-size:22px;">🚗</div>'

bottom_html = f"""
<div id="bottom-car-bar">
  <div class="bottom-inner">
    <div style="display:flex; align-items:center; justify-content:space-between;">
      <div style="flex:1; margin-right:12px;">
        <div class="car-track">
          <div class="car-fill" style="width:{display_percent}%;"></div>
          <div class="car-icon" style="left:calc({display_percent}% - 16px);">
            {car_img_html}
          </div>
          <div class="car-flag">🏁</div>
        </div>
        <div class="small-note">{display_label}</div>
      </div>
    </div>
  </div>
</div>
"""
st.markdown(bottom_html, unsafe_allow_html=True)
