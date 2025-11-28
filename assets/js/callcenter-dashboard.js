/* ========================================
   Call Center Dashboard JavaScript
   ======================================== */

// Protect page - only callcenter can access
auth.protectPage(['callcenter']);

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
    initInquiriesChart();
});

// Inquiries Trend Chart
function initInquiriesChart() {
    const ctx = document.getElementById('inquiriesChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'Created',
                    data: [18, 24, 21, 28, 24, 19, 24],
                    borderColor: 'rgba(13, 148, 136, 1)',
                    backgroundColor: 'rgba(13, 148, 136, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Forwarded',
                    data: [14, 19, 17, 22, 19, 15, 20],
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Closed',
                    data: [10, 14, 12, 16, 14, 11, 15],
                    borderColor: 'rgba(34, 197, 94, 1)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
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
                            return context.dataset.label + ': ' + context.parsed.y + ' inquiries';
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

// View inquiry details
function viewInquiry(inquiryId) {
    // In a real app, this would fetch inquiry details and show in a modal
    const modalHtml = `
        <div class="modal fade" id="inquiryModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Inquiry Details - ${inquiryId}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Customer Name</label>
                                <p>Rajesh Kumar</p>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Phone</label>
                                <p>+91 98765 43210</p>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Email</label>
                                <p>rajesh@email.com</p>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Service Type</label>
                                <p><span class="badge bg-info">Home</span></p>
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-semibold">Address</label>
                                <p>123, MG Road, Sector 5, Bangalore - 560001</p>
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-semibold">Notes</label>
                                <p>Customer interested in 100 Mbps plan. Prefers installation on weekends.</p>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Status</label>
                                <p><span class="badge badge-pending">Pending</span></p>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-semibold">Created</label>
                                <p>5 minutes ago</p>
                            </div>
                        </div>
                        
                        <hr class="my-4">
                        
                        <h6 class="mb-3">Timeline</h6>
                        <div class="timeline">
                            <div class="d-flex mb-3">
                                <div class="flex-shrink-0">
                                    <div class="user-avatar" style="width: 32px; height: 32px; font-size: 0.75rem; background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);">CC</div>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                    <div class="fw-semibold">Inquiry Created</div>
                                    <small class="text-muted">5 minutes ago by Call Center Agent</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="editInquiry('${inquiryId}')">
                            <i class="bi bi-pencil me-2"></i>Edit
                        </button>
                        <button type="button" class="btn btn-success" onclick="forwardInquiry('${inquiryId}')">
                            <i class="bi bi-arrow-right me-2"></i>Forward to Sales
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('inquiryModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('inquiryModal'));
    modal.show();
    
    // Clean up on close
    document.getElementById('inquiryModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Forward inquiry to sales
function forwardInquiry(inquiryId) {
    Modal.confirm(
        'Forward Inquiry',
        `Are you sure you want to forward inquiry ${inquiryId} to the Sales team?`,
        () => {
            // Close any open modals
            const openModal = bootstrap.Modal.getInstance(document.getElementById('inquiryModal'));
            if (openModal) {
                openModal.hide();
            }
            
            // Show loading toast
            Toast.info('Forwarding inquiry...', 2000);
            
            // Simulate API call
            setTimeout(() => {
                Toast.success(`Inquiry ${inquiryId} forwarded successfully!`, 3000);
                
                // Update the table row status
                updateInquiryStatus(inquiryId, 'forwarded');
            }, 1000);
        }
    );
}

// Edit inquiry
function editInquiry(inquiryId) {
    window.location.href = `create-inquiry.html?id=${inquiryId}&mode=edit`;
}

// Update inquiry status in table
function updateInquiryStatus(inquiryId, status) {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const idBadge = row.querySelector('.badge');
        if (idBadge && idBadge.textContent.includes(inquiryId)) {
            const statusCell = row.querySelector('td:nth-child(5)');
            if (statusCell) {
                statusCell.innerHTML = `<span class="badge badge-${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>`;
                
                // Remove forward button if forwarded
                if (status === 'forwarded') {
                    const forwardBtn = row.querySelector('.btn-outline-success');
                    if (forwardBtn) {
                        forwardBtn.remove();
                    }
                }
            }
        }
    });
}

// Quick create inquiry
function quickCreateInquiry() {
    window.location.href = 'create-inquiry.html';
}
