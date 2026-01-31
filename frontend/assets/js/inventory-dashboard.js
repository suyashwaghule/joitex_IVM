/* ========================================
   Inventory Dashboard Logic
   ======================================== */

document.addEventListener('DOMContentLoaded', async function () {
    // Layout.render('inventory') is called in HTML
    await loadInventoryStats();
});

async function loadInventoryStats() {
    try {
        const token = window.auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/inventory/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!await window.auth.checkResponse(response)) return;

        const data = await response.json();

        // Update KPIs if elements exist
        const kpiValues = document.querySelectorAll('.kpi-value');
        if (kpiValues.length >= 4) {
            kpiValues[0].textContent = data.kpi.total_stock || 0;
            kpiValues[1].textContent = data.kpi.low_stock || 0;
            kpiValues[2].textContent = data.kpi.pending_requests || 0;
            kpiValues[3].textContent = data.kpi.todays_movements || 0;
        }

        if (data.chart_data) {
            initStockChart(data.chart_data);
        }

        // Status Chart
        if (data.kpi) {
            initStatusChart(data.kpi);
        }

        await loadInventoryDashboardExtras();

    } catch (e) {
        console.error(e);
        if (window.Toast) Toast.error('Could not load dashboard stats');
    }
}

async function loadInventoryDashboardExtras() {
    try {
        const token = window.auth.token;

        // 1. Fetch Low Stock Items
        const lowStockRes = await fetch('http://127.0.0.1:5000/api/inventory/items?status=low', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const lowItems = await lowStockRes.json();

        const lowTbody = document.querySelector('.col-lg-6:nth-child(1) tbody');
        if (lowTbody) {
            if (lowItems.length === 0) {
                lowTbody.innerHTML = '<tr><td colspan="4" class="text-center p-3 text-muted">No low stock items.</td></tr>';
            } else {
                lowTbody.innerHTML = lowItems.slice(0, 5).map(i => `
                    <tr class="table-danger">
                        <td>
                            <div class="fw-semibold">${i.name}</div>
                            <small class="text-muted">SKU: ${i.sku}</small>
                        </td>
                        <td><span class="badge bg-danger">${i.quantity}</span></td>
                        <td>${i.min_stock_level}</td>
                        <td>
                           <a href="receive.html" class="btn btn-sm btn-primary"><i class="bi bi-cart-plus"></i></a>
                        </td>
                    </tr>
                `).join('');
            }
        }

        // 2. Fetch Recent Transactions
        const txRes = await fetch('http://127.0.0.1:5000/api/inventory/transactions', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const txs = await txRes.json();

        const txList = document.querySelector('.list-group-flush');
        if (txList) {
            if (txs.length === 0) {
                txList.innerHTML = '<div class="p-4 text-center text-muted">No recent transactions.</div>';
            } else {
                txList.innerHTML = txs.slice(0, 5).map(t => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="d-flex align-items-start">
                                <div class="badge bg-${t.transaction_type === 'IN' ? 'success' : (t.transaction_type === 'OUT' ? 'danger' : 'warning')} me-3 mt-1">${t.transaction_type}</div>
                                <div>
                                    <h6 class="mb-1">${t.transaction_type === 'IN' ? 'Stock Received' : 'Stock Issued'}</h6>
                                    <p class="mb-0 text-muted small">${t.quantity}x ${t.item_name || 'Item'}</p>
                                    <small class="text-muted">Ref: ${t.reference || '-'}</small>
                                </div>
                            </div>
                            <small class="text-muted">${new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                        </div>
                    </div>
                `).join('');
            }
        }

        // 3. Top Items (using logic for now just list top quantity items as we don't have separate 'usage' metric API yet)
        const itemsRes = await fetch('http://127.0.0.1:5000/api/inventory/items', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const allItems = await itemsRes.json();
        // Sort by quantity desc for "Most Stocked" as proxy OR client side usage calc
        const topItems = allItems.sort((a, b) => b.quantity - a.quantity).slice(0, 5);

        const topTbody = document.querySelector('.card:last-child tbody');
        if (topTbody) {
            if (topItems.length === 0) {
                topTbody.innerHTML = '<tr><td colspan="6" class="text-center p-3 text-muted">No items in inventory.</td></tr>';
            } else {
                topTbody.innerHTML = topItems.map((i, idx) => `
                    <tr>
                        <td><span class="badge bg-${idx === 0 ? 'warning' : 'secondary'}">${idx + 1}</span></td>
                        <td>
                            <div class="fw-semibold">${i.name}</div>
                            <small class="text-muted">SKU: ${i.sku}</small>
                        </td>
                        <td>${i.category}</td>
                        <td>-</td>
                        <td>${i.quantity} units</td>
                        <td><span class="badge bg-${i.status === 'in_stock' ? 'success' : (i.status === 'low_stock' ? 'warning' : 'danger')}">${i.status.replace('_', ' ')}</span></td>
                    </tr>
                `).join('');
            }
        }

    } catch (e) { console.error(e); }
}

function initStockChart(chartData) {
    const ctx = document.getElementById('stockChart');
    if (!ctx) return;

    if (window.stockChartInstance) window.stockChartInstance.destroy();

    window.stockChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Quantity',
                data: chartData.quantity,
                backgroundColor: 'rgba(147, 51, 234, 0.8)',
                borderColor: 'rgba(147, 51, 234, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true }
            }
        }
    });
}

function initStatusChart(kpi) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;

    if (window.statusChartInstance) window.statusChartInstance.destroy();

    const inStock = kpi.total_skus - kpi.low_stock - kpi.out_of_stock;

    window.statusChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['In Stock', 'Low Stock', 'Out of Stock'],
            datasets: [{
                data: [inStock, kpi.low_stock, kpi.out_of_stock],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function reorderItem(sku) {
    if (window.Toast) {
        window.Toast.info(`Creating reorder request for ${sku}...`, 2000);
        setTimeout(() => {
            window.Toast.success('Reorder request created!', 2000);
        }, 2000);
    }
}

function exportInventory() {
    if (window.Toast) {
        window.Toast.info('Exporting inventory data...', 2000);
        setTimeout(() => {
            window.Toast.success('Inventory exported successfully!', 2000);
        }, 2000);
    }
}
