/* ========================================
   Call Center Dashboard JavaScript
   ======================================== */

// Protect page - only callcenter can access
auth.protectPage(['callcenter']);

// Update user info in header
// Initial event listener merged with the one below to avoid redundancy

async function loadDashboardStats() {
    try {
        const token = auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/callcenter/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const stats = await response.json();

        // Update KPI values
        const kpiValues = document.querySelectorAll('.kpi-value');
        if (kpiValues.length >= 4) {
            kpiValues[0].textContent = stats.today || '-';
            kpiValues[1].textContent = stats.pending || '-';
            kpiValues[2].textContent = stats.forwarded || '-';
            kpiValues[3].textContent = stats.closed || '-';
        }

        if (stats.chart_data) {
            initInquiriesChart(stats.chart_data);
        }
    } catch (err) {
        console.error("Stats load failed", err);
    }
}

async function loadRecentInquiries() {
    try {
        const token = auth.token;
        const response = await fetch('http://127.0.0.1:5000/api/callcenter/inquiries?limit=5', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const inquiries = await response.json();
        renderInquiriesTable(inquiries);
    } catch (err) {
        console.error("Inquiries load failed", err);
    }
}

function renderInquiriesTable(inquiries) {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;

    if (inquiries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No recent inquiries</td></tr>';
        return;
    }

    tbody.innerHTML = inquiries.slice(0, 5).map(inq => `
        <tr>
            <td><span class="badge bg-secondary">${inq.inquiry_number}</span></td>
            <td>
                <div class="fw-semibold">${inq.customer_name}</div>
                <small class="text-muted">${inq.email || ''}</small>
            </td>
            <td>${inq.phone}</td>
            <td><span class="badge bg-info">${inq.service_type}</span></td>
            <td><span class="badge badge-${inq.status}">${inq.status}</span></td>
            <td><small>${new Date(inq.created_at).toLocaleDateString()}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewInquiry('${inq.inquiry_number}')">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${inq.status === 'pending' ? `
                    <button class="btn btn-outline-success" onclick="forwardInquiry('${inq.inquiry_number}')">
                        <i class="bi bi-arrow-right"></i>
                    </button>` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

// Update user info in header
// Update user info in header
document.addEventListener('DOMContentLoaded', function () {
    const user = auth.getCurrentUser();
    if (user) {
        const userNameEl = document.getElementById('userName');
        if (userNameEl) userNameEl.textContent = user.name;

        const avatarEl = document.querySelector('.user-avatar');
        if (avatarEl) {
            const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
            avatarEl.textContent = initials;
        }
    }

    // Initialize
    // initInquiriesChart will be called by loadDashboardStats when data is ready, or called here with empty data
    initInquiriesChart();
    loadDashboardStats();
    loadRecentInquiries();
});

function initInquiriesChart(data) {
    const ctx = document.getElementById('inquiriesChart');
    if (!ctx) return;

    if (window.inquiriesChartInstance) {
        if (data) {
            window.inquiriesChartInstance.data.labels = data.labels;
            window.inquiriesChartInstance.data.datasets[0].data = data.data;
            window.inquiriesChartInstance.update();
        }
        return;
    }

    const labels = data?.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const chartData = data?.data || [0, 0, 0, 0, 0, 0, 0];

    window.inquiriesChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Inquiries',
                data: chartData,
                borderColor: '#0d9488',
                backgroundColor: 'rgba(13, 148, 136, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { display: true, borderDash: [2, 2] }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// View inquiry details (updated to use inquiry_number)
async function viewInquiry(inquiryNum) {
    try {
        const token = auth.token;
        const response = await fetch(`http://127.0.0.1:5000/api/callcenter/inquiries/num/${inquiryNum}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const inq = await response.json();

        const modalHtml = `
            <div class="modal fade" id="inquiryModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Inquiry Details - ${inq.inquiry_number}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Customer Name</label>
                                    <p>${inq.customer_name}</p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Phone</label>
                                    <p>${inq.phone}</p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Email</label>
                                    <p>${inq.email || '-'}</p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Service Type</label>
                                    <p><span class="badge bg-info">${inq.service_type}</span></p>
                                </div>
                                <div class="col-12">
                                    <label class="form-label fw-semibold">Address</label>
                                    <p>${inq.address}, ${inq.city} - ${inq.pincode}</p>
                                </div>
                                <div class="col-12">
                                    <label class="form-label fw-semibold">Notes</label>
                                    <p>${inq.notes || 'No notes'}</p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Status</label>
                                    <p><span class="badge badge-${inq.status}">${inq.status}</span></p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Created</label>
                                    <p>${new Date(inq.created_at).toLocaleString()}</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            ${inq.status === 'pending' ? `
                            <button type="button" class="btn btn-success" onclick="forwardInquiry('${inq.inquiry_number}')">
                                <i class="bi bi-arrow-right me-2"></i>Forward to Sales
                            </button>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('inquiryModal')?.remove();
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('inquiryModal'));
        modal.show();

    } catch (err) {
        console.error("View failed", err);
        Toast.error("Could not load inquiry details");
    }
}

// Forward inquiry to sales
async function forwardInquiry(inquiryNum) {
    Modal.confirm(
        'Forward Inquiry',
        `Are you sure you want to forward inquiry ${inquiryNum} to the Sales team?`,
        async () => {
            bootstrap.Modal.getInstance(document.getElementById('inquiryModal'))?.hide();
            Toast.info('Forwarding inquiry...', 2000);

            try {
                const token = auth.token;
                const response = await fetch(`http://127.0.0.1:5000/api/callcenter/inquiries/num/${inquiryNum}/status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ status: 'forwarded' })
                });

                if (response.ok) {
                    Toast.success(`Inquiry ${inquiryNum} forwarded successfully!`);
                    loadDashboardStats();
                    loadRecentInquiries();
                }
            } catch (err) {
                Toast.error("Forwarding failed");
            }
        }
    );
}

// Quick create inquiry
function quickCreateInquiry() {
    window.location.href = 'create-inquiry.html';
}
