// js/auth.js
// ─────────────────────────────────────────────────────────────────────────────
// Mapa de qué páginas puede visitar cada rol.
// Cualquier página no listada aquí redirige al login.
// ─────────────────────────────────────────────────────────────────────────────
const ROLE_PAGES = {
    'admin':             ['admin.html'],
    'director-tutorias': ['director-tutorias.html'],
    'director-carrera':  [
        'director-carrera.html',
        'alta-docentes.html',
        'asignacion-tutores.html',
        'consultar-pats.html',
        'descargar-pats.html',
        'pat-detail.html'
    ],
    'docente-tutor':     ['docente-tutor.html'],
    'jefe-grupo':        ['jefe-grupo.html'],
};

// Página home de cada rol
const ROLE_HOME = {
    'admin':             'admin.html',
    'director-tutorias': 'director-tutorias.html',
    'director-carrera':  'director-carrera.html',
    'docente-tutor':     'docente-tutor.html',
    'jefe-grupo':        'jefe-grupo.html',
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers de sesión
// ─────────────────────────────────────────────────────────────────────────────
function getSession() {
    try {
        const raw = localStorage.getItem('pat_session');
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function setSession(data) {
    localStorage.setItem('pat_session', JSON.stringify(data));
}

function clearSession() {
    localStorage.removeItem('pat_session');
    // Compatibilidad con versiones anteriores que usaban claves separadas
    localStorage.removeItem('userRole');
    localStorage.removeItem('userEmail');
}

// Función pública para obtener el rol actual (usada en otras páginas)
window.getSessionRole = function () {
    const s = getSession();
    return s ? s.role : null;
};

window.getSessionEmail = function () {
    const s = getSession();
    return s ? s.email : null;
};

window.getSessionData = function () {
    return getSession();
};

// ─────────────────────────────────────────────────────────────────────────────
// Obtener nombre de página actual
// ─────────────────────────────────────────────────────────────────────────────
function getCurrentPage() {
    return window.location.pathname.split('/').pop() || 'login.html';
}

// ─────────────────────────────────────────────────────────────────────────────
// Verificación de acceso
// ─────────────────────────────────────────────────────────────────────────────
function checkAuth() {
    const currentPage = getCurrentPage();
    const isLoginPage  = currentPage === 'login.html' || currentPage === '';
    const session      = getSession();

    // 1. Sin sesión → solo puede estar en el login
    if (!session || !session.role) {
        if (!isLoginPage) {
            window.location.replace('login.html');
        }
        return;
    }

    const { role } = session;

    // 2. Con sesión en el login → redirigir a home del rol
    if (isLoginPage) {
        window.location.replace(ROLE_HOME[role] || 'login.html');
        return;
    }

    // 3. Verificar que el rol tenga permiso para la página actual
    const paginasPermitidas = ROLE_PAGES[role] || [];
    if (!paginasPermitidas.includes(currentPage)) {
        // Acceso no autorizado → redirigir al home del rol
        window.location.replace(ROLE_HOME[role] || 'login.html');
        return;
    }

    // 4. Todo OK → poblar elementos de UI con datos del usuario
    populateUserUI(session);
}

// ─────────────────────────────────────────────────────────────────────────────
// Poblar UI con datos del usuario (header, avatar)
// ─────────────────────────────────────────────────────────────────────────────
function populateUserUI(session) {
    const roleLabels = {
        'admin':             'Administrador',
        'director-tutorias': 'Director de Tutorías',
        'director-carrera':  'Director de Carrera',
        'docente-tutor':     'Docente Tutor',
        'jefe-grupo':        'Jefe de Grupo',
    };

    const roleLabel = roleLabels[session.role] || session.role;

    const emailDisplay = document.getElementById('user-email-display');
    const roleDisplay  = document.getElementById('user-role-display');
    const avatarLetter = document.getElementById('user-avatar-letter');

    if (emailDisplay) emailDisplay.textContent = session.email || '';
    if (roleDisplay)  roleDisplay.textContent  = roleLabel;

    if (avatarLetter) {
        // Mostrar inicial del nombre si está disponible
        const inicial = session.nombre
            ? session.nombre.charAt(0).toUpperCase()
            : roleLabel.charAt(0).toUpperCase();
        avatarLetter.textContent = inicial;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Formulario de Login
// ─────────────────────────────────────────────────────────────────────────────
const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email    = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value.trim();
        const errorEl  = document.getElementById('error-message');
        const loginBtn = document.getElementById('login-btn');
        const originalBtnHtml = loginBtn.innerHTML;

        // UI de carga
        loginBtn.innerHTML = '<span class="flex items-center justify-center gap-2"><i data-lucide="loader-2" class="h-5 w-5 animate-spin"></i> Iniciando...</span>';
        if (typeof lucide !== 'undefined') lucide.createIcons();
        loginBtn.disabled = true;
        errorEl.classList.add('hidden');

        const restoreBtn = () => {
            loginBtn.innerHTML = originalBtnHtml;
            loginBtn.disabled  = false;
        };

        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (data.success) {
                // Guardar sesión completa
                setSession({
                    id:          data.id,
                    nombre:      data.nombre,
                    apellidos:   data.apellidos,
                    email:       data.email,
                    role:        data.role,
                    departamento: data.departamento,
                    grupo:       data.grupo,
                });

                // Redirigir al home del rol
                window.location.href = ROLE_HOME[data.role] || 'login.html';
            } else {
                errorEl.textContent = data.message || 'Correo o contraseña incorrectos';
                errorEl.classList.remove('hidden');
                restoreBtn();
            }
        } catch (err) {
            console.error('[Auth] Error de conexión:', err);
            errorEl.textContent = 'No se pudo conectar con el servidor. Verifica que el servidor Flask esté encendido.';
            errorEl.classList.remove('hidden');
            restoreBtn();
        }
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// Cerrar Sesión (disponible globalmente)
// ─────────────────────────────────────────────────────────────────────────────
window.logout = function () {
    clearSession();
    window.location.replace('login.html');
};

// ─────────────────────────────────────────────────────────────────────────────
// Ejecutar verificación al cargar el DOM
// ─────────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', checkAuth);