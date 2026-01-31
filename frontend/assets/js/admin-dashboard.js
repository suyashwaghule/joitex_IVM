/* ========================================
   Admin Dashboard JavaScript
   ======================================== */

// Protect page - only admin can access
// Protect page - only admin can access
auth.protectPage(['admin']);

document.addEventListener('DOMContentLoaded', async () => {
    // Layout is rendered in HTML script block, but we can do it here too if we want full JS control. 
    // However, HTML calls Layout.render('admin').
    // We will just load data.
    await loadAdminData();
});

async function loadAdminData() {
    try {
        const token = window.auth.token;
        // Mocking checks or real API
        const response = await fetch('http://127.0.0.1:5000/api/dashboard/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        // Use checkResponse to handle 401 auto-logout
        if (!await window.auth.checkResponse(response)) return;

        // If API fails with other errors
        if (!response.ok) throw new Error('Failed to fetch stats');

        const data = await response.json();

        if (data.success) {
            const k = data.kpi;
            updateElement('kpiTotalUsers', k.total_users);
            updateElement('kpiActiveLeads', k.active_leads);
            updateElement('kpiPendingInstalls', k.pending_installs);
            updateElement('kpiLowStock', k.low_stock);
            updateElement('kpiOltsOnline', k.olts_online);
            updateElement('kpiLicenses', k.licenses_expiring);

            // Charts
            if (data.leads_chart) initLeadsChart(data.leads_chart);
            else initLeadsChart(null);

            if (data.olt_chart) initOLTChart(data.olt_chart);
            else initOLTChart(null);

            // Activity & Alerts
            renderActivityList(data.recent_activity || []);
            renderAlertsList(data.system_alerts || []);
        }
    } catch (e) {
        console.error("Failed to load stats", e);
        if (window.Toast) Toast.error('Failed to load dashboard data');
    }
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || '-';
}

function renderActivityList(activities) {
    const container = document.getElementById('recentActivityList');
    if (!container) return;

    if (activities.length === 0) {
        container.innerHTML = '<div class="text-center p-3 text-muted">No recent activity</div>';
        return;
    }

    container.innerHTML = activities.map(act => `
        <div class="list-group-item">
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <div class="user-avatar" style="width: 32px; height: 32px; font-size: 0.75rem;">${act.initials || 'U'}</div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div class="d-flex justify-content-between">
                        <h6 class="mb-1">${act.title}</h6>
                        <small class="text-muted">${act.time_ago}</small>
                    </div>
                    <p class="mb-0 text-muted small">${act.description}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function renderAlertsList(alerts) {
    const container = document.getElementById('systemAlertsList');
    if (!container) return;

    if (alerts.length === 0) {
        container.innerHTML = '<div class="text-center p-3 text-muted">No system alerts</div>';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="list-group-item">
            <div class="d-flex align-items-start">
                <i class="bi bi-${alert.type === 'critical' ? 'exclamation-triangle-fill text-danger' : alert.type === 'warning' ? 'exclamation-circle-fill text-warning' : 'info-circle-fill text-info'} me-3 fs-5"></i>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between">
                        <h6 class="mb-1">${alert.title}</h6>
                        <small class="text-muted">${alert.time_ago}</small>
                    </div>
                    <p class="mb-0 text-muted small">${alert.description}</p>
                </div>
            </div>
        </div>
    `).join('');
}

// Leads by Stage Chart
function initLeadsChart(chartData) {
    const ctx = document.getElementById('leadsChart');
    if (!ctx) return;

    if (window.leadsChartInstance) window.leadsChartInstance.destroy();

    const labels = chartData?.labels || ['No Data'];
    const datasets = chartData?.datasets || [{
        label: 'No Data',
        data: [],
        backgroundColor: 'rgba(200, 200, 200, 0.5)'
    }];

    window.leadsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                }
            }
        }
    });
}

// OLT Status Chart
// OLT Status Chart
function initOLTChart(chartData) {
    const ctx = document.getElementById('oltChart');
    if (!ctx) return;

    if (window.oltChartInstance) window.oltChartInstance.destroy();

    const labels = chartData?.labels || ['No Data'];
    const data = chartData?.data || [1];
    const bgColors = chartData ? [
        'rgba(34, 197, 94, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(245, 158, 11, 0.8)'
    ] : ['rgba(200, 200, 200, 0.2)'];


    window.oltChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            }
        }
    });
}

// Simulate real-time updates


// Export data functionality
function exportData(type) {
    Toast.info(`Exporting ${type} data...`, 2000);

    // Simulate export delay
    setTimeout(() => {
        Toast.success(`${type} data exported successfully!`, 3000);
    }, 1500);
}

// Quick actions
function createUser() {
    window.location.href = 'users.html?action=create';
}

function addPlan() {
    window.location.href = 'plans.html?action=create';
}

function addOLT() {
    window.location.href = 'olts.html?action=create';
}

// Refresh dashboard data
function refreshDashboard() {
    Toast.info('Refreshing dashboard...', 2000);

    // Simulate API call
    setTimeout(() => {
        Toast.success('Dashboard updated!', 2000);

        // Animate KPI cards
        document.querySelectorAll('.kpi-card').forEach((card, index) => {
            setTimeout(() => {
                card.style.animation = 'none';
                setTimeout(() => {
                    card.style.animation = 'pulse 0.5s ease';
                }, 10);
            }, index * 100);
        });
    }, 1000);
}

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
`;
document.head.appendChild(style);
