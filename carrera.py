import streamlit as st
import random
import time
import pandas as pd
import os
import json

# Archivos para estado compartido y respuestas (globales)
BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, 'state.json')
ANSWERS_FILE = os.path.join(BASE_DIR, 'answers.json')

def load_state():
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'inicio': None, 'jugadores': [], 'players_info': {}}

def save_state(s):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(s, f)

def load_answers():
    try:
        with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_answers(a):
    with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(a, f)

def append_answer(entry):
    a = load_answers()
    a.append(entry)
    save_answers(a)

# Función para simular jugadores (añade al state.json y al session_state)
def simulate_players(names):
    file_state = load_state()
    names_list = [n.strip() for n in names.split(',') if n.strip()]
    for n in names_list:
        if n not in file_state.get('jugadores', []):
            file_state.setdefault('jugadores', []).append(n)
            file_state.setdefault('players_info', {})[n] = {"pos": 0, "preg": 0, "aciertos": 0, "tiempo": 0, "fin": False, "points": 0}
            # actualizar estado local inmediato
            st.session_state.jugadores[n] = file_state['players_info'][n]
    save_state(file_state)

# Cuestionario proporcionado por el usuario (selección múltiple)
questions = [
    {"q": "¿Cuál es el propósito central de la inteligencia artificial según Russell y Norvig (2021)?",
     "options": ["Crear máquinas que imiten emociones humanas", "Construir agentes capaces de actuar racionalmente en un entorno", "Sustituir completamente al ser humano en el trabajo", "Generar entretenimiento digital"],
     "correct": "Construir agentes capaces de actuar racionalmente en un entorno"},

    {"q": "¿Qué característica define a los sistemas cibernéticos según Wiener (2019)?",
     "options": ["Su capacidad de almacenar grandes volúmenes de datos", "Su funcionamiento basado en retroalimentación y control", "Su dependencia exclusiva de supervisión humana", "Su uso limitado a la biología"],
     "correct": "Su funcionamiento basado en retroalimentación y control"},

    {"q": "¿Cuál es uno de los principales riesgos de los sistemas cibernéticos autónomos?",
     "options": ["La reducción de costos operativos", "La pérdida de retroalimentación", "Los fallos en cascada y accesos no autorizados", "La falta de algoritmos de recomendación"],
     "correct": "Los fallos en cascada y accesos no autorizados"},

    {"q": "Según Brynjolfsson y McAfee (2016), la automatización laboral genera principalmente:",
     "options": ["Mayor demanda de tareas manuales simples", "Incremento en la eficiencia y productividad", "Eliminación total de la desigualdad social", "Reducción de la necesidad de competencias digitales"],
     "correct": "Incremento en la eficiencia y productividad"},

    {"q": "¿Qué problema ético se destaca en la inteligencia artificial según Jobin, Ienca y Vayena (2019)?",
     "options": ["La falta de conectividad en zonas rurales", "El sesgo algorítmico en la toma de decisiones", "La escasez de dispositivos móviles", "La ausencia de plataformas educativas"],
     "correct": "El sesgo algorítmico en la toma de decisiones"},

    {"q": "Castells (2013) afirma que la comunicación en red es el espacio donde se construyen:",
     "options": ["Relaciones de poder, identidad y participación social", "Exclusivamente vínculos familiares", "Procesos de producción industrial", "Sistemas de entretenimiento digital"],
     "correct": "Relaciones de poder, identidad y participación social"},

    {"q": "¿Por qué las redes sociales se consideran sistemas cibernéticos según Tufekci (2015)?",
     "options": ["Porque funcionan únicamente como medios de entretenimiento", "Porque operan mediante retroalimentación entre usuarios, algoritmos y flujos de información", "Porque no influyen en la opinión pública", "Porque carecen de algoritmos de recomendación"],
     "correct": "Porque operan mediante retroalimentación entre usuarios, algoritmos y flujos de información"},

    {"q": "Wardle y Derakhshan (2017) denominan al fenómeno de la desinformación digital como:",
     "options": ["Fake news", "Information disorder", "Data overload", "Digital misinformation"],
     "correct": "Information disorder"},

    {"q": "Según la UNESCO (2021), uno de los factores clave para lograr inclusión digital es:",
     "options": ["La concentración de poder tecnológico en grandes empresas", "La alfabetización tecnológica y la accesibilidad", "La reducción de costos de producción industrial", "La eliminación de las redes sociales"],
     "correct": "La alfabetización tecnológica y la accesibilidad"},

    {"q": "En las conclusiones del trabajo, se afirma que para garantizar un uso inclusivo de la tecnología es necesario:",
     "options": ["Promover estrategias de accesibilidad, acompañamiento y formación continua", "Eliminar la inteligencia artificial de los procesos sociales", "Limitar el acceso a redes sociales", "Reducir la inversión en conectividad digital"],
     "correct": "Promover estrategias de accesibilidad, acompañamiento y formación continua"},
]

META = 5  # Número de preguntas/metros para llegar a la meta
QUESTION_TIME = 15  # segundos por pregunta
# Ajustar tiempo total: 15s por pregunta, tomar máximo 10 preguntas para total=150s
TIEMPO_LIMITE = QUESTION_TIME * min(len(questions), 10)

# Inicializar estado local y sincronizar con archivos compartidos
file_state = load_state()

# Cargar/crear jugadores locales según el archivo global
if "jugadores" not in st.session_state:
    # players_info contiene detalles por jugador (si existe)
    players_info = file_state.get('players_info', {})
    # convertir a la estructura de st.session_state.jugadores
    st.session_state.jugadores = {}
    for name, info in players_info.items():
        st.session_state.jugadores[name] = info

# Inicializar inicio desde el archivo compartido
if "inicio" not in st.session_state:
    st.session_state.inicio = file_state.get('inicio')

# Registro de respuestas (logs) — cargar desde answers.json
if "answers" not in st.session_state:
    st.session_state.answers = load_answers()

st.title("🏁 Carrera de Conocimientos Multijugador")

# Autorefresh global para actualizar la cuenta regresiva cada segundo (opcional)
try:
    from streamlit_autorefresh import st_autorefresh
    st.session_state['use_autorefresh'] = True
except Exception:
    st.session_state['use_autorefresh'] = False
    st.caption("Opcional: instala 'streamlit-autorefresh' para ver la cuenta regresiva en vivo (pip install streamlit-autorefresh)")

# Mostrar login de admin en la pantalla inicial (antes de que los jugadores ingresen nombre)
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

st.markdown('---')
st.markdown('### Área de administración (sólo para el organizador)')
# campos de admin en la parte superior
admin_user_top = st.text_input('Usuario (admin):', key='admin_user_top')
admin_pass_top = st.text_input('Contraseña (admin):', type='password', key='admin_pass_top')
if st.button('Iniciar sesión como admin (pantalla principal)', key='admin_login_top'):
    if admin_user_top == 'Grupo5' and admin_pass_top == '2025':
        st.session_state.admin_authenticated = True
        st.success('Autenticado como admin')
        # recargar estado y permitir iniciar
        file_state = load_state()
    else:
        st.session_state.admin_authenticated = False
        st.error('Credenciales incorrectas')

# Si está autenticado, mostrar control de inicio aquí también
if st.session_state.get('admin_authenticated', False):
    st.markdown('**Controles de admin**')
    file_state = load_state()
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button('Iniciar carrera (confirmar todos conectados)'):
            file_state['inicio'] = time.time()
            save_state(file_state)
            st.session_state.inicio = file_state['inicio']
            st.success('Carrera iniciada (valor compartido guardado)')
    with col2:
        if st.button('Resetear estado (borrar jugadores e inicio)'):
            file_state = {'inicio': None, 'jugadores': [], 'players_info': {}}
            save_state(file_state)
            save_answers([])
            st.session_state.jugadores = {}
            st.session_state.answers = []
            st.session_state.inicio = None
            st.success('Estado reiniciado')

    # controles de simulación para pruebas locales
    st.markdown('**Simulación / pruebas**')
    sim_names = st.text_input('Nombres simulados (coma-sep):', key='sim_names')
    if st.button('Simular jugadores', key='admin_simulate'):
        if sim_names.strip():
            simulate_players(sim_names)
            st.success('Jugadores simulados añadidos')
        else:
            simulate_players('Alice,Bob,Carlos')
            st.success('Jugadores de prueba añadidos')

    # opción de ocultar panel lateral para que los jugadores no vean controles
    hide_side = st.checkbox('Ocultar panel lateral de admin (para jugadores)', value=True, key='hide_sidebar_admin')

st.markdown('---')

nombre = st.text_input("Ingresa tu nombre para unirte a la carrera:")

if nombre:
    # sincronizar con archivo global: registrar jugador si es nuevo
    file_state = load_state()
    if nombre not in file_state.get('jugadores', []):
        file_state.setdefault('jugadores', []).append(nombre)
        file_state.setdefault('players_info', {})[nombre] = {"pos": 0, "preg": 0, "aciertos": 0, "tiempo": 0, "fin": False, "points": 0}
        save_state(file_state)

    # asegurar estado local para el jugador (cargar desde file_state si existe)
    if nombre not in st.session_state.jugadores:
        st.session_state.jugadores[nombre] = file_state.get('players_info', {}).get(nombre, {"pos": 0, "preg": 0, "aciertos": 0, "tiempo": 0, "fin": False, "points": 0})

    # actualizar inicio local con el valor global (si admin inició la carrera)
    st.session_state.inicio = file_state.get('inicio')

    jugador = st.session_state.jugadores[nombre]

    # Ya no mostramos botón de inicio para cada usuario. El admin debe iniciar la carrera desde la barra lateral.
    if st.session_state.inicio is None:
        st.info("Esperando a que el admin inicie la carrera una vez que todos se hayan unido.")

    if st.session_state.inicio:
        # Usar streamlit-autorefresh si está disponible para reruns cada segundo
        if st.session_state.get('use_autorefresh', False) and not all(j.get('fin', False) for j in st.session_state.jugadores.values()):
            try:
                st_autorefresh(interval=1000, key="global_autorefresh")
            except Exception:
                pass
        else:
            # Fallback: recarga completa del cliente cada segundo (menos eficiente)
            if not all(j.get('fin', False) for j in st.session_state.jugadores.values()):
                reload_js = """
                <script>
                setTimeout(function(){ window.location.reload(); }, 1000);
                </script>
                """
                st.components.v1.html(reload_js, height=0)

        tiempo_restante = max(0, TIEMPO_LIMITE - int(time.time() - st.session_state.inicio))
        st.info(f"⏰ Tiempo restante: {tiempo_restante} segundos")

        if tiempo_restante == 0:
            st.warning("¡Tiempo terminado!")
        else:
            # Pregunta actual del jugador (selección múltiple)
            if not jugador["fin"]:
                q_idx = jugador["preg"] % len(questions)
                pregunta = questions[q_idx]

                # clave dinámica para control de estado y temporizador
                key_name = f"{nombre}_q_{jugador['preg']}"
                start_key = key_name + "_start"
                if start_key not in st.session_state:
                    st.session_state[start_key] = time.time()
                    # resetear flag de timeout al iniciar nueva pregunta
                    jugador['timeout'] = False

                elapsed = int(time.time() - st.session_state[start_key])
                remaining = max(0, QUESTION_TIME - elapsed)

                # Visual del temporizador grande (solo si está en la pregunta activa)
                if not jugador.get('await_continue', False):
                    st.markdown(f"### ⏱ Tiempo para responder: {remaining} s")

                # Etiquetar opciones como a), b), c), d)
                options_labeled = [f"{chr(97+i)}) {opt}" for i, opt in enumerate(pregunta["options"]) ]

                # Si estamos en espera de 'Continuar', ocultar la pregunta y mostrar sólo el botón grande
                continue_key = key_name + "_continue"
                if jugador.get('await_continue', False):
                    last_msg = "Has respondido correctamente." if jugador.get('last_correct', False) else "Respuesta incorrecta."
                    st.markdown(f"### {last_msg}")
                    st.markdown("<div style='margin:20px 0; text-align:center;'>", unsafe_allow_html=True)
                    if st.button('Continuar', key=key_name + '_cont_button'):
                        jugador['await_continue'] = False
                        jugador['preg'] += 1
                        # limpiar claves de temporizador
                        if start_key in st.session_state:
                            del st.session_state[start_key]
                        if continue_key in st.session_state:
                            del st.session_state[continue_key]
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    # Mostrar la pregunta y opciones normalmente
                    with st.form(key=f"form_{key_name}"):
                        choice_label = st.radio(pregunta["q"], options_labeled, key=key_name + "_choice")
                        enviar = st.form_submit_button("Responder")

                    # Procesar respuesta (comparar por texto real de la opción)
                    if remaining == 0 and not jugador.get("timeout", False):
                        jugador["timeout"] = True  # Marcar como timeout para no procesar respuesta
                        st.warning("Se agotó el tiempo para esta pregunta. No obtuviste puntos.")
                        # registrar intento sin respuesta
                        entry = {
                            'timestamp': time.time(),
                            'jugador': nombre,
                            'pregunta_idx': q_idx,
                            'selected': None,
                            'correct': False,
                            'timeout': True
                        }
                        st.session_state.answers.append(entry)
                        append_answer(entry)
                        jugador["preg"] += 1
                        # limpiar inicio para la siguiente pregunta
                        del st.session_state[start_key]
                    elif enviar and remaining > 0:
                        # extraer texto real después de 'a) '
                        selected_text = choice_label.split(') ', 1)[1] if isinstance(choice_label, str) else choice_label
                        correct = (selected_text == pregunta["correct"])
                        # registrar respuesta
                        entry = {
                            'timestamp': time.time(),
                            'jugador': nombre,
                            'pregunta_idx': q_idx,
                            'selected': selected_text,
                            'correct': correct,
                            'timeout': False
                        }
                        st.session_state.answers.append(entry)
                        append_answer(entry)
                        if correct:
                            st.success("¡Correcto! +10 puntos 🚗💨")
                            jugador["points"] = jugador.get("points", 0) + 10
                            jugador["aciertos"] += 1
                        else:
                            st.error("Incorrecto. 0 puntos.")

                        # En lugar de avanzar inmediatamente, mostrar botón "Continuar" y dar 10s ocultos
                        jugador['await_continue'] = True
                        jugador['last_correct'] = correct
                        if continue_key not in st.session_state:
                            st.session_state[continue_key] = time.time()

                # Si estamos esperando al usuario para que haga 'Continuar'
                # ...continuación manejada más arriba: evitamos crear el botón duplicado aquí para no repetir la clave.

                # Mostrar progreso visual
                points_required = META * 10
                pts = jugador.get("points", 0)
                progreso = min(pts / points_required, 1.0)
                st.progress(progreso)
                st.write(f"Puntos: {pts} / {points_required}")

                # Mostrar pista de carrera más visual
                posiciones = []
                for nombre_j, info in st.session_state.jugadores.items():
                    # convertir puntos a avance en metros (cada 10 pts = 1 unidad)
                    avance_units = info.get("points", 0) // 10
                    avance = "🚗" + "—" * int(avance_units) + ("🏁" if info.get("points", 0) >= points_required else "")
                    posiciones.append((avance_units, nombre_j, avance))
                posiciones.sort(reverse=True)
                for pos, nombre_j, avance in posiciones:
                    st.write(f"{nombre_j}: {avance}")

                # Si alcanza puntos necesarios, marcar fin
                if jugador.get("points", 0) >= points_required:
                    jugador["fin"] = True
                    jugador["tiempo"] = int(time.time() - st.session_state.inicio)
                    st.balloons()
                    st.success("¡Llegaste a la meta con puntos suficientes!")

            else:
                st.info(f"Esperando a que terminen los demás. Tiempo restante de la sesión: {tiempo_restante} s")

        # Mostrar top/ranking actual siempre (tabla)
        ranking_table = []
        for nombre_j, info in st.session_state.jugadores.items():
            ranking_table.append({
                'Jugador': nombre_j,
                'Puntos': info.get('points', 0),
                'Aciertos': info.get('aciertos', 0),
                'Tiempo': info.get('tiempo', 0)
            })
        if ranking_table:
            df = pd.DataFrame(ranking_table)
            df = df.sort_values(by=['Puntos', 'Tiempo'], ascending=[False, True]).reset_index(drop=True)
            df.index += 1
            st.subheader('🏆 Top jugadores (actual)')
            st.table(df.head(20))

        # Vista admin: registros de respuestas con login (mejorada: filtro por jugador)
        st.sidebar.subheader('Admin')
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False
        # Mostrar login lateral sólo si no está autenticado desde la parte superior
        if not st.session_state.get('admin_authenticated', False):
            admin_user = st.sidebar.text_input('Usuario (admin):', key='admin_user')
            admin_pass = st.sidebar.text_input('Contraseña (admin):', type='password', key='admin_pass')
            if st.sidebar.button('Iniciar sesión', key='admin_login_btn'):
                if admin_user == 'Grupo5' and admin_pass == '2025':
                    st.session_state.admin_authenticated = True
                    st.sidebar.success('Autenticado como admin')
                else:
                    st.session_state.admin_authenticated = False
                    st.sidebar.error('Credenciales incorrectas')
        else:
            # si el admin ha ocultado el panel lateral, mostrar aviso mínimo
            if st.session_state.get('hide_sidebar_admin', False):
                st.sidebar.info('Admin autenticado. Panel lateral oculto por el organizador.')
            else:
                st.sidebar.markdown('Admin autenticado desde la pantalla principal.')

        if st.session_state.get('admin_authenticated', False):
            # cargar estado de archivo para opciones administrativas
            file_state = load_state()
            st.sidebar.markdown('**Panel de auditoría (jugador, pregunta, hora, respuesta)**')
            logs = st.session_state.get('answers', [])

            # Botón de inicio global (admin)
            if st.sidebar.button('Iniciar carrera (confirmar todos conectados)', key='admin_start_btn'):
                file_state['inicio'] = time.time()
                save_state(file_state)
                st.session_state.inicio = file_state['inicio']
                st.sidebar.success('Carrera iniciada (valor compartido guardado)')

            # lista de jugadores para filtro (del estado global y de los logs)
            players_from_state = list(file_state.get('jugadores', []))
            players_from_logs = sorted({entry['jugador'] for entry in logs}) if logs else []
            players = sorted(set(players_from_state + players_from_logs))
            players.insert(0, 'Todos')

            selected_player = st.sidebar.selectbox('Filtrar por jugador', players, index=0)

            if logs:
                df_logs = pd.DataFrame(logs)
                df_display = df_logs[['timestamp', 'jugador', 'pregunta_idx', 'selected']].copy()
                df_display['timestamp'] = pd.to_datetime(df_display['timestamp'], unit='s')
                df_display = df_display.rename(columns={
                    'timestamp': 'Hora',
                    'jugador': 'Jugador',
                    'pregunta_idx': 'Nro_pregunta',
                    'selected': 'Respuesta'
                })

                if selected_player != 'Todos':
                    df_display = df_display[df_display['Jugador'] == selected_player]

                st.sidebar.write(df_display)

                # exportar CSV (filtrado)
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.sidebar.download_button('Exportar auditoría (CSV)', data=csv, file_name=f'auditoria_{selected_player}.csv', mime='text/csv')

                # limpiar registros (por jugador o global)
                if st.sidebar.button('Limpiar registros del jugador seleccionado', key='admin_clear_player'):
                    if selected_player == 'Todos':
                        st.session_state['answers'] = []
                        save_answers([])
                    else:
                        st.session_state['answers'] = [r for r in st.session_state['answers'] if r.get('jugador') != selected_player]
                        save_answers(st.session_state['answers'])
                    st.sidebar.success('Registros limpiados (según filtro)')

                if st.sidebar.button('Limpiar todos los registros', key='admin_clear_all'):
                    st.session_state['answers'] = []
                    save_answers([])
                    st.sidebar.success('Todos los registros limpiados')

            else:
                st.sidebar.write('No hay registros aún.')
        else:
            st.sidebar.info('Inicia sesión para ver la auditoría')

        # Ranking final
        if all(j["fin"] or tiempo_restante == 0 for j in st.session_state.jugadores.values()):
            st.subheader("🏆 Ranking final")
            ranking = sorted(st.session_state.jugadores.items(), key=lambda x: (-x[1].get("points", 0), x[1]["tiempo"]))
            for i, (nombre_j, info) in enumerate(ranking, 1):
                st.write(f"{i}. {nombre_j} - Puntos: {info.get('points',0)} - Tiempo: {info['tiempo']} s - Aciertos: {info['aciertos']}")
else:
    st.info("Ingresa tu nombre para unirte.")

st.caption("Prototipo básico de carrera multijugador en Streamlit. Puedes personalizar las preguntas y la lógica a tu gusto.")
