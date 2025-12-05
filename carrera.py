# carrera.py — Versión FINAL con autorefresh (0.5s), 8 preguntas, 60s por pregunta
# Opción C: Admin oculto, auditoría filtrable, top3 y progreso global en admin.
# Nota: requiere instalar: pip install streamlit-autorefresh

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import pandas as pd
import os
import json

# =========================
# Configuración inicial
# =========================
st.set_page_config(page_title="Carrera", layout="wide")
# Auto-refresh cada 500 ms (0.5 s) — **SIEMPRE** activo (tal como pediste)
st_autorefresh(interval=500, key="auto_refresh")

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

# =========================
# Parámetros de la carrera
# =========================
QUESTION_TIME = 60               # 60 segundos por pregunta
POINTS_PER_CORRECT = 10
POINTS_TO_FINISH = 50

# =========================
# Preguntas (8 seleccionadas)
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

TOTAL_TIME = QUESTION_TIME * len(questions)  # tiempo total de la sesión

# =========================
# Helpers / utilidades
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

# Barra visual tipo pista (HTML)
def barra_carretera_html(progreso, width="100%"):
    porcentaje = max(0.0, min(1.0, float(progreso))) * 100
    left = max(2, min(98, porcentaje))
    html = f'''
    <div style="position:relative;width:{width};height:36px;background:#222;border-radius:10px;padding:4px;overflow:hidden;">
      <div style="position:absolute;left:0;top:0;height:100%;width:{porcentaje}%;background:rgba(34,197,94,0.18);border-radius:8px;"></div>
      <div style="position:absolute;left:{left}%;top:3px;font-size:22px;transform:translateX(-50%);transition:left .35s ease;">🚗</div>
      <div style="position:absolute;right:8px;top:6px;font-size:18px;">🏁</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

# =========================
# Estado en memoria (session)
# =========================
if "jugadores" not in st.session_state:
    st.session_state.jugadores = {}
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()

# -------------------------
# Funciones de jugador/admin
# -------------------------
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

# =========================
# UI: Sidebar (Admin hidden by checkbox)
# =========================
show_admin = st.sidebar.checkbox("🔐 Mostrar panel administrador")

if show_admin:
    st.sidebar.header("Administrador")
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_user = st.sidebar.text_input("Usuario (admin)")
        admin_pass = st.sidebar.text_input("Contraseña (admin)", type="password")
        if st.sidebar.button("Iniciar sesión como admin"):
            # credenciales por defecto (modificar si deseas)
            if admin_user == "Grupo5" and admin_pass == "2025":
                st.session_state.admin_authenticated = True
                st.sidebar.success("Autenticado como admin")
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        fs = ensure_state_keys(load_state())

        organizer = st.sidebar.text_input("Nombre de quien inicia el programa:", value=fs.get("organizer") or "")

        st.sidebar.markdown("### 👥 Jugadores conectados")
        players_list = []
        for name, info in fs.get("players_info", {}).items():
            joined_ts = info.get("joined")
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
            nombres = sorted(list({a.get("jugador","") for a in answers if a.get("jugador","")}))
            selected = st.sidebar.selectbox("Filtrar por jugador", ["(Todos)"] + nombres)
            df_a = pd.DataFrame(answers)
            if "timestamp" in df_a.columns:
                df_a = df_a.copy()
                df_a["hora"] = pd.to_datetime(df_a["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            if selected and selected != "(Todos)":
                df_a = df_a[df_a["jugador"] == selected]
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
                st.sidebar.info("Sin columnas de auditoría para mostrar.")
        else:
            st.sidebar.info("No hay registros de auditoría aún.")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🏆 Top 3 (global)")
        fs2 = ensure_state_keys(load_state())
        ranking_arr = []
        for n, info in fs2.get("players_info", {}).items():
            ranking_arr.append({
                "Jugador": n,
                "Puntos": info.get("points", 0),
                "Aciertos": info.get("aciertos", 0),
                "Tiempo_raw": info.get("tiempo", None)
            })
        if ranking_arr:
            df_r = pd.DataFrame(ranking_arr)
            # ordenar: no-int tiempo => valor grande para que queden al final
            df_r = df_r.sort_values(
                by=["Puntos", "Tiempo_raw"],
                ascending=[False, True],
                key=lambda col: col.map(lambda x: x if (isinstance(x, int) or isinstance(x,float)) else 999999)
            )
            df_r["Tiempo"] = df_r["Tiempo_raw"].apply(lambda t: format_seconds_to_mmss(t) if (t is not None) else "—")
            st.sidebar.table(df_r[["Jugador", "Puntos", "Aciertos", "Tiempo"]].head(3))

            st.sidebar.markdown("## 🌍 Progreso global")
            for row in df_r.itertuples(index=False):
                progreso = min(row.Puntos / POINTS_TO_FINISH, 1.0) if POINTS_TO_FINISH>0 else 0
                st.sidebar.write(f"**{row.Jugador}** — {row.Puntos} pts")
                barra_carretera_html(progreso, width="100%")
        else:
            st.sidebar.info("No hay ranking aún.")

# =========================
# Main: área del jugador (simplificada)
# =========================
st.header("Jugador")
nombre = st.text_input("Ingresa tu nombre para unirte:", key="player_name_input")

if nombre and nombre.strip():
    add_player(nombre.strip())

fs_main = ensure_state_keys(load_state())
inicio_global = fs_main.get("inicio", None)

if inicio_global:
    tiempo_total = QUESTION_TIME * len(questions)
    tiempo_pasado = int(time.time() - inicio_global)
    tiempo_rest = max(0, tiempo_total - tiempo_pasado)
    st.info(f"⏳ Tiempo global restante: {tiempo_rest} s")
else:
    st.info("⏳ Esperando que el organizador inicie la carrera...")

# Mostrar pregunta y manejar respuestas
if nombre and nombre.strip():
    jugador = st.session_state.jugadores.get(nombre.strip())
    if not jugador:
        st.warning("Registro pendiente; recarga la página si no aparece.")
    else:
        if inicio_global and tiempo_rest > 0 and not jugador.get("fin", False):
            idx = jugador.get("preg", 0) % len(questions)
            qdata = questions[idx]
            st.subheader(f"Pregunta #{idx+1}")
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
                    st.success("✅ Correcto (+10 pts)")
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
                # persistir jugador
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

# Nota: Top3 y progreso global están disponibles en el panel admin (cuando lo muestras).
st.caption("El panel administrador está oculto por defecto. Marca 'Mostrar panel administrador' en la barra lateral para acceder a los controles y auditoría (requiere login admin).")
