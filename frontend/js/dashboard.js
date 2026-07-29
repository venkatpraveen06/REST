// Executive Dashboard Logic
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
});

async function loadDashboardData() {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${getApiBase()}/analytics/dashboard`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (document.getElementById('kpiRevenue')) document.getElementById('kpiRevenue').innerText = `₹${data.today_revenue}`;
            if (document.getElementById('kpiOrdersCount')) document.getElementById('kpiOrdersCount').innerText = data.today_orders_count;
            if (document.getElementById('kpiPendingCount')) document.getElementById('kpiPendingCount').innerText = data.pending_orders_count;
            if (data.recent_orders) renderOrdersTable(data.recent_orders);
        } else {
            renderDemoOrdersTable();
        }
    } catch (e) {
        renderDemoOrdersTable();
    }
}

function renderDemoOrdersTable() {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    const demoOrders = [
        { num: 'ORD-20260729-0001', cust: 'Aarav Sharma (+91 9988776655)', type: 'Delivery', amt: '₹843.00', status: 'preparing' },
        { num: 'ORD-20260729-0002', cust: 'Priya Roy (+91 9811223344)', type: 'Pickup', amt: '₹610.00', status: 'pending' },
        { num: 'ORD-20260729-0003', cust: 'Karan Patel (+91 9722334455)', type: 'Delivery', amt: '₹1,240.00', status: 'delivered' }
    ];

    tbody.innerHTML = demoOrders.map(o => `
        <tr>
            <td class="fw-bold text-white">${o.num}</td>
            <td>${o.cust}</td>
            <td><span class="badge bg-secondary">${o.type}</span></td>
            <td class="fw-bold text-emerald">${o.amt}</td>
            <td><span class="badge-status status-${o.status}">${o.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-light" onclick="updateOrderStatus('${o.num}', 'delivered')">Mark Delivered</button>
            </td>
        </tr>
    `).join('');
}

function updateOrderStatus(orderNum, newStatus) {
    alert(`Order ${orderNum} status updated to: ${newStatus.toUpperCase()}`);
}

function refreshDashboard() {
    loadDashboardData();
}
