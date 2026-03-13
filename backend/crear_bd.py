import sqlite3
import os

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA_ACTUAL, 'sistema_pat.db')

def inicializar_bd():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    # Limpiar BD anterior
    cursor.executescript('''
        DROP TABLE IF EXISTS sesiones;
        DROP TABLE IF EXISTS pats;
        DROP TABLE IF EXISTS plantillas_pat;
        DROP TABLE IF EXISTS asignaciones;
        DROP TABLE IF EXISTS carreras;
        DROP TABLE IF EXISTS usuarios;

        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            departamento_o_carrera TEXT,
            grupo_asignado TEXT
        );

        CREATE TABLE carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );

        CREATE TABLE asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrera_id INTEGER,
            tutor_id INTEGER,
            grupo TEXT NOT NULL,
            periodo TEXT NOT NULL,
            anio INTEGER NOT NULL
        );

        CREATE TABLE plantillas_pat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cuatrimestre TEXT NOT NULL,
            num_sesion INTEGER,
            corte_parcial TEXT,
            tematica TEXT,
            objetivo TEXT,
            resultados_esperados TEXT,
            estado TEXT DEFAULT 'Publicada'
        );

        CREATE TABLE pats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignacion_id INTEGER,
            cuatrimestre TEXT NOT NULL,
            alumnos_h INTEGER DEFAULT 0,
            alumnos_m INTEGER DEFAULT 0,
            comentarios_tutor TEXT,
            estado TEXT
        );

        CREATE TABLE sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER,
            num_sesion INTEGER,
            fecha_programada DATE,
            hora_programada TEXT,
            corte_parcial TEXT,
            tematica TEXT,
            objetivo TEXT,
            resultados_esperados TEXT,
            canalizaciones TEXT,
            resultados_obtenidos TEXT,
            estado TEXT,
            motivo_cancelacion TEXT,
            fecha_validacion DATE
        );
    ''')

    # --- 1. CREAR LAS 8 CARRERAS ---
    carreras = [
        'Ingeniería en Tecnologías de la Información', 'Ingeniería Civil', 'Ingeniería en Agrotecnología',
        'Ingeniería Financiera', 'Ingeniería en Producción Animal', 'Ingeniería en Diseño Industrial',
        'Ingeniería en Energía', 'Licenciatura en Administración y Gestión Empresarial'
    ]
    for c in carreras:
        cursor.execute('INSERT INTO carreras (nombre) VALUES (?)', (c,))

    # --- 2. CREAR LOS PERFILES (ADMIN Y DIR TUTORÍAS) ---
    usuarios = [
        ('Super', 'Admin', 'admin@upfim.edu.mx', 'admin123', 'admin', 'Sistemas', None),
        ('Blanca', 'Monroy', 'dir.tutorias@upfim.edu.mx', 'admin123', 'director-tutorias', 'Dirección de Tutorías', None)
    ]

    # --- 3. CREAR 8 DIRECTORES DE CARRERA ---
    for i, c in enumerate(carreras):
        usuarios.append((f'Director', f'Carrera {i+1}', f'dir.carrera{i+1}@upfim.edu.mx', 'admin123', 'director-carrera', c, None))

    # --- 4. CREAR 9 TUTORES Y 9 JEFES DE GRUPO ---
    for i in range(1, 10):
        carrera_asignada = carreras[(i-1) % 8] # Distribuye las carreras
        grupo = f"1G{i}"
        usuarios.append((f'Tutor', f'Docente {i}', f'tutor{i}@upfim.edu.mx', 'admin123', 'docente-tutor', carrera_asignada, None))
        usuarios.append((f'Jefe', f'Alumno {i}', f'jefe{i}@upfim.edu.mx', 'admin123', 'jefe-grupo', carrera_asignada, grupo))

    cursor.executemany('INSERT INTO usuarios (nombre, apellidos, email, password, rol, departamento_o_carrera, grupo_asignado) VALUES (?, ?, ?, ?, ?, ?, ?)', usuarios)

    # --- 5. GENERAR PAT 1: PLANTILLA DE DIRECCIÓN DE TUTORÍAS ---
    # Simulamos que la Directora ya creó las 15 sesiones base para el Cuatrimestre 1
    plantilla = []
    for i in range(1, 16):
        corte = "I" if i <= 5 else ("II" if i <= 10 else "III")
        plantilla.append(('1', i, corte, f'Temática Base {i}', f'Objetivo Base {i}', 'Que los alumnos participen', 'Publicada'))
    cursor.executemany('INSERT INTO plantillas_pat (cuatrimestre, num_sesion, corte_parcial, tematica, objetivo, resultados_esperados, estado) VALUES (?, ?, ?, ?, ?, ?, ?)', plantilla)

    # --- 6. GENERAR PAT 2: PAT DEL TUTOR 1 EN EJECUCIÓN ---
    # Asignamos al Tutor 1 a la Carrera de TI (id 1)
    cursor.execute("INSERT INTO asignaciones (carrera_id, tutor_id, grupo, periodo, anio) VALUES (1, 11, '1G1', 'SEPT-DIC 2026', 2026)")
    asignacion_id = cursor.lastrowid

    # Creamos el documento PAT aprobado
    cursor.execute("INSERT INTO pats (asignacion_id, cuatrimestre, alumnos_h, alumnos_m, comentarios_tutor, estado) VALUES (?, '1', 15, 12, 'Grupo de prueba para testing del sistema.', 'Aprobado')", (asignacion_id,))
    pat_id = cursor.lastrowid

    # Llenamos las 15 sesiones del Tutor 1 con diferentes estados para probar las vistas
    sesiones_tutor = [
        (pat_id, 1, '2026-09-05', '14:00', 'I', 'Bienvenida al Grupo', 'Integración', 'Conocimiento del plan', 'B, PS', 'Excelente participación', 'Validada', None, '2026-09-06'),
        (pat_id, 2, '2026-09-12', '14:00', 'I', 'Reglamento Escolar', 'Conocer normas', 'Cero incidencias', '', 'Alumnos informados', 'Finalizada_Por_Tutor', None, None),
        (pat_id, 3, '2026-09-19', '14:00', 'I', 'Hábitos de Estudio', 'Mejorar retención', 'Aprobar parcial', '', '', 'Programada', None, None),
        (pat_id, 4, '2026-09-26', '14:00', 'I', 'Prevención de Adicciones', 'Informar', 'Concientización', '', '', 'Cancelada', 'No asistió el ponente invitado', None)
    ]
    # Las 11 sesiones restantes sin programar
    for i in range(5, 16):
        corte = "I" if i <= 5 else ("II" if i <= 10 else "III")
        sesiones_tutor.append((pat_id, i, None, None, corte, f'Sesión {i}', 'Objetivo', 'Resultados', '', '', 'Programada', None, None))
    
    cursor.executemany('INSERT INTO sesiones (pat_id, num_sesion, fecha_programada, hora_programada, corte_parcial, tematica, objetivo, resultados_esperados, canalizaciones, resultados_obtenidos, estado, motivo_cancelacion, fecha_validacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sesiones_tutor)

    conexion.commit()
    conexion.close()
    print("¡Base de Datos masiva generada exitosamente para el Test del Sistema!")

if __name__ == '__main__':
    inicializar_bd()