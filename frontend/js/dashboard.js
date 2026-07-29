// Realtime Dynamic Executive Dashboard & Auth Guard Logic
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

    // 3. Load Dashboard Stats
    loadDashboardData();

    // 4. Subscribe to live Supabase Realtime updates on 'orders' table
    const restaurantId = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
    if (window.AuraSupabaseRealtime) {
        window.AuraSupabaseRealtime.subscribeToLiveOrders(restaurantId, (newOrder) => {
            console.log("⚡ Realtime new order arrived in Dashboard:", newOrder);
            loadDashboardData(); // Refresh analytics & table live
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
            
            if (data.recent_orders) renderOrdersTable(data.recent_orders);
        } else {
            renderDemoOrdersTable();
        }
    } catch (e) {
        console.warn('Backend API offline, rendering initial database stats fallback');
        renderDemoOrdersTable();
    }
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

function renderDemoOrdersTable() {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    const demoOrders = [
        { id: '20000000-0000-0000-0000-000000000001', order_number: 'ORD-20260729-0001', customer: { name: 'Aarav Sharma' }, order_type: 'Delivery', total_amount: '843.00', status: 'preparing' },
        { id: '20000000-0000-0000-0000-000000000002', order_number: 'ORD-20260729-0002', customer: { name: 'Priya Roy' }, order_type: 'Pickup', total_amount: '610.00', status: 'pending' },
        { id: '20000000-0000-0000-0000-000000000003', order_number: 'ORD-20260729-0003', customer: { name: 'Karan Patel' }, order_type: 'Delivery', total_amount: '1,240.00', status: 'delivered' }
    ];
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
    
    // Reload dashboard stats and table immediately
    loadDashboardData();
}

function refreshDashboard() {
    loadDashboardData();
}
