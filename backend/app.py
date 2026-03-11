from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) 

def obtener_conexion():
    conn = sqlite3.connect('sistema_pat.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    conn = obtener_conexion()
    user = conn.execute(
        'SELECT * FROM usuarios WHERE email = ? AND password = ?', 
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        return jsonify({'success': True, 'role': user['rol'], 'email': user['email']})
    else:
        return jsonify({'success': False, 'message': 'Correo o contraseña incorrectos'}), 401
@app.route('/api/sesiones', methods=['GET'])
def obtener_sesiones():
    conn = obtener_conexion()
    # Traemos todas las sesiones ordenadas de la más reciente a la más antigua
    sesiones = conn.execute('SELECT * FROM sesiones ORDER BY fecha DESC').fetchall()
    conn.close()
    return jsonify({'success': True, 'sesiones': [dict(s) for s in sesiones]})

@app.route('/api/sesiones', methods=['POST'])
def crear_sesion():
    data = request.get_json()
    conn = obtener_conexion()
    cursor = conn.cursor()
    # Usamos pat_id = 1 porque es el que acabamos de crear de prueba
    cursor.execute('''
        INSERT INTO sesiones (pat_id, fecha, hora, descripcion, estado)
        VALUES (?, ?, ?, ?, 'Programada')
    ''', (1, data['fecha'], data['hora'], data['descripcion']))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nuevo_id})

@app.route('/api/sesiones/<int:id>/estado', methods=['PUT'])
def actualizar_estado_sesion(id):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    motivo = data.get('motivo', '')
    
    conn = obtener_conexion()
    if nuevo_estado == 'Cancelada':
        # Si se cancela, guardamos el motivo y cambiamos el estado
        conn.execute('UPDATE sesiones SET estado = ?, motivo_cancelacion = ? WHERE id = ?', (nuevo_estado, motivo, id))
    else:
        conn.execute('UPDATE sesiones SET estado = ? WHERE id = ?', (nuevo_estado, id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    print("Servidor iniciando en http://localhost:5000...")
    app.run(debug=True, port=5000)