/* ========================================
   Sales Manager Dashboard JavaScript
   ======================================== */

// Protect page - only sales manager can access
auth.protectPage(['sales']);

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
    initPipelineChart();
    initConversionChart();
});

// Sales Pipeline Chart
function initPipelineChart() {
    const ctx = document.getElementById('pipelineChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [
                {
                    label: 'New Inquiries',
                    data: [42, 38, 45, 48],
                    backgroundColor: 'rgba(13, 148, 136, 0.8)',
                    borderColor: 'rgba(13, 148, 136, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Feasible',
                    data: [35, 32, 38, 40],
                    backgroundColor: 'rgba(79, 70, 229, 0.8)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Assigned',
                    data: [28, 26, 30, 32],
                    backgroundColor: 'rgba(249, 115, 22, 0.8)',
                    borderColor: 'rgba(249, 115, 22, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Completed',
                    data: [22, 20, 24, 26],
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
                        stepSize: 10
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// Conversion Rate Chart
function initConversionChart() {
    const ctx = document.getElementById('conversionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Converted', 'In Progress', 'Lost'],
            datasets: [{
                data: [68, 22, 10],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
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
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// Mark inquiry as feasible
function markFeasible(inquiryId) {
    Modal.confirm(
        'Mark as Feasible',
        `Mark inquiry ${inquiryId} as feasible and convert to lead?`,
        () => {
            Toast.info('Processing...', 1000);
            
            setTimeout(() => {
                Toast.success(`${inquiryId} marked as feasible and converted to lead!`, 3000);
                
                // Remove from list
                const listItems = document.querySelectorAll('.list-group-item');
                listItems.forEach(item => {
                    if (item.textContent.includes(inquiryId)) {
                        item.style.transition = 'opacity 0.3s ease';
                        item.style.opacity = '0';
                        setTimeout(() => item.remove(), 300);
                    }
                });
                
                // Update badge count
                updateBadgeCount('.badge.bg-warning', -1);
            }, 1000);
        }
    );
}

// Mark inquiry as not feasible
function markNotFeasible(inquiryId) {
    Modal.confirm(
        'Mark as Not Feasible',
        `Mark inquiry ${inquiryId} as not feasible? This action cannot be undone.`,
        () => {
            Toast.info('Processing...', 1000);
            
            setTimeout(() => {
                Toast.success(`${inquiryId} marked as not feasible`, 3000);
                
                // Remove from list
                const listItems = document.querySelectorAll('.list-group-item');
                listItems.forEach(item => {
                    if (item.textContent.includes(inquiryId)) {
                        item.style.transition = 'opacity 0.3s ease';
                        item.style.opacity = '0';
                        setTimeout(() => item.remove(), 300);
                    }
                });
                
                // Update badge count
                updateBadgeCount('.badge.bg-warning', -1);
            }, 1000);
        }
    );
}

// Update badge count
function updateBadgeCount(selector, delta) {
    const badge = document.querySelector(selector);
    if (badge) {
        const currentCount = parseInt(badge.textContent.match(/\d+/)[0]);
        const newCount = Math.max(0, currentCount + delta);
        badge.textContent = badge.textContent.replace(/\d+/, newCount);
    }
}

// Export report
function exportReport() {
    Toast.info('Generating sales report...', 2000);
    
    setTimeout(() => {
        Toast.success('Report exported successfully!', 3000);
    }, 2000);
}

// Assign engineer to lead
function assignEngineer(leadId) {
    // In a real app, this would show a modal with engineer selection
    const engineers = ['Ravi Kumar', 'Suresh Patel', 'Arun Joshi'];
    const randomEngineer = engineers[Math.floor(Math.random() * engineers.length)];
    
    Toast.info(`Assigning ${randomEngineer} to ${leadId}...`, 1500);
    
    setTimeout(() => {
        Toast.success(`${leadId} assigned to ${randomEngineer}`, 3000);
    }, 1500);
}
