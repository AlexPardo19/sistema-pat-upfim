# -*- coding: utf-8 -*-
import sqlite3
import os
import datetime

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA_ACTUAL, 'sistema_pat.db')

# Cuatrimestres activos segun periodo
# ENE-ABR -> 2,5,8 | MAY-AGO -> 3,6,9 | SEP-DIC -> 1,4,7
CUATS_POR_PERIODO = {
    'ENE-ABR': [2, 5, 8],
    'MAY-AGO': [3, 6, 9],
    'SEP-DIC': [1, 4, 7],
}

def periodo_actual():
    mes = datetime.datetime.now().month
    anio = datetime.datetime.now().year
    if 1 <= mes <= 4:
        return 'ENE-ABR %d' % anio, 'ENE-ABR'
    elif 5 <= mes <= 8:
        return 'MAY-AGO %d' % anio, 'MAY-AGO'
    else:
        return 'SEP-DIC %d' % anio, 'SEP-DIC'

def inicializar_bd():
    if os.path.exists(RUTA_BD):
        os.remove(RUTA_BD)

    conn = sqlite3.connect(RUTA_BD)
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            departamento_o_carrera TEXT,
            grupo_asignado TEXT,
            tutor_id INTEGER,
            activo INTEGER DEFAULT 1
        );
        CREATE TABLE carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            abreviatura TEXT
        );
        CREATE TABLE periodos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            anio INTEGER NOT NULL,
            activo INTEGER DEFAULT 0,
            UNIQUE(tipo, anio)
        );
        CREATE TABLE plantillas_pat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cuatrimestre INTEGER NOT NULL,
            num_sesion INTEGER NOT NULL,
            corte_parcial TEXT,
            tematica TEXT NOT NULL,
            objetivo TEXT NOT NULL,
            resultados_esperados TEXT,
            estado TEXT DEFAULT 'Borrador',
            periodo_id INTEGER
        );
        CREATE TABLE asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrera_id INTEGER NOT NULL,
            tutor_id INTEGER NOT NULL,
            grupo TEXT NOT NULL,
            periodo_id INTEGER NOT NULL,
            cuatrimestre INTEGER NOT NULL,
            jefe_grupo_id INTEGER
        );
        CREATE TABLE pats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignacion_id INTEGER NOT NULL,
            cuatrimestre INTEGER NOT NULL,
            programa_educativo TEXT,
            nombre_tutor TEXT,
            periodo_cuatrimestral TEXT,
            grupo TEXT,
            alumnos_h INTEGER DEFAULT 0,
            alumnos_m INTEGER DEFAULT 0,
            comentarios_tutor TEXT,
            nombre_jefe_grupo TEXT,
            estado TEXT DEFAULT 'Borrador',
            observaciones_director TEXT,
            fecha_envio TEXT,
            fecha_aprobacion TEXT
        );
        CREATE TABLE sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pat_id INTEGER NOT NULL,
            num_sesion INTEGER NOT NULL,
            fecha_programada TEXT,
            hora_programada TEXT,
            corte_parcial TEXT,
            tematica TEXT,
            objetivo TEXT,
            resultados_esperados TEXT,
            canalizaciones TEXT,
            resultados_obtenidos TEXT,
            estado TEXT DEFAULT 'Pendiente',
            motivo_cancelacion TEXT,
            firma_jefe TEXT,
            fecha_validacion TEXT
        );
        CREATE TABLE solicitudes_jefe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitante_id INTEGER NOT NULL,
            nombre_alumno TEXT NOT NULL,
            apellidos_alumno TEXT NOT NULL,
            email_alumno TEXT NOT NULL,
            grupo TEXT NOT NULL,
            carrera TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            observaciones TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # --- CARRERAS ---
    carreras = [
        ('Ingenieria en Tecnologias de la Informacion', 'ITI'),
        ('Ingenieria Civil', 'IC'),
        ('Ingenieria en Agrotecnologia', 'IA'),
        ('Ingenieria Financiera', 'IF'),
        ('Ingenieria en Produccion Animal', 'IPA'),
        ('Ingenieria en Diseno Industrial', 'IDI'),
        ('Ingenieria en Energia', 'IE'),
        ('Licenciatura en Administracion y Gestion Empresarial', 'LAGE'),
    ]
    c.executemany('INSERT INTO carreras (nombre, abreviatura) VALUES (?,?)', carreras)

    # --- PERIODO ACTIVO ---
    p_nombre, p_tipo = periodo_actual()
    anio = datetime.datetime.now().year
    c.execute('INSERT INTO periodos (nombre, tipo, anio, activo) VALUES (?,?,?,1)',
              (p_nombre, p_tipo, anio))
    periodo_id = c.lastrowid

    # --- USUARIOS ---
    usuarios = [
        ('Super', 'Admin', 'admin@upfim.edu.mx', 'admin123', 'admin', 'Sistemas', None, None),
        ('Blanca', 'Monroy Estrada', 'director.tutorias@upfim.edu.mx', 'admin123', 'director-tutorias', 'Direccion de Tutorias', None, None),
        ('Roberto', 'Carrera Lopez', 'director.carrera@upfim.edu.mx', 'admin123', 'director-carrera', 'Ingenieria en Tecnologias de la Informacion', None, None),
        ('Alicia', 'Leon Martinez', 'tutor@upfim.edu.mx', 'admin123', 'docente-tutor', 'Ingenieria en Tecnologias de la Informacion', None, None),
        ('Alyzonn', 'Reyes Cruz', 'jefe.grupo@upfim.edu.mx', 'admin123', 'jefe-grupo', 'Ingenieria en Tecnologias de la Informacion', '1TIG3', None),
    ]
    c.executemany(
        'INSERT INTO usuarios (nombre,apellidos,email,password,rol,departamento_o_carrera,grupo_asignado,tutor_id) VALUES (?,?,?,?,?,?,?,?)',
        usuarios)

    # Vincular jefe con tutor
    c.execute("UPDATE usuarios SET tutor_id=4 WHERE email='jefe.grupo@upfim.edu.mx'")

    # Directores extra por carrera
    for i, (car, abr) in enumerate(carreras):
        c.execute('INSERT INTO usuarios (nombre,apellidos,email,password,rol,departamento_o_carrera) VALUES (?,?,?,?,?,?)',
                  ('Director', 'Carrera '+abr, 'dir.carrera%d@upfim.edu.mx' % (i+1), 'admin123', 'director-carrera', car))

    # Tutores extra
    for i in range(1, 4):
        c.execute('INSERT INTO usuarios (nombre,apellidos,email,password,rol,departamento_o_carrera) VALUES (?,?,?,?,?,?)',
                  ('Tutor', 'Docente %d' % i, 'tutor%d@upfim.edu.mx' % i, 'admin123', 'docente-tutor', carreras[0][0]))

    # --- PLANTILLA BASE (cuatrimestres del periodo activo) ---
    temas = [
        (1, 'I', 'Bienvenida e integracion al grupo', 'Fomentar la integracion del grupo', 'Que los alumnos conozcan las actividades del cuatrimestre'),
        (2, 'I', 'Diagnostico individual', 'Generar el diagnostico del grupo', 'Conocer la situacion del estudiante'),
        (3, 'I', 'Normativa institucional', 'Informar sobre el reglamento', 'Comunidad informada sobre derechos y obligaciones'),
        (4, 'I', 'Disciplina y logro de objetivos', 'Analizar la importancia de la disciplina', 'Concientizar sobre la disciplina'),
        (5, 'I', 'Estilos de aprendizaje', 'Informar sobre estilos de aprendizaje', 'Identificar su estilo de aprendizaje'),
        (6, 'II', 'Habitos de estudio', 'Reafirmar rutinas de estudio', 'Reforzar habitos de estudio'),
        (7, 'II', 'Seguimiento primer parcial', 'Revisar avance del grupo', 'Incrementar aprovechamiento'),
        (8, 'II', 'Prevencion de violencia', 'Informar sobre prevencion y reaccion', 'Comunidad informada sobre protocolos'),
        (9, 'II', 'Gestion de emociones', 'Identificar y gestionar emociones', 'Concientizar sobre gestion emocional'),
        (10, 'II', 'Seguimiento segundo parcial', 'Revisar avance del grupo', 'Disminuir reprobacion'),
        (11, 'III', 'Actitud para el logro de metas', 'Reflexionar sobre la actitud positiva', 'Beneficios de la actitud'),
        (12, 'III', 'Trabajo en equipo', 'Importancia del trabajo en equipo', 'Reflexion sobre trabajo colaborativo'),
        (13, 'III', 'Actividad integradora', 'Reforzar trabajo en equipo con dinamicas', 'Favorecer comunicacion e integracion'),
        (14, 'III', 'Seguimiento tercer parcial', 'Revisar avance y dar seguimiento', 'Disminuir reprobacion'),
        (15, 'III', 'Evaluacion del tutor e informe', 'Evaluar el trabajo del tutor', 'Evaluacion favorable de la accion tutorial'),
    ]

    cuats_activos = CUATS_POR_PERIODO.get(p_tipo, [1, 4, 7])
    for cuat in cuats_activos:
        for num, corte, tema, obj, res in temas:
            c.execute(
                'INSERT INTO plantillas_pat (cuatrimestre,num_sesion,corte_parcial,tematica,objetivo,resultados_esperados,estado,periodo_id) VALUES (?,?,?,?,?,?,?,?)',
                (cuat, num, corte, tema, obj, res, 'Publicada', periodo_id))

    # --- ASIGNACION + PAT DEMO ---
    c.execute("SELECT id FROM carreras WHERE nombre='Ingenieria en Tecnologias de la Informacion'")
    carrera_id = c.fetchone()[0]
    cuat_demo = cuats_activos[0]

    c.execute('INSERT INTO asignaciones (carrera_id,tutor_id,grupo,periodo_id,cuatrimestre,jefe_grupo_id) VALUES (?,4,?,?,?,5)',
              (carrera_id, '1TIG3', periodo_id, cuat_demo))
    asig_id = c.lastrowid

    c.execute('''INSERT INTO pats (asignacion_id,cuatrimestre,programa_educativo,nombre_tutor,periodo_cuatrimestral,grupo,alumnos_h,alumnos_m,comentarios_tutor,nombre_jefe_grupo,estado)
                 VALUES (?,?,'Ingenieria en Tecnologias de la Informacion','Alicia Leon Martinez',?,?,16,10,'Grupo participativo, se trabajo en dinamicas de integracion.','Alyzonn Reyes Cruz','Aprobado')''',
              (asig_id, cuat_demo, p_nombre, '1TIG3'))
    pat_id = c.lastrowid

    for num, corte, tema, obj, res in temas:
        estado = 'Validada' if num <= 2 else ('Finalizada' if num == 3 else 'Pendiente')
        fecha = '2026-0%d-%02d' % (1 + (num-1)//4, 5 + ((num-1)%4)*7) if num <= 6 else None
        resultado = 'Sesion impartida exitosamente' if num <= 3 else ''
        c.execute(
            'INSERT INTO sesiones (pat_id,num_sesion,fecha_programada,corte_parcial,tematica,objetivo,resultados_esperados,resultados_obtenidos,estado) VALUES (?,?,?,?,?,?,?,?,?)',
            (pat_id, num, fecha, corte, tema, obj, res, resultado, estado))

    # Solicitud demo
    c.execute("INSERT INTO solicitudes_jefe (solicitante_id,nombre_alumno,apellidos_alumno,email_alumno,grupo,carrera) VALUES (4,'Carlos','Mendoza','carlos@upfim.edu.mx','2TIG1','Ingenieria en Tecnologias de la Informacion')")

    conn.commit()
    conn.close()

    print("============================================================")
    print("  Base de Datos creada OK")
    print("============================================================")
    print("  Periodo: " + p_nombre)
    print("  Cuatrimestres: " + str(cuats_activos))
    print("  --------------------------------------------------------")
    print("  admin@upfim.edu.mx             -> Admin")
    print("  director.tutorias@upfim.edu.mx -> Dir. Tutorias")
    print("  director.carrera@upfim.edu.mx  -> Dir. Carrera (ITI)")
    print("  tutor@upfim.edu.mx             -> Docente Tutor")
    print("  jefe.grupo@upfim.edu.mx        -> Jefe de Grupo")
    print("  Password: admin123")
    print("============================================================")

if __name__ == '__main__':
    inicializar_bd()
