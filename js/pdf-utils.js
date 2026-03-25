// js/pdf-utils.js
// Utilidad compartida para generar PDFs del Sistema PAT
// Usa jsPDF + autoTable directamente (sin html2canvas)

/**
 * Genera y descarga un PDF de propuesta PAT.
 * @param {Object} opts
 * @param {string} opts.carrera - Nombre del programa educativo
 * @param {string} opts.tutor - Nombre del tutor
 * @param {string} opts.grupo - Código del grupo
 * @param {number} opts.h - Alumnos hombres
 * @param {number} opts.m - Alumnos mujeres
 * @param {string} opts.periodo - Periodo (opcional)
 * @param {string} opts.comentarios - Comentarios (opcional)
 * @param {Array}  opts.sesiones - Array de sesiones
 * @param {string} opts.tipo - 'propuesta' | 'completo'
 * @param {string} opts.filename - Nombre del archivo (opcional)
 */
function generarPDFPat(opts) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'letter' });

    const pageW = doc.internal.pageSize.getWidth();
    const marginX = 12;
    let y = 12;

    // ── ENCABEZADO ──
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.text('UNIVERSIDAD POLITÉCNICA DE FRANCISCO I. MADERO', pageW / 2, y, { align: 'center' });
    y += 5;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text('DEPARTAMENTO DE ASESORÍAS Y TUTORÍAS', pageW / 2, y, { align: 'center' });
    y += 5;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    const titulo = opts.tipo === 'propuesta' ? 'PLAN DE ACCIÓN TUTORIAL - PROPUESTA' : 'PLAN DE ACCIÓN TUTORIAL (PAT)';
    doc.text(titulo, pageW / 2, y, { align: 'center' });
    y += 8;

    // ── TABLA DE DATOS GENERALES ──
    const h = opts.h || 0;
    const m = opts.m || 0;
    const total = h + m;

    if (opts.tipo === 'propuesta') {
        doc.autoTable({
            startY: y,
            margin: { left: marginX, right: marginX },
            theme: 'grid',
            styles: { fontSize: 9, cellPadding: 3, halign: 'center' },
            headStyles: { fillColor: [229, 231, 235], textColor: [0, 0, 0], fontStyle: 'bold' },
            head: [['PROGRAMA EDUCATIVO', 'NOMBRE DEL TUTOR', 'GRUPO', 'TOTAL ALUMNOS']],
            body: [[opts.carrera || '', opts.tutor || '', opts.grupo || '', `${total} (${h}H, ${m}M)`]],
        });
    } else {
        doc.autoTable({
            startY: y,
            margin: { left: marginX, right: marginX },
            theme: 'grid',
            styles: { fontSize: 9, cellPadding: 3, halign: 'center' },
            headStyles: { fillColor: [229, 231, 235], textColor: [0, 0, 0], fontStyle: 'bold' },
            head: [['PROGRAMA EDUCATIVO', 'NOMBRE DEL TUTOR', 'PERIODO', 'GRUPO', 'H', 'M']],
            body: [[opts.carrera || '', opts.tutor || '', opts.periodo || '', opts.grupo || '', String(h), String(m)]],
        });
    }

    y = doc.lastAutoTable.finalY + 4;

    // ── TABLA DE SESIONES ──
    const sesiones = opts.sesiones || [];

    if (opts.tipo === 'propuesta') {
        // Solo temática, objetivo, resultados esperados
        doc.autoTable({
            startY: y,
            margin: { left: marginX, right: marginX },
            theme: 'grid',
            styles: { fontSize: 8, cellPadding: 2.5, overflow: 'linebreak' },
            headStyles: { fillColor: [243, 244, 246], textColor: [0, 0, 0], fontStyle: 'bold', halign: 'center' },
            columnStyles: {
                0: { halign: 'center', cellWidth: 10 },
                1: { cellWidth: 75 },
                2: { cellWidth: 75 },
                3: { cellWidth: 75 },
            },
            head: [['No.', 'TEMÁTICA', 'OBJETIVO', 'RESULTADOS ESPERADOS']],
            body: sesiones.map(s => [
                s.num || s.num_sesion || '',
                s.tematica || '',
                s.objetivo || '',
                s.resultados_esperados || '',
            ]),
        });
    } else {
        // Versión completa con canalizaciones, firma, resultados obtenidos
        doc.autoTable({
            startY: y,
            margin: { left: marginX, right: marginX },
            theme: 'grid',
            styles: { fontSize: 7, cellPadding: 2, overflow: 'linebreak' },
            headStyles: { fillColor: [243, 244, 246], textColor: [0, 0, 0], fontStyle: 'bold', halign: 'center', fontSize: 7 },
            columnStyles: {
                0: { halign: 'center', cellWidth: 8 },
                1: { cellWidth: 38 },
                2: { cellWidth: 38 },
                3: { cellWidth: 38 },
                4: { cellWidth: 25, halign: 'center' },
                5: { cellWidth: 22, halign: 'center' },
                6: { cellWidth: 45 },
            },
            head: [['No.', 'TEMÁTICA', 'OBJETIVO', 'RESULTADOS ESPERADOS', 'CANALIZACIONES', 'JEFE GRUPO', 'RESULTADOS OBTENIDOS']],
            body: sesiones.map(s => {
                const firma = s.estado === 'Validada' ? 'FIRMADO' : (s.estado === 'Cancelada' ? 'CANCELADA' : 'PENDIENTE');
                const resultado = s.estado === 'Cancelada'
                    ? `Motivo: ${s.motivo || s.motivo_cancelacion || ''}`
                    : (s.resultados_obtenidos || '');
                const canalizaciones = Array.isArray(s.canalizaciones)
                    ? s.canalizaciones.join(', ')
                    : (s.canalizaciones || '—');
                return [
                    s.num || s.num_sesion || '',
                    s.tematica || '',
                    s.objetivo || '',
                    s.resultados_esperados || '',
                    canalizaciones,
                    firma,
                    resultado,
                ];
            }),
        });
    }

    // ── GUARDAR ──
    const filename = opts.filename || `PAT_${opts.grupo || 'PAT'}_${(opts.tutor || '').replace(/ /g, '_')}.pdf`;
    doc.save(filename);
}
