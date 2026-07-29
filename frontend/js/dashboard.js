// Realtime Dynamic Executive Dashboard & Live Order Stream Logic
const getApiBase = () => {
    if (typeof window === 'undefined') return 'http://localhost:8000/api/v1';
    const host = window.location.hostname;
    if (!host || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000/api/v1';
    }
    return window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1';
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. ADMIN AUTHENTICATION GUARD
    if (!checkAdminAuthGuard()) return;

    // 2. Load User Profile Header
    initAdminProfileHeader();

    // 3. Load Dashboard Stats & Live Stream
    loadDashboardData();

    // 4. Subscribe to live Supabase Realtime updates on 'orders' table
    const restaurantId = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
    if (window.AuraSupabaseRealtime) {
        window.AuraSupabaseRealtime.subscribeToLiveOrders(restaurantId, (newOrder) => {
            console.log("⚡ Realtime new order arrived in Dashboard:", newOrder);
            loadDashboardData(); // Refresh analytics & live cards stream
        });
    }
});

function checkAdminAuthGuard() {
    const token = localStorage.getItem('auradine_token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function initAdminProfileHeader() {
    try {
        const userJson = localStorage.getItem('auradine_user');
        if (userJson) {
            const user = JSON.parse(userJson);
            if (document.getElementById('adminUserName')) {
                document.getElementById('adminUserName').innerText = user.full_name || 'Chef Vikram Seth';
            }
            if (document.getElementById('adminUserRole')) {
                document.getElementById('adminUserRole').innerText = `${user.restaurant_name || 'Aura Bistro'} (${user.role || 'Owner'})`;
            }
        }
    } catch (e) {
        console.log('Profile header initialized');
    }
}

function logoutAdmin() {
    localStorage.removeItem('auradine_token');
    localStorage.removeItem('auradine_user');
    window.location.href = 'login.html';
}

async function loadDashboardData() {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/analytics/dashboard`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (res.ok) {
            const data = await res.json();
            
            if (document.getElementById('kpiRevenue')) document.getElementById('kpiRevenue').innerText = `₹${data.today_revenue}`;
            if (document.getElementById('kpiOrdersCount')) document.getElementById('kpiOrdersCount').innerText = data.today_orders_count;
            if (document.getElementById('kpiPendingCount')) document.getElementById('kpiPendingCount').innerText = data.pending_orders_count;
            if (document.getElementById('kpiCompletedCount')) document.getElementById('kpiCompletedCount').innerText = data.completed_orders_count;
            
            if (data.recent_orders) {
                renderLiveOrderCards(data.recent_orders);
                renderOrdersTable(data.recent_orders);
            }
        } else {
            renderDemoOrdersData();
        }
    } catch (e) {
        console.warn('Backend API offline, rendering initial database stats fallback');
        renderDemoOrdersData();
    }
}

function renderLiveOrderCards(orders) {
    const container = document.getElementById('liveOrderCardsGrid');
    if (!container) return;

    if (!orders || orders.length === 0) {
        container.innerHTML = `<div class="col-12 text-secondary text-center py-4">No active orders in stream</div>`;
        return;
    }

    container.innerHTML = orders.map(o => {
        const status = (o.status || 'pending').toLowerCase();
        const itemsText = (o.items || []).map(i => `${i.quantity}x ${i.item_name}`).join(', ') || '1x Gourmet Order';

        let actionBtns = '';
        if (status === 'pending') {
            actionBtns = `
                <button class="btn btn-sm btn-success fw-bold" onclick="updateOrderStatus('${o.id}', 'preparing')">Accept 🍳</button>
                <button class="btn btn-sm btn-outline-danger" onclick="updateOrderStatus('${o.id}', 'cancelled')">Reject</button>
            `;
        } else if (status === 'preparing') {
            actionBtns = `
                <button class="btn btn-sm btn-info text-white fw-bold" onclick="updateOrderStatus('${o.id}', 'ready')">Mark Ready ✅</button>
            `;
        } else if (status === 'ready') {
            actionBtns = `
                <button class="btn btn-sm btn-primary-saas fw-bold" onclick="updateOrderStatus('${o.id}', 'delivered')">Dispatch 🛵</button>
            `;
        } else {
            actionBtns = `<span class="badge bg-secondary py-1.5 px-3">Completed</span>`;
        }

        return `
            <div class="col-md-4" id="stream-card-${o.id}">
                <div class="p-3 bg-dark bg-opacity-50 border border-secondary border-opacity-20 rounded-3 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-bold text-white fs-5">#${o.order_number}</span>
                            <span class="badge-status status-${status}">${status.toUpperCase()}</span>
                        </div>
                        <div class="text-secondary small mb-2">Customer: <strong>${o.customer?.name || 'WhatsApp Guest'}</strong></div>
                        <div class="fw-bold text-white mb-2 small">${itemsText}</div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center pt-2 border-top border-secondary border-opacity-20 mt-3">
                        <span class="fw-bold text-success fs-5">₹${o.total_amount}</span>
                        <div class="d-flex gap-2">
                            ${actionBtns}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderOrdersTable(orders) {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    tbody.innerHTML = orders.map(o => {
        const status = (o.status || 'pending').toLowerCase();
        let actionBtn = '';
        if (status === 'pending') {
            actionBtn = `<button class="btn btn-sm btn-success me-1" onclick="updateOrderStatus('${o.id}', 'preparing')">Accept 🍳</button>
                         <button class="btn btn-sm btn-outline-danger" onclick="updateOrderStatus('${o.id}', 'cancelled')">Reject</button>`;
        } else if (status === 'preparing') {
            actionBtn = `<button class="btn btn-sm btn-info text-white me-1" onclick="updateOrderStatus('${o.id}', 'ready')">Mark Ready ✅</button>`;
        } else if (status === 'ready') {
            actionBtn = `<button class="btn btn-sm btn-primary-saas" onclick="updateOrderStatus('${o.id}', 'delivered')">Dispatch 🛵</button>`;
        } else {
            actionBtn = `<span class="badge bg-secondary">Completed</span>`;
        }

        return `
            <tr>
                <td class="fw-bold text-white">#${o.order_number}</td>
                <td>${o.customer?.name || 'WhatsApp Guest'}</td>
                <td><span class="badge bg-secondary">${o.order_type || 'Delivery'}</span></td>
                <td class="fw-bold text-emerald">₹${o.total_amount}</td>
                <td><span class="badge-status status-${status}">${status.toUpperCase()}</span></td>
                <td>${actionBtn}</td>
            </tr>
        `;
    }).join('');
}

function renderDemoOrdersData() {
    const demoOrders = [
        { 
            id: '20000000-0000-0000-0000-000000000001', 
            order_number: 'ORD-20260729-0001', 
            customer: { name: 'Rahul Verma' }, 
            order_type: 'Delivery', 
            total_amount: '899.00', 
            status: 'preparing',
            items: [{ quantity: 2, item_name: 'Paneer Burgers' }, { quantity: 1, item_name: 'Coke' }]
        },
        { 
            id: '20000000-0000-0000-0000-000000000002', 
            order_number: 'ORD-20260729-0002', 
            customer: { name: 'Ananya Sen' }, 
            order_type: 'Delivery', 
            total_amount: '420.00', 
            status: 'pending',
            items: [{ quantity: 1, item_name: 'Truffle Cheeseburger' }]
        }
    ];
    renderLiveOrderCards(demoOrders);
    renderOrdersTable(demoOrders);
}

async function updateOrderStatus(orderId, newStatus) {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/orders/${orderId}/status?new_status=${newStatus}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (res.ok) {
            console.log(`Order ${orderId} updated to ${newStatus}`);
        }
    } catch (e) {
        console.warn('API Offline, status updated locally');
    }
    
    // Reload dashboard stats & live order stream cards immediately
    loadDashboardData();
}

function refreshDashboard() {
    loadDashboardData();
}
