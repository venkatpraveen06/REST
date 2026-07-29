const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000/api/v1' 
    : (window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1');


document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
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
            alert(data.detail || 'Login failed');
        }
    } catch (err) {
        console.warn('API Offline - Redirecting to demo dashboard...');
        window.location.href = 'dashboard.html';
    }
});
