// auth.js - Sistema PAT
var API_BASE = 'http://localhost:5000/api';

var ROLE_PAGES = {
    'admin': ['admin.html'],
    'director-tutorias': ['director-tutorias.html'],
    'director-carrera': ['director-carrera.html'],
    'docente-tutor': ['docente-tutor.html'],
    'jefe-grupo': ['jefe-grupo.html']
};
var ROLE_HOME = {
    'admin':'admin.html', 'director-tutorias':'director-tutorias.html',
    'director-carrera':'director-carrera.html', 'docente-tutor':'docente-tutor.html',
    'jefe-grupo':'jefe-grupo.html'
};

function getSession() {
    try { return JSON.parse(localStorage.getItem('pat_session')); } catch(e) { return null; }
}
function setSession(d) { localStorage.setItem('pat_session', JSON.stringify(d)); }
function clearSession() { localStorage.removeItem('pat_session'); }
window.getSessionRole = function() { var s=getSession(); return s?s.role:null; };
window.getSessionEmail = function() { var s=getSession(); return s?s.email:null; };
window.getSessionData = function() { return getSession(); };
window.logout = function() { clearSession(); window.location.replace('login.html'); };

function getCurrentPage() {
    var p = window.location.pathname.split('/');
    return p[p.length-1] || 'login.html';
}

function checkAuth() {
    var page = getCurrentPage();
    var isLogin = (page === 'login.html' || page === '');
    var s = getSession();
    if (!s || !s.role) { if (!isLogin) window.location.replace('login.html'); return; }
    if (isLogin) { window.location.replace(ROLE_HOME[s.role]||'login.html'); return; }
    var ok = ROLE_PAGES[s.role] || [];
    if (ok.indexOf(page) === -1) { window.location.replace(ROLE_HOME[s.role]||'login.html'); return; }
    // Poblar header
    var labels = {'admin':'Administrador','director-tutorias':'Director de Tutorias','director-carrera':'Director de Carrera','docente-tutor':'Docente Tutor','jefe-grupo':'Jefe de Grupo'};
    var lbl = labels[s.role] || s.role;
    var el1 = document.getElementById('user-email-display');
    var el2 = document.getElementById('user-role-display');
    var el3 = document.getElementById('user-avatar-letter');
    if (el1) el1.textContent = s.email || '';
    if (el2) el2.textContent = lbl;
    if (el3) el3.textContent = s.nombre ? s.nombre.charAt(0).toUpperCase() : 'U';
}

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();

    // Login form handler
    var form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var email = document.getElementById('email').value.trim().toLowerCase();
        var pwd = document.getElementById('password').value.trim();
        var errEl = document.getElementById('error-message');
        var btn = document.getElementById('login-btn');

        if (!email || !pwd) {
            errEl.textContent = 'Ingresa correo y contrasena';
            errEl.classList.remove('hidden');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Conectando...';
        errEl.classList.add('hidden');

        var xhr = new XMLHttpRequest();
        xhr.open('POST', API_BASE + '/login', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.timeout = 10000;

        xhr.onload = function() {
            try {
                var data = JSON.parse(xhr.responseText);
                if (data.success) {
                    setSession({
                        id: data.id, nombre: data.nombre, apellidos: data.apellidos,
                        email: data.email, role: data.role, departamento: data.departamento,
                        grupo: data.grupo, tutor_id: data.tutor_id
                    });
                    window.location.href = ROLE_HOME[data.role] || 'login.html';
                } else {
                    errEl.textContent = data.message || 'Credenciales incorrectas';
                    errEl.classList.remove('hidden');
                    btn.disabled = false;
                    btn.textContent = 'Iniciar Sesion';
                }
            } catch(ex) {
                errEl.textContent = 'Error inesperado. Abre consola (F12) para mas info.';
                errEl.classList.remove('hidden');
                btn.disabled = false;
                btn.textContent = 'Iniciar Sesion';
                console.error('Parse error:', ex, 'Response:', xhr.responseText);
            }
        };
        xhr.onerror = function() {
            errEl.textContent = 'No se pudo conectar. Verifica que Flask este corriendo: python app.py (puerto 5000)';
            errEl.classList.remove('hidden');
            btn.disabled = false;
            btn.textContent = 'Iniciar Sesion';
        };
        xhr.ontimeout = function() {
            errEl.textContent = 'Tiempo agotado. El servidor no responde.';
            errEl.classList.remove('hidden');
            btn.disabled = false;
            btn.textContent = 'Iniciar Sesion';
        };

        xhr.send(JSON.stringify({email: email, password: pwd}));
    });
});
