from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import sqlite3
import os

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_RAIZ = os.path.dirname(CARPETA_ACTUAL)  # Sube de backend/ a INTERFACES/
RUTA_BD = os.path.join(CARPETA_ACTUAL, 'sistema_pat.db')

app = Flask(__name__)
CORS(app)


def get_db():
    """Helper para abrir conexión y retornar conexión+cursor."""
    conn = sqlite3.connect(RUTA_BD)
    conn.row_factory = sqlite3.Row  # Permite acceder columnas por nombre
    return conn


# ─────────────────────────────────────────────
# SERVIR ARCHIVOS ESTÁTICOS (HTML, CSS, JS, Assets)
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return redirect('/paginas/login.html')


@app.route('/paginas/<path:filename>')
def serve_paginas(filename):
    return send_from_directory(os.path.join(CARPETA_RAIZ, 'paginas'), filename)


@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(CARPETA_RAIZ, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(CARPETA_RAIZ, 'js'), filename)


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(CARPETA_RAIZ, 'assets'), filename)


# ─────────────────────────────────────────────
# AUTENTICACIÓN
# ─────────────────────────────────────────────

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Correo y contraseña son requeridos'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, apellidos, email, rol, departamento_o_carrera, grupo_asignado "
            "FROM usuarios WHERE LOWER(email) = ? AND password = ?",
            (email, password)
        )
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            return jsonify({
                'success': True,
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'apellidos': usuario['apellidos'],
                'email': usuario['email'],
                'role': usuario['rol'],
                'departamento': usuario['departamento_o_carrera'],
                'grupo': usuario['grupo_asignado']
            })
        else:
            return jsonify({'success': False, 'message': 'Correo o contraseña incorrectos'}), 401

    except Exception as e:
        print(f"[ERROR /api/login] {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ─────────────────────────────────────────────
# USUARIOS (Panel Admin)
# ─────────────────────────────────────────────

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """Devuelve todos los usuarios registrados (sin contraseña)."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, apellidos, email, rol, departamento_o_carrera, grupo_asignado "
            "FROM usuarios ORDER BY rol, nombre"
        )
        rows = cursor.fetchall()
        conn.close()

        usuarios = [dict(r) for r in rows]
        return jsonify({'success': True, 'usuarios': usuarios})

    except Exception as e:
        print(f"[ERROR GET /api/usuarios] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener usuarios'}), 500


@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    """Crea un nuevo usuario desde el panel de administración."""
    data = request.get_json()
    nombre = (data.get('nombre') or '').strip()
    apellidos = (data.get('apellidos') or '').strip()
    email = (data.get('email') or '').strip().lower()
    rol = (data.get('rol') or '').strip()
    grupo = (data.get('grupo') or '').strip() or None
    carrera = (data.get('carrera') or '').strip() or None # NUEVO: Obtenemos la carrera

    if not all([nombre, apellidos, email, rol]):
        return jsonify({'success': False, 'message': 'Todos los campos base son requeridos'}), 400

    roles_validos = ['director-tutorias', 'director-carrera', 'docente-tutor', 'jefe-grupo']
    if rol not in roles_validos:
        return jsonify({'success': False, 'message': 'Rol no válido'}), 400

    if not email.endswith('@upfim.edu.mx'):
        return jsonify({'success': False, 'message': 'El correo debe ser @upfim.edu.mx'}), 400

    import datetime
    anio = datetime.datetime.now().year
    password_temp = (apellidos[:4].lower() + str(anio))

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE LOWER(email) = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Ya existe un usuario con ese correo'}), 409

        # NUEVO: Insertamos también el departamento_o_carrera
        cursor.execute(
            "INSERT INTO usuarios (nombre, apellidos, email, password, rol, grupo_asignado, departamento_o_carrera) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nombre, apellidos, email, password_temp, rol, grupo, carrera)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Usuario creado. Contraseña temporal: {password_temp}',
            'id': nuevo_id,
            'password_temp': password_temp
        }), 201

    except Exception as e:
        print(f"[ERROR POST /api/usuarios] {e}")
        return jsonify({'success': False, 'message': 'Error al crear usuario'}), 500


@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    """Elimina un usuario por ID (no permite borrar admins)."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT rol FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        if row['rol'] == 'admin':
            conn.close()
            return jsonify({'success': False, 'message': 'No se puede eliminar un administrador'}), 403

        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Usuario eliminado'})

    except Exception as e:
        print(f"[ERROR DELETE /api/usuarios/{usuario_id}] {e}")
        return jsonify({'success': False, 'message': 'Error al eliminar usuario'}), 500


# ─────────────────────────────────────────────
# DOCENTES
# ─────────────────────────────────────────────

@app.route('/api/docentes', methods=['GET'])
def listar_docentes():
    """Devuelve usuarios con rol docente-tutor. Acepta ?carrera=X para filtrar."""
    carrera = request.args.get('carrera')
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = (
            "SELECT id, nombre, apellidos, email, departamento_o_carrera "
            "FROM usuarios WHERE rol = 'docente-tutor'"
        )
        params = []
        if carrera:
            query += " AND departamento_o_carrera = ?"
            params.append(carrera)
        query += " ORDER BY nombre"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        docentes = [dict(r) for r in rows]
        return jsonify({'success': True, 'docentes': docentes})

    except Exception as e:
        print(f"[ERROR GET /api/docentes] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener docentes'}), 500


@app.route('/api/docentes', methods=['POST'])
def registrar_docente():
    """Registra un nuevo docente (crea usuario con rol docente-tutor)."""
    data = request.get_json()
    nombre = (data.get('nombre') or '').strip()
    apellidos = (data.get('apellidos') or '').strip()
    email = (data.get('email') or '').strip().lower()
    departamento = (data.get('departamento') or '').strip()

    if not all([nombre, apellidos, email, departamento]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    if not email.endswith('@upfim.edu.mx'):
        return jsonify({'success': False, 'message': 'El correo debe ser institucional (@upfim.edu.mx)'}), 400

    import datetime
    anio = datetime.datetime.now().year
    password_temp = apellidos[:4].lower() + str(anio)

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE LOWER(email) = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Ya existe un docente con ese correo'}), 409

        cursor.execute(
            "INSERT INTO usuarios (nombre, apellidos, email, password, rol, departamento_o_carrera) VALUES (?, ?, ?, ?, 'docente-tutor', ?)",
            (nombre, apellidos, email, password_temp, departamento)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Docente "{nombre} {apellidos}" registrado. Contraseña temporal: {password_temp}',
            'id': nuevo_id
        }), 201

    except Exception as e:
        print(f"[ERROR POST /api/docentes] {e}")
        return jsonify({'success': False, 'message': 'Error al registrar docente'}), 500


# ─────────────────────────────────────────────
# ASIGNACIONES (Director de Carrera)
# ─────────────────────────────────────────────

@app.route('/api/asignaciones', methods=['GET'])
def listar_asignaciones():
    """Devuelve asignaciones activas. Acepta ?carrera_id=X para filtrar."""
    carrera_id = request.args.get('carrera_id')
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT a.id, a.grupo, a.periodo, a.anio,
                   u.nombre || ' ' || u.apellidos AS tutor,
                   c.nombre AS carrera
            FROM asignaciones a
            JOIN usuarios u ON a.tutor_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
        """
        params = []
        if carrera_id:
            query += " WHERE a.carrera_id = ?"
            params.append(carrera_id)
        query += " ORDER BY a.anio DESC, a.grupo"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return jsonify({'success': True, 'asignaciones': [dict(r) for r in rows]})

    except Exception as e:
        print(f"[ERROR GET /api/asignaciones] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener asignaciones'}), 500


@app.route('/api/asignaciones', methods=['POST'])
def crear_asignacion():
    """Crea una nueva asignación tutor-grupo."""
    data = request.get_json()
    carrera_id = data.get('carrera_id')
    tutor_id = data.get('tutor_id')
    grupo = (data.get('grupo') or '').strip().upper()
    periodo = (data.get('periodo') or '').strip()
    anio = data.get('anio')

    if not all([carrera_id, tutor_id, grupo, periodo, anio]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Verificar que no exista ya esa asignación en el mismo periodo
        cursor.execute(
            "SELECT id FROM asignaciones WHERE tutor_id = ? AND grupo = ? AND periodo = ?",
            (tutor_id, grupo, periodo)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Ya existe esa asignación para este periodo'}), 409

        cursor.execute(
            "INSERT INTO asignaciones (carrera_id, tutor_id, grupo, periodo, anio) VALUES (?, ?, ?, ?, ?)",
            (carrera_id, tutor_id, grupo, periodo, anio)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'Tutor asignado al grupo {grupo}'}), 201

    except Exception as e:
        print(f"[ERROR POST /api/asignaciones] {e}")
        return jsonify({'success': False, 'message': 'Error al crear asignación'}), 500


# ─────────────────────────────────────────────
# PATs
# ─────────────────────────────────────────────

@app.route('/api/pats', methods=['GET'])
def listar_pats():
    """Lista PATs. Acepta ?estado=X, ?carrera=X, ?tutor_id=X para filtrar."""
    estado = request.args.get('estado')
    carrera = request.args.get('carrera')
    tutor_id = request.args.get('tutor_id')
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT p.id, p.cuatrimestre, p.estado,
                   p.alumnos_h, p.alumnos_m,
                   a.grupo, a.periodo,
                   u.nombre || ' ' || u.apellidos AS tutor,
                   c.nombre AS carrera
            FROM pats p
            JOIN asignaciones a ON p.asignacion_id = a.id
            JOIN usuarios u ON a.tutor_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
        """
        conditions = []
        params = []
        if estado:
            conditions.append("p.estado = ?")
            params.append(estado)
        if carrera:
            conditions.append("c.nombre = ?")
            params.append(carrera)
        if tutor_id:
            conditions.append("a.tutor_id = ?")
            params.append(tutor_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY p.id DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return jsonify({'success': True, 'pats': [dict(r) for r in rows]})

    except Exception as e:
        print(f"[ERROR GET /api/pats] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener PATs'}), 500


@app.route('/api/pats/<int:pat_id>', methods=['GET'])
def detalle_pat(pat_id):
    """Devuelve el PAT completo con sus sesiones."""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.*, a.grupo, a.periodo,
                   u.nombre || ' ' || u.apellidos AS tutor, u.email AS tutor_email,
                   c.nombre AS carrera
            FROM pats p
            JOIN asignaciones a ON p.asignacion_id = a.id
            JOIN usuarios u ON a.tutor_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
            WHERE p.id = ?
        """, (pat_id,))
        pat = cursor.fetchone()

        if not pat:
            conn.close()
            return jsonify({'success': False, 'message': 'PAT no encontrado'}), 404

        cursor.execute(
            "SELECT * FROM sesiones WHERE pat_id = ? ORDER BY num_sesion",
            (pat_id,)
        )
        sesiones = cursor.fetchall()
        conn.close()

        pat_dict = dict(pat)
        pat_dict['sesiones'] = [dict(s) for s in sesiones]

        return jsonify({'success': True, 'pat': pat_dict})

    except Exception as e:
        print(f"[ERROR GET /api/pats/{pat_id}] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener PAT'}), 500


@app.route('/api/pats/<int:pat_id>/estado', methods=['PATCH'])
def actualizar_estado_pat(pat_id):
    """Actualiza el estado de un PAT (Aprobado / Rechazado)."""
    data = request.get_json()
    nuevo_estado = (data.get('estado') or '').strip()
    observaciones = (data.get('observaciones') or '').strip()

    if nuevo_estado not in ['Aprobado', 'Rechazado', 'Pendiente Revision']:
        return jsonify({'success': False, 'message': 'Estado no válido'}), 400

    if nuevo_estado == 'Rechazado' and not observaciones:
        return jsonify({'success': False, 'message': 'Las observaciones son obligatorias al rechazar'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pats SET estado = ?, comentarios_tutor = ? WHERE id = ?",
            (nuevo_estado, observaciones if observaciones else None, pat_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'PAT no encontrado'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'PAT marcado como {nuevo_estado}'})

    except Exception as e:
        print(f"[ERROR PATCH /api/pats/{pat_id}/estado] {e}")
        return jsonify({'success': False, 'message': 'Error al actualizar PAT'}), 500


# ─────────────────────────────────────────────
# PLANTILLAS PAT (Director de Tutorías)
# ─────────────────────────────────────────────

@app.route('/api/plantillas', methods=['GET'])
def listar_plantillas():
    """Devuelve las plantillas para un cuatrimestre. ?cuatrimestre=1"""
    cuatrimestre = request.args.get('cuatrimestre', '1')
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM plantillas_pat WHERE cuatrimestre = ? ORDER BY num_sesion",
            (cuatrimestre,)
        )
        rows = cursor.fetchall()
        conn.close()

        return jsonify({'success': True, 'plantillas': [dict(r) for r in rows]})

    except Exception as e:
        print(f"[ERROR GET /api/plantillas] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener plantillas'}), 500


@app.route('/api/plantillas', methods=['POST'])
def crear_sesion_plantilla():
    """Agrega una sesión a la plantilla."""
    data = request.get_json()
    cuatrimestre = data.get('cuatrimestre', '1')
    num_sesion = data.get('num_sesion')
    corte = (data.get('corte_parcial') or '').strip()
    tematica = (data.get('tematica') or '').strip()
    objetivo = (data.get('objetivo') or '').strip()
    resultados = (data.get('resultados_esperados') or '').strip()

    if not all([cuatrimestre, num_sesion, corte, tematica, objetivo, resultados]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO plantillas_pat (cuatrimestre, num_sesion, corte_parcial, tematica, objetivo, resultados_esperados) VALUES (?, ?, ?, ?, ?, ?)",
            (cuatrimestre, num_sesion, corte, tematica, objetivo, resultados)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()

        return jsonify({'success': True, 'message': 'Sesión agregada a la plantilla', 'id': nuevo_id}), 201

    except Exception as e:
        print(f"[ERROR POST /api/plantillas] {e}")
        return jsonify({'success': False, 'message': 'Error al guardar sesión'}), 500


# ─────────────────────────────────────────────
# SESIONES (Docente Tutor)
# ─────────────────────────────────────────────

@app.route('/api/sesiones/<int:sesion_id>', methods=['PATCH'])
def actualizar_sesion(sesion_id):
    """Actualiza datos de una sesión (fecha, resultados, estado, etc.)."""
    data = request.get_json()
    campos_permitidos = ['fecha_programada', 'hora_programada', 'resultados_obtenidos',
                         'canalizaciones', 'estado', 'motivo_cancelacion', 'fecha_validacion']

    updates = {k: v for k, v in data.items() if k in campos_permitidos}

    if not updates:
        return jsonify({'success': False, 'message': 'No hay campos válidos para actualizar'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        set_clause = ', '.join(f"{k} = ?" for k in updates)
        valores = list(updates.values()) + [sesion_id]
        cursor.execute(f"UPDATE sesiones SET {set_clause} WHERE id = ?", valores)

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Sesión no encontrada'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Sesión actualizada'})

    except Exception as e:
        print(f"[ERROR PATCH /api/sesiones/{sesion_id}] {e}")
        return jsonify({'success': False, 'message': 'Error al actualizar sesión'}), 500


# ─────────────────────────────────────────────
# CARRERAS
# ─────────────────────────────────────────────

@app.route('/api/carreras', methods=['GET'])
def listar_carreras():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM carreras ORDER BY nombre")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'carreras': [dict(r) for r in rows]})
    except Exception as e:
        print(f"[ERROR GET /api/carreras] {e}")
        return jsonify({'success': False, 'message': 'Error al obtener carreras'}), 500


if __name__ == '__main__':
    print("=" * 55)
    print("  Servidor Sistema PAT - UPFIM")
    print(f"  BD: {RUTA_BD}")
    print(f"  Raíz del proyecto: {CARPETA_RAIZ}")
    print("")
    print("  Abre en tu navegador:")
    print("  http://localhost:5000")
    print("  (o usa Live Server en el puerto 5500)")
    print("=" * 55)
    app.run(debug=True, port=5000)