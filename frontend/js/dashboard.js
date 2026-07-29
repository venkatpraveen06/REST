const API_BASE = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    loadDashboardData();
});

function initChart() {
    const ctx = document.getElementById('topItemsChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Smoky Truffle Burger', 'Paneer Tikka Pops', 'Margherita Pizza'],
            datasets: [{
                data: [48, 35, 29],
                backgroundColor: ['#10b981', '#f59e0b', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: { position: 'bottom', labels: { color: '#9ca3af' } }
            }
        }
    });
}

async function loadDashboardData() {
    const token = localStorage.getItem('auradine_token');
    try {
        const res = await fetch(`${API_BASE}/analytics/dashboard`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            document.getElementById('kpiRevenue').innerText = `₹${data.today_revenue}`;
            document.getElementById('kpiOrdersCount').innerText = data.today_orders_count;
            document.getElementById('kpiPendingCount').innerText = data.pending_orders_count;
            renderOrdersTable(data.recent_orders);
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
                <button class="btn btn-sm btn-outline-light" onclick="updateStatus('${o.num}', 'delivered')">Mark Delivered</button>
            </td>
        </tr>
    `).join('');
}

function refreshDashboard() {
    loadDashboardData();
}
