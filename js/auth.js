  // js/auth.js


// 1. Proteger rutas: Verifica si el usuario tiene permiso de estar en la página actual
function checkAuth() {
    const isAuth = localStorage.getItem('isAuthenticated');
    const currentPath = window.location.pathname;
    
    const isLoginPage = currentPath.includes('login.html') || currentPath.endsWith('/');

    // Si NO está logueado y NO está en el login -> Lo mandamos al login
    if (!isAuth && !isLoginPage) {
        window.location.href = 'login.html';
    }
    
    // Si SÍ está logueado y trata de ver el login -> Lo regresamos a su dashboard correspondiente
    if (isAuth && isLoginPage) {
        redirectByRole(localStorage.getItem('userRole'));
    }
}


// 2. Función para iniciar sesión (Conectada a la API en Python)
async function login(email, password) {
    try {
        const response = await fetch('http://localhost:5000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Guardamos los datos reales que vienen de la BD
            localStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('userRole', data.role);
            localStorage.setItem('userEmail', data.email);
            
            redirectByRole(data.role);
            return { success: true };
        } else {
            return { success: false, message: data.message || 'Error en la autenticación' };
        }
    } catch (error) {
        console.error('Error al conectar con el servidor:', error);
        return { success: false, message: 'No se pudo conectar con el servidor. Verifica que Flask esté corriendo.' };
    }
}

// 3. Función para cerrar sesión
function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

// 4. Redirección basada en roles
function redirectByRole(role) {
    if (role === 'director-tutorias') window.location.href = 'director-tutorias.html';
    else if (role === 'jefe-grupo') window.location.href = 'jefe-grupo.html';
    else if (role === 'director-carrera') window.location.href = 'director-carrera.html';
    else if (role === 'docente-tutor') window.location.href = 'docente-tutor.html'; 
    else window.location.href = 'asignacion-tutores.html'; // Default (Administrador/Control Escolar)
}

// Ejecutamos la validación inmediatamente al cargar el script en cualquier página
checkAuth();