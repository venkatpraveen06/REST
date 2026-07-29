document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);
});

function updateClock() {
    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000/api/v1' 
    : (window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1');
    const clock = document.getElementById('liveClock');
    if (clock) {
        const now = new Date();
        clock.innerText = now.toLocaleTimeString();
    }
}

function updateTicketStatus(ticketId, status) {
    alert(`Order ${ticketId} status updated to: ${status.toUpperCase()}`);
}

function playAlertSound() {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
    osc.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
}
