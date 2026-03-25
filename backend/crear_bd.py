import sqlite3
import os

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA_ACTUAL, 'sistema_pat.db')


def inicializar_bd():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

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

    # ─── 1. CARRERAS ───
    carreras = [
        'Ingeniería en Tecnologías de la Información',
        'Ingeniería Civil',
        'Ingeniería en Agrotecnología',
        'Ingeniería Financiera',
        'Ingeniería en Producción Animal',
        'Ingeniería en Diseño Industrial',
        'Ingeniería en Energía',
        'Licenciatura en Administración y Gestión Empresarial'
    ]
    for c in carreras:
        cursor.execute('INSERT INTO carreras (nombre) VALUES (?)', (c,))

    # ─── 2. USUARIOS BASE ───
    # IMPORTANTE: Los emails coinciden EXACTAMENTE con login.html
    usuarios = [
        # Rol Admin
        ('Super', 'Admin',
         'admin@upfim.edu.mx', 'admin123', 'admin', 'Sistemas', None),

        # Director de Tutorías — email mostrado en login.html
        ('Blanca', 'Monroy',
         'director.tutorias@upfim.edu.mx', 'admin123', 'director-tutorias', 'Dirección de Tutorías', None),

        # Director de Carrera — email mostrado en login.html (carrera TI por defecto)
        ('Roberto', 'Carrera',
         'director.carrera@upfim.edu.mx', 'admin123', 'director-carrera',
         'Ingeniería en Tecnologías de la Información', None),

        # Docente Tutor — email mostrado en login.html
        ('Alicia', 'León Martínez',
         'tutor@upfim.edu.mx', 'admin123', 'docente-tutor',
         'Ingeniería en Tecnologías de la Información', None),

        # Jefe de Grupo — email mostrado en login.html
        ('Alyzonn', 'Reyes Pérez',
         'jefe.grupo@upfim.edu.mx', 'admin123', 'jefe-grupo',
         'Ingeniería en Tecnologías de la Información', '1G1'),
    ]

    # ─── 3. DIRECTORES ADICIONALES (uno por carrera) ───
    for i, c in enumerate(carreras):
        email = f'dir.carrera{i + 1}@upfim.edu.mx'
        usuarios.append(
            (f'Director', f'Carrera {i + 1}', email, 'admin123', 'director-carrera', c, None)
        )

    # ─── 4. TUTORES Y JEFES ADICIONALES ───
    for i in range(1, 10):
        carrera_asignada = carreras[(i - 1) % 8]
        grupo = f'1G{i}'
        usuarios.append(
            (f'Tutor', f'Docente {i}', f'tutor{i}@upfim.edu.mx', 'admin123',
             'docente-tutor', carrera_asignada, None)
        )
        usuarios.append(
            (f'Jefe', f'Alumno {i}', f'jefe{i}@upfim.edu.mx', 'admin123',
             'jefe-grupo', carrera_asignada, grupo)
        )

    cursor.executemany(
        'INSERT INTO usuarios (nombre, apellidos, email, password, rol, departamento_o_carrera, grupo_asignado) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        usuarios
    )

    # ─── 5. PLANTILLA DEL DIRECTOR DE TUTORÍAS (15 sesiones, Cuatrimestre 1) ───
    plantilla = []
    temas_base = [
        ('Bienvenida e integración al grupo', 'Fomentar la integración del grupo y conocer su perfil'),
        ('Reglamento escolar y normativas', 'Informar sobre las normas institucionales vigentes'),
        ('Hábitos de estudio efectivos', 'Desarrollar técnicas de aprendizaje para el cuatrimestre'),
        ('Prevención de adicciones', 'Concientizar sobre riesgos y vías de apoyo institucional'),
        ('Orientación vocacional', 'Fortalecer la identidad profesional del estudiante'),
        ('Manejo del estrés académico', 'Brindar herramientas para la gestión del estrés'),
        ('Cierre del primer corte', 'Evaluar avances y detectar alumnos en riesgo (Corte I)'),
        ('Habilidades de comunicación', 'Desarrollar competencias de comunicación efectiva'),
        ('Trabajo en equipo y liderazgo', 'Promover la colaboración y el trabajo colaborativo'),
        ('Salud mental y bienestar', 'Identificar señales de alerta y canales de apoyo'),
        ('Cierre del segundo corte', 'Evaluar avances y detectar alumnos en riesgo (Corte II)'),
        ('Proyecto profesional integrador', 'Vincular contenidos académicos con el campo laboral'),
        ('Emprendimiento e innovación', 'Fomentar la cultura emprendedora'),
        ('Repaso general y dudas finales', 'Resolver dudas y reforzar temas del cuatrimestre'),
        ('Cierre y retroalimentación final', 'Evaluar el PAT y la satisfacción de los estudiantes'),
    ]

    for i, (tematica, objetivo) in enumerate(temas_base, 1):
        corte = 'I' if i <= 5 else ('II' if i <= 10 else 'III')
        plantilla.append(('1', i, corte, tematica, objetivo, 'Que los alumnos participen activamente', 'Publicada'))

    cursor.executemany(
        'INSERT INTO plantillas_pat (cuatrimestre, num_sesion, corte_parcial, tematica, objetivo, resultados_esperados, estado) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        plantilla
    )

    # ─── 6. PAT DEL TUTOR DEMO (tutor@upfim.edu.mx) ───
    # Obtenemos el ID del tutor demo y su carrera
    cursor.execute("SELECT id FROM usuarios WHERE email = 'tutor@upfim.edu.mx'")
    tutor_demo = cursor.fetchone()

    cursor.execute("SELECT id FROM carreras WHERE nombre = 'Ingeniería en Tecnologías de la Información'")
    carrera_ti = cursor.fetchone()

    if tutor_demo and carrera_ti:
        cursor.execute(
            "INSERT INTO asignaciones (carrera_id, tutor_id, grupo, periodo, anio) VALUES (?, ?, '1G1', 'SEPT-DIC 2026', 2026)",
            (carrera_ti[0], tutor_demo[0])
        )
        asignacion_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO pats (asignacion_id, cuatrimestre, alumnos_h, alumnos_m, comentarios_tutor, estado) "
            "VALUES (?, '1', 15, 12, 'Grupo de prueba inicial del sistema.', 'Aprobado')",
            (asignacion_id,)
        )
        pat_id = cursor.lastrowid

        # Sesiones de ejemplo con diferentes estados
        sesiones_demo = [
            (pat_id, 1, '2026-09-05', '14:00', 'I', temas_base[0][0], temas_base[0][1],
             'Que los alumnos participen', 'B, PS', 'Excelente participación grupal',
             'Validada', None, '2026-09-06'),
            (pat_id, 2, '2026-09-12', '14:00', 'I', temas_base[1][0], temas_base[1][1],
             'Alumnos informados', '', 'Todos informados del reglamento',
             'Finalizada_Por_Tutor', None, None),
            (pat_id, 3, '2026-09-19', '14:00', 'I', temas_base[2][0], temas_base[2][1],
             'Aprobar parcial', '', '',
             'Programada', None, None),
            (pat_id, 4, '2026-09-26', '14:00', 'I', temas_base[3][0], temas_base[3][1],
             'Concientización', '', '',
             'Cancelada', 'No asistió el ponente invitado', None),
        ]

        # Las sesiones 5-15 sin programar
        for i in range(5, 16):
            corte = 'I' if i <= 5 else ('II' if i <= 10 else 'III')
            tema = temas_base[i - 1]
            sesiones_demo.append(
                (pat_id, i, None, None, corte, tema[0], tema[1],
                 'Que los alumnos participen', '', '',
                 'Programada', None, None)
            )

        cursor.executemany(
            'INSERT INTO sesiones (pat_id, num_sesion, fecha_programada, hora_programada, corte_parcial, '
            'tematica, objetivo, resultados_esperados, canalizaciones, resultados_obtenidos, '
            'estado, motivo_cancelacion, fecha_validacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            sesiones_demo
        )

    conexion.commit()
    conexion.close()

    print("=" * 55)
    print("  Base de Datos inicializada correctamente")
    print("=" * 55)
    print("\n  CREDENCIALES DE PRUEBA:")
    print("  ─────────────────────────────────────────────")
    print("  admin@upfim.edu.mx             → Admin")
    print("  director.tutorias@upfim.edu.mx → Director Tutorías")
    print("  director.carrera@upfim.edu.mx  → Director Carrera")
    print("  tutor@upfim.edu.mx             → Docente Tutor")
    print("  jefe.grupo@upfim.edu.mx        → Jefe de Grupo")
    print("  Contraseña general: admin123")
    print("=" * 55)


if __name__ == '__main__':
    inicializar_bd()