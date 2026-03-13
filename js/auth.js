// js/auth.js

const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // El .trim() elimina los espacios en blanco accidentales que el usuario ponga al inicio o al final
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        
        const errorMessage = document.getElementById('error-message');
        const loginBtn = document.getElementById('login-btn');
        const originalBtnText = loginBtn.innerHTML;

        try {
            loginBtn.innerHTML = '<span class="flex items-center justify-center"><i data-lucide="loader-2" class="h-5 w-5 mr-2 animate-spin"></i> Iniciando...</span>';
            if(typeof lucide !== 'undefined') lucide.createIcons();
            loginBtn.disabled = true;
            errorMessage.classList.add('hidden');

            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (data.success) {
                localStorage.setItem('userRole', data.role);
                localStorage.setItem('userEmail', data.email);

                // Como estamos en paginas/login.html, redirigimos directamente a los archivos HTML en la misma carpeta
                if (data.role === 'admin') window.location.href = 'admin.html';
                else if (data.role === 'director-tutorias') window.location.href = 'director-tutorias.html';
                else if (data.role === 'director-carrera') window.location.href = 'director-carrera.html';
                else if (data.role === 'docente-tutor') window.location.href = 'docente-tutor.html';
                else if (data.role === 'jefe-grupo') window.location.href = 'jefe-grupo.html';
            } else {
                errorMessage.textContent = data.message || 'Error al iniciar sesión';
                errorMessage.classList.remove('hidden');
                loginBtn.innerHTML = originalBtnText;
                loginBtn.disabled = false;
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = 'Error de conexión. Verifica que el servidor Flask esté encendido.';
            errorMessage.classList.remove('hidden');
            loginBtn.innerHTML = originalBtnText;
            loginBtn.disabled = false;
        }
    });
}

// Validación de seguridad para que nadie entre a los paneles sin iniciar sesión
function checkAuth() {
    const currentPath = window.location.pathname;
    const isLoginPage = currentPath.endsWith('login.html');
    
    const userRole = localStorage.getItem('userRole');
    const userEmail = localStorage.getItem('userEmail');

    if (!userRole && !isLoginPage) {
        window.location.href = 'login.html';
    } 
    else if (userRole && isLoginPage) {
        if (userRole === 'admin') window.location.href = 'admin.html';
        else if (userRole === 'director-tutorias') window.location.href = 'director-tutorias.html';
        else if (userRole === 'director-carrera') window.location.href = 'director-carrera.html';
        else if (userRole === 'docente-tutor') window.location.href = 'docente-tutor.html';
        else if (userRole === 'jefe-grupo') window.location.href = 'jefe-grupo.html';
    }

    if (!isLoginPage) {
        const roleDisplay = document.getElementById('user-role-display');
        const emailDisplay = document.getElementById('user-email-display');
        
        if (roleDisplay && userRole) {
            const formattedRole = userRole.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            roleDisplay.textContent = formattedRole;
        }
        if (emailDisplay && userEmail) {
            emailDisplay.textContent = userEmail;
        }
    }
}

// Función global para Cerrar Sesión
window.logout = function() {
    localStorage.removeItem('userRole');
    localStorage.removeItem('userEmail');
    window.location.href = 'login.html'; // Lo devuelve a paginas/login.html
};

document.addEventListener('DOMContentLoaded', checkAuth);