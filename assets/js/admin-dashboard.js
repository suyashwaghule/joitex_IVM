/* ========================================
   Admin Dashboard JavaScript
   ======================================== */

// Protect page - only admin can access
auth.protectPage(['admin']);

// Update user info in header
document.addEventListener('DOMContentLoaded', function() {
    const user = auth.getCurrentUser();
    if (user) {
        document.getElementById('userName').textContent = user.name;
        
        // Update avatar initials
        const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
        document.querySelector('.user-avatar').textContent = initials;
    }

    // Initialize charts
    initLeadsChart();
    initOLTChart();
    
    // Simulate real-time updates
    startRealtimeUpdates();
});

// Leads by Stage Chart
function initLeadsChart() {
    const ctx = document.getElementById('leadsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'New Inquiries',
                    data: [12, 19, 15, 17, 14, 21, 18],
                    backgroundColor: 'rgba(13, 148, 136, 0.8)',
                    borderColor: 'rgba(13, 148, 136, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Feasible',
                    data: [8, 14, 11, 13, 10, 16, 14],
                    backgroundColor: 'rgba(79, 70, 229, 0.8)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 1
                },
                {
                    label: 'In Progress',
                    data: [5, 9, 7, 8, 6, 11, 9],
                    backgroundColor: 'rgba(249, 115, 22, 0.8)',
                    borderColor: 'rgba(249, 115, 22, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Installed',
                    data: [3, 6, 5, 6, 4, 8, 7],
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 1
                }
            ]
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
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' leads';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// OLT Status Chart
function initOLTChart() {
    const ctx = document.getElementById('oltChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Online', 'Offline', 'Maintenance'],
            datasets: [{
                data: [45, 2, 1],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
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
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Simulate real-time updates
function startRealtimeUpdates() {
    // Update notification badge randomly
    setInterval(() => {
        const badge = document.querySelector('.notification-badge');
        if (badge && Math.random() > 0.7) {
            badge.style.display = 'block';
            
            // Show toast notification
            const messages = [
                'New inquiry received',
                'Installation completed',
                'Low stock alert',
                'OLT status changed'
            ];
            const randomMessage = messages[Math.floor(Math.random() * messages.length)];
            
            // Uncomment to show toast notifications
            // Toast.info(randomMessage, 3000);
        }
    }, 30000); // Every 30 seconds
}

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
