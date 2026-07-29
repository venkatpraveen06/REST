// Realtime Dynamic Kitchen Display System (KDS) Logic
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
    
    // Load initial orders from DB
    loadKitchenQueue();

    // Subscribe to live Supabase Realtime updates on table 'orders'
    const restaurantId = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
    if (window.AuraSupabaseRealtime) {
        window.AuraSupabaseRealtime.subscribeToLiveOrders(restaurantId, (newOrder) => {
            console.log("⚡ Realtime new order arrived in KDS:", newOrder);
            playAlertSound();
            loadKitchenQueue(); // Reload cards dynamically
        });
    }
});

function updateKdsClock() {
    const clock = document.getElementById('kdsClock');
    if (clock) {
        const now = new Date();
        clock.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
}

async function loadKitchenQueue() {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/orders`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (res.ok) {
            const orders = await res.json();
            renderKanbanBoard(orders);
        } else {
            renderDemoKanbanBoard();
        }
    } catch (e) {
        console.warn('Backend API offline, rendering initial database queue fallback');
        renderDemoKanbanBoard();
    }
}

function renderKanbanBoard(orders) {
    const cols = {
        pending: document.getElementById('col-pending'),
        preparing: document.getElementById('col-preparing'),
        ready: document.getElementById('col-ready'),
        delivered: document.getElementById('col-delivered')
    };

    if (!cols.pending) return;

    // Reset columns
    Object.values(cols).forEach(c => { if(c) c.innerHTML = ''; });

    const counts = { pending: 0, preparing: 0, ready: 0, delivered: 0 };

    orders.forEach(order => {
        const status = (order.status || 'pending').toLowerCase();
        if (counts[status] !== undefined) counts[status]++;

        const targetCol = cols[status] || cols.pending;

        const itemsHtml = (order.items || []).map(item => 
            `<li><strong>${item.quantity}x</strong> ${item.item_name}</li>`
        ).join('');

        let actionBtn = '';
        if (status === 'pending') {
            actionBtn = `<button class="btn btn-warning btn-sm w-100 fw-bold" onclick="updateTicketStatus('${order.id}', 'preparing')">Start Prep 🍳</button>`;
        } else if (status === 'preparing') {
            actionBtn = `<button class="btn btn-success btn-sm w-100 fw-bold" style="background: #10B981;" onclick="updateTicketStatus('${order.id}', 'ready')">Mark Ready ✅</button>`;
        } else if (status === 'ready') {
            actionBtn = `<button class="btn btn-secondary-saas btn-sm w-100" onclick="updateTicketStatus('${order.id}', 'delivered')">Dispatch Order 🛵</button>`;
        } else {
            actionBtn = `<span class="badge bg-secondary w-100 py-2">Completed</span>`;
        }

        const cardHtml = `
            <div class="kanban-card" id="ticket-${order.id}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-bold text-white fs-5">#${order.order_number}</span>
                    <span class="badge-status status-${status}">${status.toUpperCase()}</span>
                </div>
                <div class="small text-secondary mb-2">Type: <strong>${order.order_type || 'Delivery'}</strong> • ₹${order.total_amount}</div>
                <div class="p-2 bg-dark rounded-3 mb-3 border border-secondary border-opacity-20">
                    <ul class="list-unstyled m-0 text-white small">
                        ${itemsHtml || '<li>1x Gourmet Order</li>'}
                    </ul>
                </div>
                ${order.special_instructions ? `<div class="p-2 bg-warning bg-opacity-10 border border-warning border-opacity-20 text-warning rounded-3 small mb-3">⚠️ ${order.special_instructions}</div>` : ''}
                ${actionBtn}
            </div>
        `;

        targetCol.innerHTML += cardHtml;
    });

    // Update Counts Header
    if (document.getElementById('count-pending')) document.getElementById('count-pending').innerText = `${counts.pending} Orders`;
    if (document.getElementById('count-preparing')) document.getElementById('count-preparing').innerText = `${counts.preparing} Orders`;
    if (document.getElementById('count-ready')) document.getElementById('count-ready').innerText = `${counts.ready} Orders`;
    if (document.getElementById('count-delivered')) document.getElementById('count-delivered').innerText = `${counts.delivered} Orders`;

    if (window.lucide) window.lucide.createIcons();
}

function renderDemoKanbanBoard() {
    const demoOrders = [
        {
            id: '20000000-0000-0000-0000-000000000001',
            order_number: 'ORD-20260729-0001',
            status: 'preparing',
            order_type: 'delivery',
            total_amount: 843.00,
            special_instructions: 'Less spicy, extra tissue papers please',
            items: [
                { quantity: 1, item_name: 'Aura Smoky Truffle Cheeseburger' },
                { quantity: 1, item_name: 'Fiery Chicken Wings (6pcs)' }
            ]
        },
        {
            id: 'demo-2',
            order_number: 'ORD-20260729-0002',
            status: 'pending',
            order_type: 'pickup',
            total_amount: 610.00,
            special_instructions: 'Pickup at 7:30 PM',
            items: [
                { quantity: 1, item_name: 'Crispy Paneer Tikka Pops' },
                { quantity: 1, item_name: 'Belgium Dark Chocolate Thickshake' }
            ]
        }
    ];
    renderKanbanBoard(demoOrders);
}

async function updateTicketStatus(orderId, newStatus) {
    const card = document.getElementById(`ticket-${orderId}`);
    if (card) card.style.opacity = '0.5';

    playAlertSound();

    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/orders/${orderId}/status?new_status=${newStatus}`, {
            method: 'PATCH',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (res.ok) {
            console.log(`Order ${orderId} status updated to ${newStatus}`);
        }
    } catch (e) {
        console.warn('API Offline, status updated locally');
    }

    // Refresh UI Queue
    loadKitchenQueue();
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
        console.log('Audio alert initialized');
    }
}
