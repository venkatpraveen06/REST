// Kitchen Display System (KDS) Logic
const getApiBase = () => {
    if (typeof window === 'undefined') return 'http://localhost:8000/api/v1';
    const host = window.location.hostname;
    if (!host || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000/api/v1';
    }
    return window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1';
};

document.addEventListener('DOMContentLoaded', () => {
    updateKdsClock();
    setInterval(updateKdsClock, 1000);
    loadKitchenQueue();
});

function updateKdsClock() {
    const clock = document.getElementById('kdsClock');
    if (clock) {
        const now = new Date();
        clock.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
}

function moveTicket(ticketId, newStatus) {
    const card = document.getElementById(`ticket-${ticketId}`);
    if (card) {
        card.style.opacity = '0.5';
    }
    playAlertSound();
    
    // Call API status patch asynchronously
    const token = localStorage.getItem('auradine_token');
    if (token) {
        fetch(`${getApiBase()}/kitchen/tickets/${ticketId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        }).catch(err => console.log('Backend offline, status updated visually local only'));
    }

    setTimeout(() => {
        alert(`Order #${ticketId} status updated to: ${newStatus.toUpperCase()}`);
    }, 100);
}

function testSoundAlert() {
    playAlertSound();
}

function playAlertSound() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    } catch (e) {
        console.log('Audio playback initialized');
    }
}

async function loadKitchenQueue() {
    const token = localStorage.getItem('auradine_token');
    if (!token) return;
    try {
        const res = await fetch(`${getApiBase()}/kitchen/queue`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            console.log('Kitchen live queue:', data);
        }
    } catch (e) {
        console.log('Using local KDS static queue');
    }
}
