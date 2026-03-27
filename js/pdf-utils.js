// js/pdf-utils.js
// Utilidad para generar PDFs del Sistema PAT - IDENTICO AL FORMATO EXCEL (GRISES Y SUBCOLUMNAS)

function generarPDFPat(opts) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'letter' });

    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const marginX = 12;
    let y = 15;

    // --- 1. ENCABEZADOS PRINCIPALES ---
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('UNIVERSIDAD POLITÉCNICA DE FRANCISCO I. MADERO', pageW / 2, y, { align: 'center' });
    y += 6;
    doc.text('DEPARTAMENTO DE ASESORÍAS Y TUTORÍAS', pageW / 2, y, { align: 'center' });
    y += 6;
    doc.text('PLAN DE ACCIÓN TUTORIAL (PAT)', pageW / 2, y, { align: 'center' });
    y += 8;

    // --- 2. TABLA DE DATOS DE IDENTIFICACIÓN ---
    doc.autoTable({
        startY: y,
        theme: 'grid',
        styles: { fontSize: 8, textColor: [0, 0, 0], lineColor: [0, 0, 0], lineWidth: 0.2 },
        // GRIS INSTITUCIONAL PARA LAS CABECERAS
        headStyles: { fillColor: [217, 217, 217], textColor: [0, 0, 0], halign: 'center', valign: 'middle', fontStyle: 'bold' },
        bodyStyles: { halign: 'center', valign: 'middle' },
        columnStyles: {
            0: { cellWidth: 50 }, 
            1: { cellWidth: 50 }, 
            2: { cellWidth: 35 }, 
            3: { cellWidth: 20 }, 
            4: { cellWidth: 25 }, 
            5: { cellWidth: 'auto', halign: 'left' } 
        },
        head: [['PROGRAMA EDUCATIVO', 'NOMBRE DEL TUTOR', 'PERIODO CUATRIMESTRAL', 'GRUPO', 'TOTAL DE ALUMNOS TUTORADOS', 'COMENTARIOS DEL TUTOR']],
        body: [[
            opts.carrera || '—',
            opts.tutor || '—',
            opts.periodo || '—',
            opts.grupo || '—',
            `H: ${opts.h || 0}   M: ${opts.m || 0}   Total: ${(parseInt(opts.h)||0) + (parseInt(opts.m)||0)}`,
            opts.comentarios || '—'
        ]]
    });

    // --- 3. TABLA PRINCIPAL DE SESIONES ---
    const sesiones = opts.sesiones || [];
    
    doc.autoTable({
        startY: doc.lastAutoTable.finalY + 6,
        theme: 'grid',
        styles: { fontSize: 7, textColor: [0, 0, 0], lineColor: [0, 0, 0], lineWidth: 0.2, cellPadding: 1 },
        headStyles: { fillColor: [217, 217, 217], textColor: [0, 0, 0], halign: 'center', valign: 'middle', fontStyle: 'bold' },
        columnStyles: {
            0: { cellWidth: 8, halign: 'center' }, // Num
            1: { cellWidth: 15, halign: 'center' }, // Fecha
            2: { cellWidth: 10, halign: 'center' }, // Corte
            3: { cellWidth: 33 }, // Tematica
            4: { cellWidth: 33 }, // Objetivo
            5: { cellWidth: 33 }, // Resultados Esperados
            6: { cellWidth: 10, halign: 'center' }, // Asesoria
            7: { cellWidth: 10, halign: 'center' }, // Tutoria
            8: { cellWidth: 5, halign: 'center' }, // B
            9: { cellWidth: 5, halign: 'center' }, // M
            10: { cellWidth: 5, halign: 'center' }, // PS
            11: { cellWidth: 5, halign: 'center' }, // TS
            12: { cellWidth: 5, halign: 'center' }, // JD
            13: { cellWidth: 20, halign: 'center' }, // Nombre JG
            14: { cellWidth: 15, halign: 'center' }, // Firma
            15: { cellWidth: 43 } // Resultados Obtenidos
        },
        head: [
            // FILA SUPERIOR (Super-encabezados de división)
            [
                { content: 'PLAN DE TUTORÍA', colSpan: 6 },
                { content: 'SEGUIMIENTO DEL PROGRAMA DE TUTORÍAS', colSpan: 10 }
            ],
            // FILA INTERMEDIA (Nombres de las columnas con Rowspans para dejar hueco a las subcolumnas)
            [
                { content: 'NUM. DE\nSESIÓN', rowSpan: 2 },
                { content: 'FECHA', rowSpan: 2 },
                { content: 'CORTE\nPARCIAL', rowSpan: 2 },
                { content: 'TEMÁTICA A ABORDAR', rowSpan: 2 },
                { content: 'OBJETIVO', rowSpan: 2 },
                { content: 'RESULTADOS ESPERADOS', rowSpan: 2 },
                { content: 'CANALIZACIONES\n(registrar número de caso)', colSpan: 2 },
                { content: 'B', rowSpan: 2 },
                { content: 'M', rowSpan: 2 },
                { content: 'PS', rowSpan: 2 },
                { content: 'TS', rowSpan: 2 },
                { content: 'JD', rowSpan: 2 },
                { content: 'NOMBRE JEFE\nDE GRUPO', rowSpan: 2 },
                { content: 'FIRMA', rowSpan: 2 },
                { content: 'RESULTADOS OBTENIDOS', rowSpan: 2 }
            ],
            // FILA INFERIOR (Sub-columnas que van debajo de CANALIZACIONES)
            [
                { content: 'ASESORÍA', styles: { fontSize: 5.5 } },
                { content: 'TUTORÍA', styles: { fontSize: 5.5 } }
            ]
        ],
        body: sesiones.map(s => {
            // Evaluamos el estado de la firma
            let firma = '';
            if (s.estado === 'Validada') firma = 'FIRMADO';
            else if (s.estado === 'Cancelada') firma = 'CANCELADO';
            else if (s.estado === 'Finalizada') firma = 'PENDIENTE';

            const resultado = s.estado === 'Cancelada'
                ? `Motivo de cancelación: ${s.motivo || s.motivo_cancelacion || ''}`
                : (s.resultados_obtenidos || '');

            // Mapeo de las casillas
            const c_arr = Array.isArray(s.canalizaciones) ? s.canalizaciones : (s.canalizaciones || '').split(',').map(x => x.trim());
            
            // Evaluamos Asesoría y Tutoría
            let asesoria_mark = c_arr.includes('AS') ? 'X' : '';
            let tutoria_mark = c_arr.includes('TU') ? 'X' : '';
            
            // Lógica por defecto: Si la sesión ya se finalizó pero son datos viejos (sin AS ni TU), marcamos Tutoría por ser un PAT.
            if (!asesoria_mark && !tutoria_mark && s.estado !== 'Pendiente' && s.estado !== 'Programada') {
                tutoria_mark = 'X';
            }

            // Evaluamos Canalizaciones
            const b = c_arr.includes('B') ? 'X' : '';
            const m = c_arr.includes('M') ? 'X' : '';
            const ps = c_arr.includes('PS') ? 'X' : '';
            const ts = c_arr.includes('TS') ? 'X' : '';
            const jd = c_arr.includes('JD') ? 'X' : '';

            return [
                s.num || s.num_sesion || '',
                s.fecha_programada || '',
                s.corte_parcial || '',
                s.tematica || '',
                s.objetivo || '',
                s.resultados_esperados || '',
                asesoria_mark, // <--- Nueva variable de Asesoría
                tutoria_mark,  // <--- Nueva variable de Tutoría
                b, m, ps, ts, jd,
                '', 
                firma,
                resultado,
            ];
        }),
    });

    // --- 4. SECCIÓN DE FIRMAS AL CALCE ---
    let finalY = doc.lastAutoTable.finalY + 25; 

    // Salto de página preventivo si no caben las firmas
    if (finalY > pageH - 25) {
        doc.addPage();
        finalY = 30;
    }

    const colW = (pageW - marginX * 2) / 3;
    const lineW = 65; 

    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');

    // FIRMA 1
    doc.line(marginX + colW / 2 - lineW / 2, finalY, marginX + colW / 2 + lineW / 2, finalY);
    doc.text('COORDINADOR DEL PROGRAMA EDUCATIVO', marginX + colW / 2, finalY + 5, { align: 'center' });

    // FIRMA 2
    doc.line(marginX + colW + colW / 2 - lineW / 2, finalY, marginX + colW + colW / 2 + lineW / 2, finalY);
    doc.text('NOMBRE Y FIRMA DEL TUTOR', marginX + colW + colW / 2, finalY + 5, { align: 'center' });

    // FIRMA 3
    doc.line(marginX + 2 * colW + colW / 2 - lineW / 2, finalY, marginX + 2 * colW + colW / 2 + lineW / 2, finalY);
    doc.text('NOMBRE Y FIRMA DEL RESPONSABLE', marginX + 2 * colW + colW / 2, finalY + 5, { align: 'center' });
    doc.text('DE ASESORÍAS Y TUTORÍAS', marginX + 2 * colW + colW / 2, finalY + 10, { align: 'center' });

    // --- 5. GUARDAR ---
    const filename = opts.filename || `PAT_${opts.grupo || 'Plantilla'}_${(opts.tutor || 'Tutor').replace(/ /g, '_')}.pdf`;
    doc.save(filename);
}