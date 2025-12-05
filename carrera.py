# carrera.py — Versión FINAL corregida y unificada
# - Autorefresh 0.5s siempre
# - 8 preguntas, 60s por pregunta
# - Termina al responder las 8 preguntas (no por puntos)
# - Barra individual estética y animada (solo visible para cada jugador)
# - Botón "Continuar → Pregunta X" con avance automático a 20s
# - Panel admin oculto por checkbox; auditoría filtrable; top3 y progreso global en admin
# - Manejo robusto de session_state y sincronización con state.json para evitar NoneType
# Requisitos: pip install streamlit streamlit-autorefresh pandas

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json

# ---------------------------
# Configuración inicial
# ---------------------------
st.set_page_config(page_title="Carrera en vivo", layout="wide")
st_autorefresh(interval=500, key="auto_refresh")  # refresco cada 0.5s (siempre)

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")

# ---------------------------
# Utilidades de persistencia
# ---------------------------
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
    ans = load_answers()
    ans.append(entry)
    save_answers(ans)

# ---------------------------
# Preguntas (8 seleccionadas)
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

TOTAL_QUESTIONS = len(questions)  # 8
QUESTION_TIME = 60                # segundos por pregunta (global)
AUTO_CONTINUE_TIME = 20           # segundos para presionar "Continuar" o avanzar automáticamente
POINTS_PER_CORRECT = 10
MAX_POINTS = POINTS_PER_CORRECT * TOTAL_QUESTIONS  # 80, usado solo para representación de la barra

# ---------------------------
# Helpers / UI utilities
# ---------------------------
def ensure_state_keys(fs):
    fs.setdefault("inicio", None)
    fs.setdefault("jugadores", [])
    fs.setdefault("players_info", {})
    fs.setdefault("organizer", None)
    return fs

def format_seconds_to_mmss(s):
    try:
        s = int(s)
    except Exception:
        return "—"
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"

def barra_carretera_html_for_player(progreso, width="90%"):
    porcentaje = max(0.0, min(1.0, float(progreso))) * 100
    left = max(2, min(98, porcentaje))
    html = f"""
    <div style="margin-top:12px;margin-bottom:24px;">
      <div style="margin: 0 auto; max-width:{width};">
        <div style="position:relative;width:100%;height:34px;background:#101214;border-radius:18px;padding:4px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.4);">
          <div style="position:absolute;left:0;top:0;height:100%;width:{porcentaje}%;background:linear-gradient(90deg,#00c6ff,#0072ff);opacity:0.23;border-radius:18px;transition:width:0.35s ease;"></div>
          <div style="position:absolute;left:{left}%;top:2px;transform:translateX(-50%);transition:left:0.35s ease;">
            <img src="https://img.icons8.com/emoji/48/car-emoji.png" style="width:28px;height:28px;"/>
          </div>
          <div style="position:absolute;right:8px;top:6px;font-size:16px;color:#cfe9ff;">🏁</div>
        </div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Inicializar session_state seguro
# ---------------------------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()
if "last_answer_time" not in st.session_state:
    st.session_state.last_answer_time = {}
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# ---------------------------
# Funciones de sincronización y manipulación
# ---------------------------
def sync_state_to_session():
    """Trae el state.json y sincroniza players_info con st.session_state.jugadores sin sobrescribir datos locales."""
    fs = ensure_state_keys(load_state())
    players_info = fs.get("players_info", {})
    # Añadir o actualizar session_state.jugadores con lo que haya en file
    for name, info in players_info.items():
        st.session_state.jugadores.setdefault(name, info)
    # Asegurar lista de jugadores en session_state (no necesaria pero útil)
    for n in fs.get("jugadores", []):
        st.session_state.jugadores.setdefault(n, players_info.get(n, {"points":0,"aciertos":0,"preg":0,"fin":False,"tiempo":None,"joined":time.time()}))

def add_player(name):
    """Registra jugador en state.json y en session_state de forma robusta."""
    name = name.strip()
    if not name:
        return
    fs = ensure_state_keys(load_state())
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
    # sincronizar inmediatamente en session_state
    st.session_state.jugadores.setdefault(name, fs["players_info"][name])

def persist_player(player_name):
    """Guarda datos de un jugador en state.json."""
    fs = ensure_state_keys(load_state())
    fs.setdefault("players_info", {})
    fs["players_info"][player_name] = st.session_state.jugadores[player_name]
    if player_name not in fs.get("jugadores", []):
        fs.setdefault("jugadores", []).append(player_name)
    save_state(fs)

def reset_all():
    save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
    save_answers([])
    st.session_state.jugadores = {}
    st.session_state.answers = []
    st.session_state.last_answer_time = {}
    st.session_state.admin_authenticated = False

# Sincronizar al inicio del script
sync_state_to_session()

# ---------------------------
# Sidebar: Admin (oculto por checkbox)
# ---------------------------
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")

if show_admin:
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
        fs = ensure_state_keys(load_state())
        organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")

        st.sidebar.markdown("### 👥 Jugadores conectados")
        players_table = []
        for n, info in fs.get("players_info", {}).items():
            joined_ts = info.get("joined", None)
            joined = time.strftime("%H:%M:%S", time.localtime(joined_ts)) if joined_ts else "—"
            players_table.append({
                "Jugador": n,
                "Aciertos": info.get("aciertos", 0),
                "Puntos": info.get("points", 0),
                "Conectado": joined
            })
        if players_table:
            st.sidebar.dataframe(pd.DataFrame(players_table).sort_values("Conectado"), height=220)
        else:
            st.sidebar.info("No hay jugadores conectados")

        st.sidebar.markdown("---")
        if st.sidebar.button("🚀 Iniciar carrera (confirmar todos conectados)"):
            if not organizer.strip():
                st.sidebar.warning("Ingrese el nombre del organizador antes de iniciar.")
            else:
                fs["inicio"] = time.time()
                fs["organizer"] = organizer
                save_state(fs)
                st.sidebar.success("Carrera iniciada")

        if st.sidebar.button("🧹 Limpiar TODOS los registros"):
            reset_all()
            st.sidebar.success("Registros limpiados")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🗂 Auditoría (respuestas)")
        answers = load_answers()
        if answers:
            df_a = pd.DataFrame(answers)
            if "timestamp" in df_a.columns:
                df_a = df_a.copy()
                df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            jugadores_a = sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")}))
            sel = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + jugadores_a)
            if sel != "(Todos)":
                df_a = df_a[df_a["jugador"] == sel]
            cols = []
            if "hora" in df_a.columns:
                cols.append("hora")
            for c in ["jugador", "pregunta_idx", "selected", "correct"]:
                if c in df_a.columns:
                    cols.append(c)
            if cols:
                st.sidebar.dataframe(df_a[cols].sort_values(by="hora", ascending=False).reset_index(drop=True), height=220)
                csv = df_a[cols].to_csv(index=False).encode("utf-8")
                st.sidebar.download_button("Exportar auditoría (CSV)", data=csv, file_name="auditoria.csv", mime="text/csv")
            else:
                st.sidebar.info("No hay columnas para mostrar")
        else:
            st.sidebar.info("No hay registros de auditoría aún")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🏆 Top 3 (global)")
        ranking = []
        fs_cur = ensure_state_keys(load_state())
        for n, info in fs_cur.get("players_info", {}).items():
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
            df_r["Tiempo"] = df_r["Tiempo_raw"].apply(lambda t: format_seconds_to_mmss(t) if (t is not None) else "—")
            st.sidebar.table(df_r[["Jugador", "Puntos", "Aciertos", "Tiempo"]].head(3))

            st.sidebar.markdown("## 🌍 Progreso global")
            for row in df_r.itertuples(index=False):
                progreso = min(row.Puntos / MAX_POINTS, 1.0) if MAX_POINTS > 0 else 0
                st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
                barra_carretera_html_for_player(progreso, width="100%")
        else:
            st.sidebar.info("No hay ranking aún")

# ---------------------------
# Main: área del jugador (centrada, con animaciones CSS)
# ---------------------------
st.markdown("""
<style>
.player-wrapper {
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
  padding: 18px;
}
.fadeIn {
  animation: fadeIn 0.28s ease-in-out;
}
@keyframes fadeIn {
  from {opacity:0; transform: translateY(6px);}
  to {opacity:1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='player-wrapper fadeIn'>", unsafe_allow_html=True)

st.title("Jugador")
player_name = st.text_input("Ingresa tu nombre:", key="player_name_input")

# Registrar y sincronizar
if player_name and player_name.strip():
    add_player(player_name.strip())
    # asegurar sincronización inmediata
    sync_state_to_session()

fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)

# Mostrar tiempo global restante si inició
if inicio_global:
    tiempo_total = QUESTION_TIME * TOTAL_QUESTIONS
    tiempo_pasado = int(time.time() - inicio_global)
    tiempo_restante = max(0, tiempo_total - tiempo_pasado)
    st.info(f"⏳ Tiempo global restante: {tiempo_restante} s")
else:
    st.info("⏳ Esperando que el organizador inicie la carrera...")

# Si no hay nombre, detener aquí
if not player_name or not player_name.strip():
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Asegurar que player exista en session_state (evita NoneType)
if player_name.strip() not in st.session_state.jugadores:
    sync_state_to_session()
player = st.session_state.jugadores.get(player_name.strip())

if player is None:
    # Crear un registro temporal y sincronizar
    add_player(player_name.strip())
    sync_state_to_session()
    player = st.session_state.jugadores.get(player_name.strip())

# Si el jugador terminó
if player.get("fin", False):
    st.success("Has terminado la carrera. ¡Buen trabajo!")
    if player.get("tiempo") is not None:
        st.info(f"Tiempo total: {format_seconds_to_mmss(player.get('tiempo'))}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Si carrera no inició
if not inicio_global:
    st.info("La carrera aún no ha iniciado. Espera al organizador.")
    progreso_temp = player.get("points", 0) / MAX_POINTS if MAX_POINTS > 0 else 0
    barra_carretera_html_for_player(progreso_temp, width="90%")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Si jugador ya ha respondido las 8 preguntas (seguridad)
if player.get("preg", 0) >= TOTAL_QUESTIONS:
    player["fin"] = True
    player["tiempo"] = int(time.time() - inicio_global)
    st.session_state.jugadores[player_name.strip()] = player
    persist_player(player_name.strip())
    st.experimental_rerun()

# Lógica para pantalla "Continuar" y contador auto-advance
preg_idx = player.get("preg", 0)
last_t = st.session_state.last_answer_time.get(player_name.strip(), None)
in_continue_screen = False
if last_t:
    elapsed = time.time() - last_t
    if elapsed < AUTO_CONTINUE_TIME:
        in_continue_screen = True
    else:
        # tiempo agotado: limpiar y recargar (ya se avanzó preg cuando respondió)
        st.session_state.last_answer_time[player_name.strip()] = None
        st.experimental_rerun()

if in_continue_screen:
    siguiente = preg_idx + 1
    st.markdown("### Resultado registrado ✅")
    # mostrar si última respuesta correcta (leer última de auditoría)
    answers = load_answers()
    last_answers = [a for a in answers if a.get("jugador") == player_name.strip()]
    if last_answers:
        last = last_answers[-1]
        if last.get("correct"):
            st.success("Respuesta correcta. +10 pts")
        else:
            st.error("Respuesta incorrecta.")
    st.write("")  # espacio
    # Botón Continuar con etiqueta dinámica
    if st.button(f"Continuar → Pregunta {siguiente}"):
        st.session_state.last_answer_time[player_name.strip()] = None
        st.experimental_rerun()
    # mostrar barra solo del jugador
    progreso_local = player.get("points", 0) / MAX_POINTS if MAX_POINTS > 0 else 0
    barra_carretera_html_for_player(progreso_local, width="90%")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Mostrar pregunta actual
qobj = questions[preg_idx]
st.subheader(f"Pregunta #{preg_idx + 1}")
st.write(qobj["q"])

# Radio con key único por jugador y pregunta
radio_key = f"radio_{player_name.strip()}_{preg_idx}"
options = qobj["options"]
try:
    selection = st.radio("Selecciona una opción:", options, key=radio_key)
except Exception:
    selection = options[0]

# Botón enviar protegido
send_key = f"send_{player_name.strip()}_{preg_idx}"
if st.button("Enviar respuesta", key=send_key):
    if selection not in options:
        st.warning("Selecciona una opción antes de enviar.")
    else:
        correcto = (selection == qobj["correct"])
        append_answer({
            "timestamp": int(time.time()),
            "jugador": player_name.strip(),
            "pregunta_idx": preg_idx,
            "selected": selection,
            "correct": correcto
        })
        # actualizar datos del jugador en memory
        if correcto:
            player["points"] = player.get("points", 0) + POINTS_PER_CORRECT
            player["aciertos"] = player.get("aciertos", 0) + 1
        player["preg"] = player.get("preg", 0) + 1
        # persistir en state
        st.session_state.jugadores[player_name.strip()] = player
        persist_player(player_name.strip())
        # marcar tiempo de respuesta para pantalla continuar
        st.session_state.last_answer_time[player_name.strip()] = time.time()
        # si completó la última pregunta, marcar tiempo final
        if player["preg"] >= TOTAL_QUESTIONS:
            player["fin"] = True
            player["tiempo"] = int(time.time() - inicio_global)
            st.session_state.jugadores[player_name.strip()] = player
            persist_player(player_name.strip())
        st.experimental_rerun()

# Mostrar barra solo del jugador
progreso_vis = player.get("points", 0) / MAX_POINTS if MAX_POINTS > 0 else 0
barra_carretera_html_for_player(progreso_vis, width="90%")

st.markdown("</div>", unsafe_allow_html=True)

# Pie de página: nota
st.caption("El panel administrador está oculto por defecto. Marque 'Mostrar panel administrador' en la barra lateral para administrar la carrera (requiere login).")
