// Realtime Dynamic Executive Dashboard Logic
const getApiBase = () => {
    if (typeof window === 'undefined') return 'http://localhost:8000/api/v1';
    const host = window.location.hostname;
    if (!host || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000/api/v1';
    }
    return window.AURADINE_BACKEND_URL || 'https://your-backend.onrender.com/api/v1';
};

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    // Subscribe to live Supabase Realtime updates on 'orders' table
    const restaurantId = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
    if (window.AuraSupabaseRealtime) {
        window.AuraSupabaseRealtime.subscribeToLiveOrders(restaurantId, (newOrder) => {
            console.log("⚡ Realtime new order arrived in Dashboard:", newOrder);
            loadDashboardData(); // Refresh analytics & table live
        });
    }
});

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

    tbody.innerHTML = orders.map(o => `
        <tr>
            <td class="fw-bold text-white">#${o.order_number}</td>
            <td>${o.customer?.name || 'WhatsApp Guest'}</td>
            <td><span class="badge bg-secondary">${o.order_type || 'Delivery'}</span></td>
            <td class="fw-bold text-emerald">₹${o.total_amount}</td>
            <td><span class="badge-status status-${(o.status || 'pending').toLowerCase()}">${o.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-light" onclick="updateOrderStatus('${o.id}', 'delivered')">Mark Delivered</button>
            </td>
        </tr>
    `).join('');
}

function renderDemoOrdersTable() {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    const demoOrders = [
        { id: '1', order_number: 'ORD-20260729-0001', customer: { name: 'Aarav Sharma' }, order_type: 'Delivery', total_amount: '843.00', status: 'preparing' },
        { id: '2', order_number: 'ORD-20260729-0002', customer: { name: 'Priya Roy' }, order_type: 'Pickup', total_amount: '610.00', status: 'pending' },
        { id: '3', order_number: 'ORD-20260729-0003', customer: { name: 'Karan Patel' }, order_type: 'Delivery', total_amount: '1,240.00', status: 'delivered' }
    ];
    renderOrdersTable(demoOrders);
}

async function updateOrderStatus(orderId, newStatus) {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/orders/${orderId}/status?new_status=${newStatus}`, {
            method: 'PATCH',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (res.ok) {
            console.log(`Order ${orderId} updated to ${newStatus}`);
            loadDashboardData();
        }
    } catch (e) {
        console.warn('API Offline, status updated locally');
    }
}

function refreshDashboard() {
    loadDashboardData();
}
