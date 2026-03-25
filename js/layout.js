// js/layout.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializar iconos de Lucide
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. Cargar datos del usuario desde la sesión (auth.js)
    const session = typeof window.getSessionData === 'function' ? window.getSessionData() : null;

    // Fallback a claves antiguas por compatibilidad
    const userEmail = (session && session.email) || localStorage.getItem('userEmail') || '';
    const userRole  = (session && session.role)  || localStorage.getItem('userRole')  || '';
    const userName  = (session && session.nombre) || '';

    const ROLE_LABELS = {
        'admin':             'Administrador',
        'director-tutorias': 'Director de Tutorías',
        'director-carrera':  'Director de Carrera',
        'docente-tutor':     'Docente Tutor',
        'jefe-grupo':        'Jefe de Grupo',
    };

    const emailDisplay  = document.getElementById('user-email-display');
    const roleDisplay   = document.getElementById('user-role-display');
    const avatarLetter  = document.getElementById('user-avatar-letter');

    if (emailDisplay) emailDisplay.textContent  = userEmail;
    if (roleDisplay)  roleDisplay.textContent   = ROLE_LABELS[userRole] || userRole;

    if (avatarLetter) {
        // Usar la inicial del nombre si está disponible; si no, la del rol
        const inicial = userName
            ? userName.charAt(0).toUpperCase()
            : (ROLE_LABELS[userRole] || 'U').charAt(0).toUpperCase();
        avatarLetter.textContent = inicial;
    }

    // 3. Resaltar enlace activo en el sidebar
    const currentPage = window.location.pathname.split('/').pop() || '';
    const navLinks    = document.querySelectorAll('aside nav a.nav-link, aside nav a');

    navLinks.forEach(link => {
        const linkFile = (link.getAttribute('href') || '').split('/').pop();

        if (linkFile === currentPage) {
            link.classList.remove('text-gray-700', 'hover:bg-gray-100');
            link.classList.add('text-white', 'bg-[#69B22E]');
            // Quitar hover que sobreescribe el color activo
            link.classList.remove('hover:bg-gray-100');
        } else {
            link.classList.remove('text-white', 'bg-[#69B22E]');
            link.classList.add('text-gray-700', 'hover:bg-gray-100');
        }
    });
});

// 4. Toggle del menú móvil
function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
    }
}