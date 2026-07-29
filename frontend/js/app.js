// Admin JWT Login & Authentication Handler
const getApiBase = () => {
    if (typeof window === 'undefined') return 'http://localhost:8000/api/v1';
    const host = window.location.hostname;
    if (!host || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000/api/v1';
    }
    return window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1';
};

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;

    try {
        const response = await fetch(`${getApiBase()}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('auradine_token', data.access_token);
            localStorage.setItem('auradine_user', JSON.stringify(data.user));
            window.location.href = 'dashboard.html';
        } else {
            // Fallback for demo login if API is starting
            if (email === 'admin@aurabistro.com' && password === 'password123') {
                saveDemoSession();
                window.location.href = 'dashboard.html';
            } else {
                alert(data.detail || 'Invalid admin credentials');
            }
        }
    } catch (err) {
        console.warn('Backend API Offline - Initializing demo admin session');
        if (email === 'admin@aurabistro.com' && password === 'password123') {
            saveDemoSession();
            window.location.href = 'dashboard.html';
        } else {
            alert('Invalid credentials. Use admin@aurabistro.com / password123');
        }
    }
});

function saveDemoSession() {
    const demoUser = {
        id: 'u1b2c3d4-e5f6-7890-abcd-ef1234567892',
        email: 'admin@aurabistro.com',
        full_name: 'Chef Vikram Seth',
        role: 'restaurant_owner',
        restaurant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        restaurant_name: 'Aura Bistro & Grill'
    };
    localStorage.setItem('auradine_token', 'demo_jwt_token_admin_authenticated');
    localStorage.setItem('auradine_user', JSON.stringify(demoUser));
}
