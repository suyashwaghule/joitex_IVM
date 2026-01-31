/* ========================================
   Engineer Dashboard Logic
   ======================================== */

async function loadEngineerData() {
    try {
        const token = window.auth.token;
        if (!token) return;

        // In a real app, we would fetch from API
        // const response = await fetch(`${window.auth.apiBaseUrl}/engineer/dashboard`, ...);

        // Mocking data for now as per previous inline scripts or expected behavior

        // Update KPIs
        const kpi = {
            assigned: 5,
            completed: 2,
            travel: '24m',
            rating: 4.8
        };

        updateElement('kpi-assigned', kpi.assigned);
        updateElement('kpi-completed', kpi.completed);
        updateElement('kpi-travel', kpi.travel);
        updateElement('kpi-rating', kpi.rating);

        // Load Jobs
        loadJobs();

        // Load Device Stock
        updateStockDisplay({
            ont: 5,
            router: 3,
            cable: 150
        });

    } catch (e) {
        console.error('Error loading engineer data', e);
    }
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

async function loadJobs() {
    const list = document.getElementById('t-jobs-list');
    if (!list) return;

    list.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border spinner-border-sm text-primary"></div>
        </div>
    `;

    // Simulate API delay
    setTimeout(() => {
        // Mock Jobs
        const jobs = [
            { id: 101, type: 'Installation', time: '09:00 AM', customer: 'Amit Sharma', address: 'Sector 4, Noida', status: 'In Progress' },
            { id: 102, type: 'Repair', time: '11:00 AM', customer: 'TechHub Office', address: 'Sector 62, Noida', status: 'Pending' },
            { id: 103, type: 'Installation', time: '02:00 PM', customer: 'Priya Singh', address: 'Indirapuram', status: 'Pending' },
            { id: 104, type: 'Recovery', time: '04:00 PM', customer: 'Nexus Tower', address: 'Sector 18', status: 'Pending' },
            { id: 105, type: 'Installation', time: '05:30 PM', customer: 'Rohan Gupta', address: 'Vaishali', status: 'Pending' }
        ];

        list.innerHTML = jobs.map(job => `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3">
                <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-light text-primary rounded-circle me-3 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <i class="bi bi-${getJobIcon(job.type)}"></i>
                    </div>
                    <div>
                        <h6 class="mb-0">${job.customer}</h6>
                        <small class="text-muted"><i class="bi bi-geo-alt me-1"></i>${job.address}</small>
                        <div class="d-flex align-items-center mt-1">
                            <span class="badge bg-light text-dark border me-2">${job.type}</span>
                            <small class="text-muted"><i class="bi bi-clock me-1"></i>${job.time}</small>
                        </div>
                    </div>
                </div>
                <div>
                    ${getJobAction(job)}
                </div>
            </div>
        `).join('');
    }, 800);
}

function getJobIcon(type) {
    switch (type.toLowerCase()) {
        case 'installation': return 'router';
        case 'repair': return 'tools';
        case 'recovery': return 'box-seam';
        default: return 'card-checklist';
    }
}

function getJobAction(job) {
    if (job.status === 'In Progress') {
        return `<a href="completion.html?jobId=${job.id}" class="btn btn-sm btn-primary">Complete</a>`;
    }
    return `<a href="assigned-jobs.html?jobId=${job.id}" class="btn btn-sm btn-outline-secondary">View</a>`;
}

function updateStockDisplay(stock) {
    updateElement('stock-ont', stock.ont);
    updateElement('stock-router', stock.router);
    updateElement('stock-cable', stock.cable);

    updateBar('bar-ont', (stock.ont / 10) * 100);
    updateBar('bar-router', (stock.router / 10) * 100);
    updateBar('bar-cable', (stock.cable / 300) * 100);

    // Also init chart if needed, but progress bars might be enough
    initDeviceChart(stock);
}

function updateBar(id, percent) {
    const el = document.getElementById(id);
    if (el) el.style.width = `${percent}%`;
}

function initDeviceChart(stock) {
    const ctx = document.getElementById('deviceChart');
    if (!ctx) return;

    if (window.deviceChartInstance) window.deviceChartInstance.destroy();

    window.deviceChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['ONTs', 'Routers', 'Cable (Bundles)'],
            datasets: [{
                data: [stock.ont, stock.router, Math.ceil(stock.cable / 100)],
                backgroundColor: ['#0d6efd', '#198754', '#0dcaf0']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}
