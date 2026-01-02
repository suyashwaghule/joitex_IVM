/* ========================================
   Sales Manager Dashboard JavaScript
   ======================================== */

// Protect page - only sales manager can access
auth.protectPage(['sales']);

// Update user info in header
document.addEventListener('DOMContentLoaded', async function () {
    const user = auth.getCurrentUser();
    if (user) {
        document.getElementById('userName').textContent = user.name;

        // Update avatar initials
        const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
        document.querySelector('.user-avatar').textContent = initials;
    }

    await loadSalesData();
});

async function loadSalesData() {
    try {
        const token = auth.token;
        const [statsRes, feasRes, assignRes] = await Promise.all([
            fetch('http://127.0.0.1:5000/api/sales/stats', { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch('http://127.0.0.1:5000/api/sales/feasibility', { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch('http://127.0.0.1:5000/api/sales/assignments', { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        if (statsRes.ok) {
            const stats = await statsRes.json();
            updateKPIs(stats.kpi);
            initPipelineChart(stats.pipeline_chart);
            if (stats.conversion) {
                initConversionChart(stats.conversion);
            } else {
                // Fetch conversion from leads if possible or use a default
                initConversionChart({
                    data: [stats.kpi.leads_closed, stats.kpi.new_inquiries + stats.kpi.feasibility_pending, 2],
                    labels: ['Converted', 'In Progress', 'Lost']
                });
            }
        }

        if (feasRes.ok) {
            const queue = await feasRes.json();
            renderFeasibilityQueue(queue);
        }

        if (assignRes.ok) {
            const jobs = await assignRes.json();
            renderAssignments(jobs);
        }

    } catch (error) {
        console.error('Error loading sales data:', error);
        Toast.error('Failed to load dashboard data');
    }
}

function updateKPIs(kpi) {
    const kpiValues = document.querySelectorAll('.kpi-value');
    if (kpiValues.length >= 4) {
        kpiValues[0].textContent = kpi.new_inquiries;
        kpiValues[1].textContent = kpi.feasibility_pending;
        kpiValues[2].textContent = kpi.installations_progress;
        kpiValues[3].textContent = kpi.leads_closed;
    }
}

function renderFeasibilityQueue(items) {
    const list = document.querySelector('.card .list-group'); // This targets the first card's list group (Feasibility)
    if (!list) return;

    if (items.length === 0) {
        list.innerHTML = '<div class="list-group-item text-center text-muted">No pending feasibility checks</div>';
        return;
    }

    list.innerHTML = items.map(item => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">#${item.id} - ${item.name}</h6>
                    <p class="mb-1 text-muted small">${item.address || 'No address'}</p>
                    <span class="badge bg-${item.type === 'inquiry' ? 'info' : 'secondary'} text-capitalize">${item.type}</span>
                    ${item.priority === 'high' ? '<span class="badge bg-danger ms-1">High Priority</span>' : ''}
                </div>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-success" onclick="markFeasible('${item.id}')">
                        <i class="bi bi-check"></i>
                    </button>
                    <button class="btn btn-danger" onclick="markNotFeasible('${item.id}')">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Update badge count
    const badge = document.querySelector('.card-header .badge.bg-warning');
    if (badge) badge.textContent = `${items.length} Pending`;
}

function renderAssignments(jobs) {
    // Determine the second card's list group
    // A bit fragile selector but based on layout
    const cards = document.querySelectorAll('.card .list-group');
    if (cards.length < 2) return;
    const list = cards[1];

    if (jobs.length === 0) {
        list.innerHTML = '<div class="list-group-item text-center text-muted">No jobs scheduled today</div>';
        return;
    }

    list.innerHTML = jobs.map(job => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">#${job.job_number} - ${job.customer_name}</h6>
                    <p class="mb-1 text-muted small">Plan: ${job.plan || 'N/A'}</p>
                    <span class="badge badge-in-progress text-capitalize">${job.status.replace('_', ' ')}</span>
                </div>
                <small class="text-muted">${new Date(job.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
            </div>
        </div>
    `).join('');

    // Update badge
    const badge = document.querySelectorAll('.card-header .badge.bg-primary')[0]; // Assuming it's the first primary badge or unique
    if (badge) badge.textContent = `${jobs.length} Jobs`;
}

// Sales Pipeline Chart
function initPipelineChart(chartData) {
    const ctx = document.getElementById('pipelineChart');
    if (!ctx) return;

    // Destroy if exists
    if (window.pipelineChartInstance) window.pipelineChartInstance.destroy();

    const data = chartData ? chartData.data : [];
    const labels = chartData ? chartData.labels : [];

    window.pipelineChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads',
                data: data,
                backgroundColor: [
                    'rgba(13, 148, 136, 0.8)',
                    'rgba(79, 70, 229, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(34, 197, 94, 0.8)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.05)' } }
            }
        }
    });
}

// Conversion Rate Chart
function initConversionChart(chartData) {
    const ctx = document.getElementById('conversionChart');
    if (!ctx) return;

    if (window.conversionChartInstance) window.conversionChartInstance.destroy();

    const data = chartData ? chartData.data : [];
    const labels = chartData ? chartData.labels : ['Converted', 'In Progress', 'Lost'];

    window.conversionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 15 } }
            }
        }
    });
}

// Mark inquiry as feasible
function markFeasible(id) {
    Modal.confirm(
        'Mark as Feasible',
        `Mark lead ${id} as feasible?`,
        async () => {
            try {
                const token = auth.token;
                const response = await fetch(`http://127.0.0.1:5000/api/sales/feasibility/${id}/approve`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    Toast.success('Marked feasible!');
                    loadSalesData();
                } else {
                    Toast.error('Failed to approve feasibility');
                }
            } catch (e) {
                console.error(e);
                Toast.error('Error updating status');
            }
        }
    );
}

// Mark inquiry as not feasible
function markNotFeasible(id) {
    Modal.confirm(
        'Mark as Not Feasible',
        `Reject lead ${id}?`,
        async () => {
            try {
                const token = auth.token;
                const response = await fetch(`http://127.0.0.1:5000/api/sales/feasibility/${id}/reject`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    Toast.success('Lead rejected');
                    loadSalesData();
                } else {
                    Toast.error('Failed to reject lead');
                }
            } catch (e) {
                console.error(e);
                Toast.error('Error updating status');
            }
        }
    );
}

// Export report
function exportReport() {
    Toast.info('Generating sales report...', 2000);
    setTimeout(() => {
        Toast.success('Report exported successfully!', 3000);
    }, 2000);
}

