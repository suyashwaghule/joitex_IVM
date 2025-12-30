/* ========================================
   Admin Dashboard JavaScript
   ======================================== */

// Protect page - only admin can access
auth.protectPage(['admin']);

// Update user info in header
// Initial event listener removed to avoid redundancy with inline script in dashboard.html

// Leads by Stage Chart
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
            maintainAspectRatio: true,
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
