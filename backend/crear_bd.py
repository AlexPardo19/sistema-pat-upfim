import sqlite3

def inicializar_bd():
    conexion = sqlite3.connect('sistema_pat.db')
    cursor = conexion.cursor()

    # 1. Creamos las tablas
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('director-tutorias', 'jefe-grupo', 'director-carrera', 'docente-tutor', 'admin')),
            departamento TEXT
        );

        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER,
            grupo_id INTEGER,
            periodo TEXT NOT NULL,
            FOREIGN KEY (tutor_id) REFERENCES usuarios(id),
            FOREIGN KEY (grupo_id) REFERENCES grupos(id)
        );

        CREATE TABLE IF NOT EXISTS pats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignacion_id INTEGER,
            estado TEXT DEFAULT 'Borrador' CHECK(estado IN ('Borrador', 'Pendiente', 'Validado', 'Aprobado', 'Inactivo')),
            fecha_creacion DATE DEFAULT CURRENT_DATE,
            fecha_aprobacion DATE,
            FOREIGN KEY (asignacion_id) REFERENCES asignaciones(id)
        );

        CREATE TABLE IF NOT EXISTS sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            descripcion TEXT NOT NULL,
            estado TEXT DEFAULT 'Programada' CHECK(estado IN ('Programada', 'En Curso', 'Finalizada', 'Validada', 'Cancelada', 'Cancelacion Validada')),
            motivo_cancelacion TEXT,
            FOREIGN KEY (pat_id) REFERENCES pats(id)
        );
    ''')

    # 2. Credenciales base)
    usuarios_prueba = [
        ('Docente', 'Tutor', 'tutor@upfim.edu.mx', 'admin123', 'docente-tutor', 'Ingeniería en Tecnologías de la Información'),
        ('Director', 'de Tutorías', 'director.tutorias@upfim.edu.mx', 'admin123', 'director-tutorias', 'Dirección Académica'),
        ('Jefe', 'de Grupo', 'jefe.grupo@upfim.edu.mx', 'admin123', 'jefe-grupo', 'Ingeniería en Tecnologías de la Información'),
        ('Director', 'de Carrera', 'director.carrera@upfim.edu.mx', 'admin123', 'director-carrera', 'Ingeniería en Tecnologías de la Información')
    ]

    # 3. Insertamos todos los usuarios
    cursor.executemany('''
        INSERT OR IGNORE INTO usuarios (nombre, apellidos, email, password, rol, departamento)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', usuarios_prueba)
# Insertamos datos de prueba para enlazar las sesiones
    cursor.execute("INSERT OR IGNORE INTO grupos (codigo, nombre) VALUES ('ISC-5A', 'Sistemas Computacionales')")
    cursor.execute("INSERT OR IGNORE INTO asignaciones (tutor_id, grupo_id, periodo) VALUES (1, 1, '2026-1')")
    cursor.execute("INSERT OR IGNORE INTO pats (asignacion_id, estado) VALUES (1, 'Aprobado')")
    conexion.commit()
    conexion.close()
    print("¡Base de datos 'sistema_pat.db' creada y usuarios de prueba insertados con éxito!")

if __name__ == '__main__':
    inicializar_bd()