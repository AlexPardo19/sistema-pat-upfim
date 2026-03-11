// js/layout.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializar iconos de Lucide
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. Cargar los datos del usuario en la interfaz (Header Superior)
    const userEmail = localStorage.getItem('userEmail') || 'usuario@upfim.edu.mx';
    const userRole = localStorage.getItem('userRole') || 'Usuario';
    
    const emailDisplay = document.getElementById('user-email-display');
    const roleDisplay = document.getElementById('user-role-display');
    const avatarLetter = document.getElementById('user-avatar-letter');
    
    if (emailDisplay) emailDisplay.textContent = userEmail;
    
    if (roleDisplay) {
        let roleTitle = 'Usuario';
        if (userRole === 'director-tutorias') roleTitle = 'Director de Tutorías';
        else if (userRole === 'jefe-grupo') roleTitle = 'Jefe de Grupo';
        else if (userRole === 'director-carrera') roleTitle = 'Director de Carrera';
        else if (userRole === 'docente-tutor') roleTitle = 'Docente Tutor';
        
        roleDisplay.textContent = roleTitle;
        // Pone la primera letra del rol en el circulito del avatar (si existe)
        if(avatarLetter) avatarLetter.textContent = roleTitle.charAt(0); 
    }

    // 3. Resaltar en verde el menú activo en el Sidebar (Menú Lateral)
    const currentPath = window.location.pathname.split('/').pop() || 'asignacion-tutores.html';
    const navLinks = document.querySelectorAll('aside nav a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        // Si el enlace coincide con la página actual, le ponemos los colores de la UPFIM
        if (linkPath === currentPath) {
            link.classList.remove('text-gray-700', 'hover:bg-gray-100');
            link.classList.add('text-white', 'bg-[#69B22E]');
        } else {
            // Asegurarnos de que los inactivos tengan el estilo gris correcto
            link.classList.remove('text-white', 'bg-[#69B22E]');
            link.classList.add('text-gray-700', 'hover:bg-gray-100');
        }
    });
});

// 4. Lógica para abrir/cerrar el menú en vista de Celular
function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    
    if(sidebar && overlay) {
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
    }
}