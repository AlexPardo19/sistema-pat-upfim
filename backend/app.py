from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# Esto permite que tu HTML (frontend) se comunique con Python sin bloqueos de seguridad
CORS(app) 

# Ruta a tu base de datos
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA_ACTUAL, 'sistema_pat.db')

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    try:
        conexion = sqlite3.connect(RUTA_BD)
        cursor = conexion.cursor()
        
        # Buscamos al usuario en la base de datos
        cursor.execute("SELECT email, rol FROM usuarios WHERE email = ? AND password = ?", (email, password))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            # ¡Si lo encuentra, le da el pase de entrada!
            return jsonify({
                'success': True,
                'email': usuario[0],
                'role': usuario[1]
            })
        else:
            return jsonify({'success': False, 'message': 'Correo o contraseña incorrectos'}), 401
            
    except Exception as e:
        print(f"Error interno: {e}")
        return jsonify({'success': False, 'message': 'Error de conexión con la base de datos'}), 500

if __name__ == '__main__':
    print("Iniciando servidor del Sistema PAT...")
    app.run(debug=True, port=5000)