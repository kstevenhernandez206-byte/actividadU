# carrera.py — Versión final integrada
# - Admin oculto en sidebar (abrir mediante checkbox)
# - Auditoría con filtro por persona
# - Tiempo mostrado solo si el jugador terminó (formato MM:SS)
# - Vista de jugador simplificada (sin "Carrera en vivo" ni "Tu progreso" global)
# - 12 preguntas, 20s por pregunta, 10 ptos/Correct, meta 50 pts

import streamlit as st
import time
import pandas as pd
import os
import json
from datetime import timedelta

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
# Preguntas (12)
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
# Parámetros
# ---------------------------
QUESTION_TIME = 20
POINTS_PER_CORRECT = 10
POINTS_TO_FINISH = 50

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

# ---------------------------
# Estado en session
# ---------------------------
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()

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
        "aciertos": 0,
        "preg": 0,
        "fin": False,
        "tiempo": None,
        "joined": time.time()
    })
    save_state(fs)
    # sync session state
    st.session_state.jugadores[name] = fs["players_info"][name]

def reset_all():
    save_state({"inicio": None, "jugadores": [], "players_info": {}, "organizer": None})
    save_answers([])
    st.session_state.jugadores = {}
    st.session_state.answers = []

# ---------------------------
# Barra carretera HTML (carrito)
# ---------------------------
def barra_carretera_html(progreso, width="100%"):
    porcentaje = max(0.0, min(1.0, float(progreso))) * 100
    left_percent = max(2, min(98, porcentaje))  # keep car visible
    html = f"""
    <div style="position:relative;width:{width};height:36px;background:#222;border-radius:10px;padding:4px;overflow:hidden;">
        <div style="position:absolute;left:0;top:0;height:100%;width:{porcentaje}%;background:rgba(34,197,94,0.18);border-radius:8px;"></div>
        <div style="position:absolute;left:{left_percent}%;top:3px;font-size:22px;transform:translateX(-50%);transition:left .4s ease;">🚗</div>
        <div style="position:absolute;right:8px;top:6px;font-size:18px;">🏁</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Página
# ---------------------------
st.set_page_config(page_title="Carrera", layout="wide")

# ---------- Sidebar: control para mostrar Admin ----------
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")
# Note: panel admin hidden by default; when checked, login/auth appears.

# ---------- Admin area (hidden until checkbox) ----------
if show_admin:
    st.sidebar.header("Administrador")
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_user = st.sidebar.text_input("Usuario (admin)")
        admin_pass = st.sidebar.text_input("Contraseña (admin)", type="password")
        if st.sidebar.button("Iniciar sesión como admin"):
            # Cambia credenciales aquí si quieres
            if admin_user == "Grupo5" and admin_pass == "2025":
                st.session_state.admin_authenticated = True
                st.sidebar.success("Autenticado como admin")
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        # Admin authenticated: show full admin controls
        fs = ensure_state_keys(load_state())

        # Organizer name
        organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")

        # Players connected table
        st.sidebar.markdown("### 👥 Jugadores conectados")
        players_list = []
        for name, info in fs.get("players_info", {}).items():
            joined_ts = info.get("joined", None)
            joined_str = time.strftime("%H:%M:%S", time.localtime(joined_ts)) if joined_ts else "—"
            players_list.append({
                "Jugador": name,
                "Aciertos": info.get("aciertos", 0),
                "Puntos": info.get("points", 0),
                "Conectado": joined_str
            })
        if players_list:
            df_players = pd.DataFrame(players_list).sort_values("Conectado")
            st.sidebar.dataframe(df_players, height=220)
        else:
            st.sidebar.info("No hay jugadores conectados")

        st.sidebar.markdown("---")
        # Start race
        if st.sidebar.button("🚀 Iniciar carrera (confirmar todos conectados)"):
            if not organizer.strip():
                st.sidebar.warning("Ingrese el nombre del organizador antes de iniciar.")
            else:
                fs["inicio"] = time.time()
                fs["organizer"] = organizer
                save_state(fs)
                st.sidebar.success("Carrera iniciada")

        # Reset
        if st.sidebar.button("🧹 Limpiar TODOS los registros"):
            reset_all()
            st.sidebar.success("Registros limpiados")

        st.sidebar.markdown("---")
        # ----- Auditoría (filterable) -----
        st.sidebar.markdown("### 🗂 Auditoría (respuestas)")
        answers = load_answers()
        if answers:
            # list unique players
            nombres = sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")}))
            nombres = [n for n in nombres if n]
            selected = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + nombres)
            # build df
            df_a = pd.DataFrame(answers)
            # convert timestamp to readable
            if "timestamp" in df_a.columns:
                df_a = df_a.copy()
                df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            # apply filter
            if selected and selected != "(Todos)":
                df_a = df_a[df_a["jugador"] == selected]
            # show limited columns
            cols_to_show = []
            if "hora" in df_a.columns:
                cols_to_show.append("hora")
            for col in ["jugador", "pregunta_idx", "selected", "correct"]:
                if col in df_a.columns:
                    cols_to_show.append(col)
            if cols_to_show:
                st.sidebar.dataframe(df_a[cols_to_show].sort_values(by="hora", ascending=False).reset_index(drop=True), height=220)
                csv = df_a[cols_to_show].to_csv(index=False).encode("utf-8")
                st.sidebar.download_button("Exportar auditoría (CSV)", data=csv, file_name="auditoria.csv", mime="text/csv")
            else:
                st.sidebar.info("No hay columnas de auditoría para mostrar.")
        else:
            st.sidebar.info("No hay registros de auditoría aún.")

        st.sidebar.markdown("---")
        # ----- Top 3 and global progress (admin only) -----
        st.sidebar.markdown("## 🏆 Top 3 (global)")
        fs2 = ensure_state_keys(load_state())
        ranking_arr = []
        for n, info in fs2.get("players_info", {}).items():
            tiempo_val = info.get("tiempo", None)
            ranking_arr.append({
                "Jugador": n,
                "Puntos": info.get("points", 0),
                "Aciertos": info.get("aciertos", 0),
                "Tiempo_raw": tiempo_val  # store raw for sorting
            })
        if ranking_arr:
            df_r = pd.DataFrame(ranking_arr)
            # sorting: map non-int time to large number so unfinished go below
            def map_time_for_sort(x):
                return x if (isinstance(x, int) or isinstance(x, float)) else 999999
            df_r = df_r.sort_values(by=["Puntos", "Tiempo_raw"], ascending=[False, True], key=lambda col: col.map(map_time_for_sort) if col.name=="Tiempo_raw" else col)
            # Add formatted time column
            df_r["Tiempo"] = df_r["Tiempo_raw"].apply(lambda t: format_seconds_to_mmss(t) if (t is not None) else "—")
            st.sidebar.table(df_r[["Jugador", "Puntos", "Aciertos", "Tiempo"]].head(3))
            st.sidebar.markdown("## 🌍 Progreso global")
            for row in df_r.itertuples(index=False):
                progreso = min(row.Puntos / POINTS_TO_FINISH, 1.0) if POINTS_TO_FINISH>0 else 0
                st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
                barra_carretera_html(progreso, width="100%")
        else:
            st.sidebar.info("No hay ranking aún.")

# ---------- Main (Jugador) ----------
st.header("Jugador")
nombre = st.text_input("Ingresa tu nombre para unirte:", key="player_name_input")

if nombre and nombre.strip():
    add_player(nombre.strip())

# Show global status (simple)
fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)
if inicio_global:
    tiempo_total = QUESTION_TIME * len(questions)
    tiempo_pasado = int(time.time() - inicio_global)
    tiempo_rest = max(0, tiempo_total - tiempo_pasado)
    st.info(f"⏳ Tiempo global restante: {tiempo_rest} s")
else:
    st.info("⏳ Esperando que el organizador inicie la carrera...")

# If player entered name -> show quiz (no big progress blocks)
if nombre and nombre.strip():
    jugador = st.session_state.jugadores.get(nombre.strip())
    if not jugador:
        st.warning("Registro pendiente; intenta recargar la página.")
    else:
        # show question only if started and time remains and not finished
        if inicio_global and tiempo_rest > 0 and not jugador.get("fin", False):
            idx = jugador.get("preg", 0) % len(questions)
            qdata = questions[idx]
            st.subheader(f"Pregunta #{idx+1}")
            st.write(qdata["q"])
            selection = st.radio("Selecciona una opción:", qdata["options"], key=f"radio_{nombre.strip()}_{idx}")
            if st.button("Enviar respuesta", key=f"submit_{nombre.strip()}_{idx}"):
                correcto = selection == qdata["correct"]
                entry = {
                    "timestamp": int(time.time()),
                    "jugador": nombre.strip(),
                    "pregunta_idx": idx,
                    "selected": selection,
                    "correct": correcto
                }
                append_answer(entry)
                if correcto:
                    st.success("✅ Correcto (+10 pts)")
                    jugador["points"] = jugador.get("points", 0) + POINTS_PER_CORRECT
                    jugador["aciertos"] = jugador.get("aciertos", 0) + 1
                else:
                    st.error("❌ Incorrecto")
                jugador["preg"] = jugador.get("preg", 0) + 1
                # check finish
                if jugador.get("points", 0) >= POINTS_TO_FINISH:
                    jugador["fin"] = True
                    jugador["tiempo"] = int(time.time() - inicio_global)
                    st.balloons()
                    st.success("🏁 ¡Llegaste a la meta!")
                # persist player state
                fs_p = ensure_state_keys(load_state())
                fs_p.setdefault("players_info", {})
                fs_p["players_info"][nombre.strip()] = jugador
                if nombre.strip() not in fs_p.get("jugadores", []):
                    fs_p.setdefault("jugadores", []).append(nombre.strip())
                save_state(fs_p)
        else:
            if not inicio_global:
                st.info("La carrera no ha iniciado. Espera al organizador.")
            elif jugador.get("fin", False):
                st.success("Has terminado la carrera. ¡Buen trabajo!")
                if jugador.get("tiempo") is not None:
                    st.info(f"Tiempo total: {format_seconds_to_mmss(jugador.get('tiempo'))}")
            else:
                st.warning("Tiempo global finalizado o no disponible.")

# ---------- TOP & PROGRESO visible en MAIN? (we keep main minimal per request)
# The Top3 and global progress are intentionally *only* in admin sidebar (when admin opens it).
# If you want to also show a small top3 in the main area, we can add it here — currently omitted.

# Footer: small help
st.caption("Nota: El panel administrador está oculto por defecto. Marca 'Mostrar panel administrador' en la barra lateral para acceder a controles y auditoría (requiere login admin).")
