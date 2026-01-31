/* ========================================
   Network Dashboard Logic
   ======================================== */

document.addEventListener('DOMContentLoaded', async function () {
    // Layout.render('network') is called in HTML

    await loadNetworkStats();
    startAutoRefresh();

    // Re-inject Refresh Button into Header
    const headerRight = document.querySelector('.header-right');
    if (headerRight) {
        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'header-action';
        refreshBtn.onclick = refreshAll;
        refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
        refreshBtn.title = "manual refresh";

        // Insert before the user dropdown (last element)
        const userDropdown = headerRight.querySelector('.dropdown');
        if (userDropdown) {
            headerRight.insertBefore(refreshBtn, userDropdown);
        } else {
            headerRight.appendChild(refreshBtn);
        }
    }
});

async function loadNetworkStats() {
    try {
        const token = window.auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/network/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!await window.auth.checkResponse(response)) return;

        const data = await response.json();

        // KPIs
        const kpiValues = document.querySelectorAll('.kpi-value');
        if (kpiValues.length >= 4) {
            kpiValues[0].textContent = `${data.kpi.olts_online || 0}/${data.kpi.olts_total || 0}`;
            kpiValues[1].textContent = data.kpi.olts_offline || 0;
            kpiValues[2].textContent = data.kpi.alerts_today || 0;
            kpiValues[3].textContent = `${data.kpi.ip_utilization || 0}%`;
        }

        // OLT Grid
        await loadOLTGrid();

        // IP Pools
        await loadIPPools();

        // Alerts
        await loadAlerts();

        // Charts
        if (data.uptime_chart) initUptimeChart(data.uptime_chart);
        if (data.outage_distribution) initOutageChart(data.outage_distribution);

        // Header Cards (Status Overview)
        const gridHeader = document.querySelector('.card-header .d-flex.gap-3');
        if (gridHeader) {
            gridHeader.innerHTML = `
                <span><span class="badge bg-success">●</span> Online (${data.kpi.olts_online || 0})</span>
                <span><span class="badge bg-danger">●</span> Offline (${data.kpi.olts_offline || 0})</span>
            `;
        }

    } catch (e) {
        console.error(e);
        if (window.Toast) Toast.error('Failed to load dashboard data');
    }
}

async function loadOLTGrid() {
    try {
        const token = window.auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/network/olts', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const olts = await response.json();

        const grid = document.getElementById('oltGrid');
        if (grid) {
            if (olts.length === 0) {
                grid.innerHTML = '<div class="text-center w-100 p-4 text-muted">No OLTs found</div>';
                return;
            }
            grid.innerHTML = olts.map(olt => `
                <div class="olt-card ${olt.status}" onclick="viewOLT(${olt.id}, '${olt.name}')">
                    <i class="bi bi-hdd-network fs-3 mb-2"></i>
                    <div class="fw-semibold">${olt.name}</div>
                    <small class="text-capitalize">${olt.status}</small>
                </div>
            `).join('');
        }
    } catch (e) { console.error(e); }
}

async function loadIPPools() {
    try {
        const token = window.auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/network/ipam/pools', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const pools = await response.json();

        const tbody = document.getElementById('ipPoolsTbody');
        if (tbody) {
            if (pools.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center p-3">No IP Pools found</td></tr>';
                return;
            }
            tbody.innerHTML = pools.map(pool => {
                const usage = pool.utilization || 0;
                const barColor = usage > 80 ? 'danger' : usage > 60 ? 'warning' : 'success';
                return `
                    <tr>
                        <td><strong>${pool.name}</strong></td>
                        <td><span class="badge bg-${pool.pool_type === 'public' ? 'primary' : 'secondary'}">${pool.pool_type}</span></td>
                        <td>${pool.total_ips}</td>
                        <td>${pool.used_ips}</td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-${barColor}" style="width: ${usage}%">${usage}%</div>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        }
    } catch (e) { console.error(e); }
}

async function loadAlerts() {
    try {
        const token = window.auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/network/incidents', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const allIncidents = await response.json();
        // Filter only active incidents for dashboard widget
        const active = allIncidents.filter(i => i.status !== 'resolved').slice(0, 5);

        const list = document.getElementById('activeAlertsList');
        if (list) {
            if (active.length === 0) {
                list.innerHTML = '<div class="list-group-item text-center text-muted">No active alerts</div>';
                return;
            }
            list.innerHTML = active.map(inc => {
                const icon = inc.severity === 'critical' ? 'exclamation-triangle-fill text-danger' : 'exclamation-circle-fill text-warning';
                return `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="d-flex align-items-start">
                            <i class="bi bi-${icon} fs-4 me-3"></i>
                            <div>
                                <h6 class="mb-1">${inc.title}</h6>
                                <p class="mb-1 text-muted small">${inc.description || 'No description'}</p>
                                <small class="text-muted">Device: ${inc.device_name || 'N/A'}</small>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted d-block">${new Date(inc.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                            <button class="btn btn-sm btn-outline-primary mt-1" onclick="resolveAlert(${inc.id})">
                                Resolve
                            </button>
                        </div>
                    </div>
                </div>
                `;
            }).join('');
        }
    } catch (e) { console.error(e); }
}

function initUptimeChart(chartData) {
    const ctx = document.getElementById('uptimeChart');
    if (!ctx) return;

    if (window.uptimeChartInstance) window.uptimeChartInstance.destroy();

    window.uptimeChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Uptime %',
                data: chartData.data,
                borderColor: 'rgba(22, 163, 74, 1)',
                backgroundColor: 'rgba(22, 163, 74, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                x: { grid: { display: false } },
                y: {
                    min: 99,
                    max: 100,
                    ticks: { callback: value => value + '%' },
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                }
            }
        }
    });
}

function initOutageChart(chartData) {
    const ctx = document.getElementById('outageChart');
    if (!ctx) return;

    if (window.outageChartInstance) window.outageChartInstance.destroy();

    const labels = chartData?.labels || ['No Data'];
    const data = chartData?.data || [0];
    const bgColors = [
        'rgba(239, 68, 68, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(147, 51, 234, 0.8)'
    ];

    window.outageChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function viewOLT(id, name) {
    window.location.href = `olt-details.html?id=${id}`;
}

async function resolveAlert(id) {
    if (window.Modal) {
        window.Modal.confirm('Resolve Alert', 'Mark this incident as resolved?', async () => {
            // Mock resolution
            if (window.Toast) window.Toast.success('Alert resolved', 2000);
            loadNetworkStats();
        });
    }
}

function refreshAll() {
    if (window.Toast) window.Toast.info('Refreshing data...', 1500);
    loadNetworkStats();
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) lastUpdateEl.textContent = 'Just now';
    setTimeout(() => {
        if (window.Toast) window.Toast.success('Data refreshed', 2000);
    }, 1500);
}

function startAutoRefresh() {
    setInterval(() => {
        loadNetworkStats();
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        const lastUpdateEl = document.getElementById('lastUpdate');
        if (lastUpdateEl) lastUpdateEl.textContent = timeStr;
    }, 30000);
}
