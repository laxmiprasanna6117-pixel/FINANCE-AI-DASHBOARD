/**
 * Finance Data Analysis & AI Automation Dashboard
 * Production JavaScript Application Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        currency: '$',
        activeSection: 'overview',
        hasData: false,
        filters: {
            startDate: '',
            endDate: '',
            category: 'all',
            frequency: 'monthly',
            search: '',
            page: 1,
            pageSize: 15
        },
        charts: {}
    };

    // DOM Elements
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link, .nav-link-trigger');
    const sections = document.querySelectorAll('.app-section');
    const pageTitle = document.getElementById('page-title');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const activeFilePill = document.getElementById('sidebar-active-file');
    const diagnosticBanner = document.getElementById('diagnostic-banner');
    const diagnosticContent = document.getElementById('diagnostic-content');

    // Section Titles Map
    const sectionTitles = {
        'overview': 'Platform Overview',
        'upload': 'Upload Financial Dataset',
        'dashboard': 'Financial Dashboard',
        'revenue': 'Revenue Analysis',
        'expense': 'Expense Analysis',
        'insights': 'AI Insights & Anomaly Audit',
        'reports': 'Automated Financial Reports',
        'data': 'Data Management Ledger',
        'settings': 'Platform Settings'
    };

    // =========================================================================
    // 1. NAVIGATION & ROUTING
    // =========================================================================
    function navigateTo(sectionId) {
        state.activeSection = sectionId;

        // Update Nav Active States
        document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
            if (link.getAttribute('data-section') === sectionId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Show/Hide Sections
        sections.forEach(sec => {
            if (sec.id === `section-${sectionId}`) {
                sec.classList.remove('d-none');
            } else {
                sec.classList.add('d-none');
            }
        });

        // Update Title
        if (pageTitle && sectionTitles[sectionId]) {
            pageTitle.textContent = sectionTitles[sectionId];
        }

        // Close Mobile Sidebar
        if (sidebar && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }

        // Contextual Data Loads
        if (sectionId === 'insights' || sectionId === 'reports') {
            loadAiInsights();
        } else if (['dashboard', 'revenue', 'expense', 'data'].includes(sectionId)) {
            loadDashboardData();
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            if (targetSection) {
                navigateTo(targetSection);
            }
        });
    });

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // =========================================================================
    // 2. CURRENCY & NUMBER FORMATTING HELPERS
    // =========================================================================
    function formatCurrency(val) {
        if (val === null || val === undefined || isNaN(val)) return `${state.currency}0.00`;
        return `${state.currency}${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    function formatNumber(val) {
        if (val === null || val === undefined || isNaN(val)) return '0';
        return Number(val).toLocaleString('en-US');
    }

    // =========================================================================
    // 3. CHART.JS HELPERS & RENDERING
    // =========================================================================
    function destroyChart(name) {
        if (state.charts[name]) {
            state.charts[name].destroy();
            delete state.charts[name];
        }
    }

    // 1. Revenue & Expense Line/Area Trends
    function renderTrendsChart(timeSeries) {
        destroyChart('trends');
        const ctx = document.getElementById('chart-trends');
        if (!ctx) return;

        state.charts['trends'] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeSeries.labels || [],
                datasets: [
                    {
                        label: 'Gross Revenue',
                        data: timeSeries.revenue || [],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.08)',
                        fill: true,
                        tension: 0.35,
                        borderWidth: 2.5,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Expenditures',
                        data: timeSeries.expenses || [],
                        borderColor: '#dc2626',
                        backgroundColor: 'rgba(220, 38, 38, 0.05)',
                        fill: true,
                        tension: 0.35,
                        borderWidth: 2.5,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (val) => formatCurrency(val) }
                    }
                }
            }
        });
    }

    // 2. Income vs Expenses Donut
    function renderIncomeVsExpenseChart(kpis) {
        destroyChart('incomeVsExpense');
        const ctx = document.getElementById('chart-income-vs-expense');
        if (!ctx) return;

        state.charts['incomeVsExpense'] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Gross Revenue', 'Expenditures'],
                datasets: [{
                    data: [kpis.total_revenue || 0, kpis.total_expenses || 0],
                    backgroundColor: ['#2563eb', '#dc2626'],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12 } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Net Operating Profit Evolution
    function renderProfitEvolutionChart(timeSeries) {
        destroyChart('profitEvolution');
        const ctx = document.getElementById('chart-profit-evolution');
        if (!ctx) return;

        const profits = timeSeries.profit || [];
        const backgroundColors = profits.map(p => p >= 0 ? '#16a34a' : '#dc2626');

        state.charts['profitEvolution'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: timeSeries.labels || [],
                datasets: [{
                    label: 'Net Profit / Operating Margin',
                    data: profits,
                    backgroundColor: backgroundColors,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Net Operating Profit: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (val) => formatCurrency(val) }
                    }
                }
            }
        });
    }

    // 4. Cumulative Cash & Performance Trajectory
    function renderCumulativeChart(timeSeries) {
        destroyChart('cumulative');
        const ctx = document.getElementById('chart-cumulative');
        if (!ctx) return;

        state.charts['cumulative'] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeSeries.labels || [],
                datasets: [
                    {
                        label: 'Cumulative Revenue',
                        data: timeSeries.cumulative_revenue || [],
                        borderColor: '#0f2942',
                        backgroundColor: 'rgba(15, 41, 66, 0.08)',
                        fill: true,
                        tension: 0.3,
                        borderWidth: 2.5
                    },
                    {
                        label: 'Cumulative Expenses',
                        data: timeSeries.cumulative_expenses || [],
                        borderColor: '#d97706',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        borderWidth: 2.5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12 } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (val) => formatCurrency(val) }
                    }
                }
            }
        });
    }

    // 5. Revenue Categories Bar & Share Donut
    function renderRevenueAnalysisCharts(revData) {
        destroyChart('revCats');
        destroyChart('revShare');

        const labels = revData.labels || [];
        const values = revData.values || [];

        // Horizontal Bar
        const ctxBar = document.getElementById('chart-revenue-categories');
        if (ctxBar) {
            state.charts['revCats'] = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Revenue Recognized',
                        data: values,
                        backgroundColor: '#2563eb',
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `Revenue: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#f1f5f9' },
                            ticks: { callback: (val) => formatCurrency(val) }
                        },
                        y: { grid: { display: false } }
                    }
                }
            });
        }

        // Donut Share
        const ctxDonut = document.getElementById('chart-revenue-share');
        if (ctxDonut) {
            const colors = ['#1e3a8a', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#e0e7ff'];
            state.charts['revShare'] = new Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }
    }

    // 6. Expense Categories Bar & Share Donut
    function renderExpenseAnalysisCharts(expData) {
        destroyChart('expCats');
        destroyChart('expShare');

        const labels = expData.labels || [];
        const values = expData.values || [];

        // Horizontal Bar
        const ctxBar = document.getElementById('chart-expense-categories');
        if (ctxBar) {
            state.charts['expCats'] = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Expenditure Recognized',
                        data: values,
                        backgroundColor: '#dc2626',
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `Spend: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#f1f5f9' },
                            ticks: { callback: (val) => formatCurrency(val) }
                        },
                        y: { grid: { display: false } }
                    }
                }
            });
        }

        // Donut Share
        const ctxDonut = document.getElementById('chart-expense-share');
        if (ctxDonut) {
            const colors = ['#991b1b', '#b91c1c', '#dc2626', '#ef4444', '#f87171', '#fca5a5', '#fee2e2'];
            state.charts['expShare'] = new Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }
    }

    // 7. Budget vs Actual Grouped Bar Chart
    function renderBudgetVsActualChart(budgetData) {
        destroyChart('budgetVsActual');
        const ctx = document.getElementById('chart-budget-vs-actual');
        const card = document.getElementById('budget-chart-card');
        if (!ctx || !card) return;

        if (!budgetData || !budgetData.labels || budgetData.labels.length === 0) {
            card.classList.add('d-none');
            return;
        }

        card.classList.remove('d-none');
        state.charts['budgetVsActual'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: budgetData.labels,
                datasets: [
                    {
                        label: 'Planned Budget',
                        data: budgetData.budget,
                        backgroundColor: '#1e3a8a',
                        borderRadius: 4
                    },
                    {
                        label: 'Actual Expenditure',
                        data: budgetData.actual,
                        backgroundColor: '#dc2626',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12 } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (val) => formatCurrency(val) }
                    }
                }
            }
        });
    }

    // =========================================================================
    // 4. DATA FETCHING & POPULATING
    // =========================================================================
    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();

            state.hasData = data.has_data;
            if (data.currency_symbol) state.currency = data.currency_symbol;

            if (data.has_data) {
                if (activeFilePill) activeFilePill.textContent = data.filename || 'Active Dataset';
                
                const recsEl = document.getElementById('overview-records');
                if (recsEl) recsEl.textContent = formatNumber(data.records_count);

                if (data.quality_report) {
                    updateQualityUI(data.quality_report);
                }

                // Check diagnostics
                handleDiagnostics(data.quality_report);
                loadDashboardData();
            } else {
                if (activeFilePill) activeFilePill.textContent = 'None Loaded';
            }
        } catch (err) {
            console.error('Failed to fetch status:', err);
        }
    }

    function updateQualityUI(quality) {
        const qScoreEl = document.getElementById('overview-quality');
        const qScoreVal = document.getElementById('quality-score-val');
        const qBadge = document.getElementById('quality-badge');
        const qCleaned = document.getElementById('q-cleaned-rows');
        const qDups = document.getElementById('q-duplicates');
        const qMissing = document.getElementById('q-missing');
        const qOutliers = document.getElementById('q-outliers');
        const schemaChips = document.getElementById('detected-schema-chips');

        const score = quality.quality_score || 0;
        if (qScoreEl) qScoreEl.textContent = `${score}/100`;
        if (qScoreVal) qScoreVal.textContent = score;
        if (qBadge) qBadge.textContent = `Quality: ${score}%`;
        if (qCleaned) qCleaned.textContent = formatNumber(quality.cleaned_rows);
        if (qDups) qDups.textContent = formatNumber(quality.duplicates_removed);
        if (qMissing) qMissing.textContent = `${quality.missing_cells} (${quality.missing_rate_pct}%)`;
        if (qOutliers) qOutliers.textContent = formatNumber(quality.outlier_count);

        if (schemaChips && quality.columns_detected) {
            schemaChips.innerHTML = '';
            for (const [role, col] of Object.entries(quality.columns_detected)) {
                const chip = document.createElement('span');
                chip.className = 'badge bg-primary-subtle text-primary border';
                chip.innerHTML = `<b>${role.toUpperCase()}:</b> ${col}`;
                schemaChips.appendChild(chip);
            }
        }
    }

    function handleDiagnostics(quality) {
        if (!diagnosticBanner || !diagnosticContent) return;

        if (quality && quality.diagnostics && quality.diagnostics.length > 0) {
            diagnosticBanner.classList.remove('d-none');
            diagnosticContent.innerHTML = `
                <div>
                    <b>Dataset Notice:</b>
                    <ul class="mb-0 ps-3 mt-1 small">
                        ${quality.diagnostics.map(d => `<li>${d}</li>`).join('')}
                    </ul>
                </div>
            `;
        } else {
            diagnosticBanner.classList.add('d-none');
        }
    }

    async function loadDashboardData() {
        if (!state.hasData) return;

        try {
            const res = await fetch('/api/dashboard-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state.filters)
            });
            const data = await res.json();
            if (!data.success) return;

            const k = data.kpis;
            // Update Core KPI cards
            const revEl = document.getElementById('kpi-revenue');
            const expEl = document.getElementById('kpi-expenses');
            const profEl = document.getElementById('kpi-profit');
            const marginBadge = document.getElementById('kpi-margin-badge');
            const txEl = document.getElementById('kpi-tx-count');
            const avgTxEl = document.getElementById('kpi-avg-tx');

            if (revEl) revEl.textContent = formatCurrency(k.total_revenue);
            if (expEl) expEl.textContent = formatCurrency(k.total_expenses);
            if (profEl) {
                profEl.textContent = formatCurrency(k.net_profit);
                profEl.className = `kpi-value ${k.net_profit >= 0 ? 'text-success' : 'text-danger'}`;
            }
            if (marginBadge) {
                marginBadge.textContent = `Margin: ${k.profit_margin_pct.toFixed(1)}%`;
                marginBadge.className = `badge ${k.profit_margin_pct >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'}`;
            }
            if (txEl) txEl.textContent = formatNumber(k.total_transactions);
            if (avgTxEl) avgTxEl.textContent = formatCurrency(k.avg_transaction_value);

            // Update Budget Banner if present
            const budgetBanner = document.getElementById('budget-banner');
            if (budgetBanner) {
                if (k.has_budget) {
                    budgetBanner.classList.remove('d-none');
                    document.getElementById('budget-total').textContent = formatCurrency(k.total_budget);
                    document.getElementById('budget-actual').textContent = formatCurrency(k.total_expenses);
                    const varEl = document.getElementById('budget-variance');
                    varEl.textContent = `${formatCurrency(k.budget_variance)} (${k.budget_variance_pct.toFixed(1)}%)`;
                    varEl.className = k.budget_variance >= 0 ? 'text-success' : 'text-danger';
                } else {
                    budgetBanner.classList.add('d-none');
                }
            }

            // Populate Filter Options
            if (data.filter_options) {
                populateCategoryFilter(data.filter_options.categories);
            }

            // Render Charts
            renderTrendsChart(data.time_series);
            renderIncomeVsExpenseChart(k);
            renderProfitEvolutionChart(data.time_series);
            renderCumulativeChart(data.time_series);
            renderRevenueAnalysisCharts(data.categories.revenue_categories);
            renderExpenseAnalysisCharts(data.categories.expense_categories);
            renderBudgetVsActualChart(data.budget_vs_actual);

            // Populate Table
            if (data.table) {
                populateDataTable(data.table);
            }
        } catch (err) {
            console.error('Failed to load dashboard data:', err);
        }
    }

    function populateCategoryFilter(categories) {
        const select = document.getElementById('filter-category');
        if (!select || !categories) return;

        const currentVal = select.value;
        select.innerHTML = '';
        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.toLowerCase();
            opt.textContent = cat;
            if (opt.value === currentVal) opt.selected = true;
            select.appendChild(opt);
        });
    }

    function populateDataTable(tableData) {
        const head = document.getElementById('data-table-head');
        const body = document.getElementById('data-table-body');
        const rowCount = document.getElementById('table-row-count');
        const pageInfo = document.getElementById('table-page-info');
        const prevBtn = document.getElementById('table-prev-page');
        const nextBtn = document.getElementById('table-next-page');

        if (rowCount) rowCount.textContent = `${tableData.total_rows} Rows`;
        if (pageInfo) pageInfo.textContent = `Page ${tableData.page} of ${tableData.total_pages}`;
        if (prevBtn) prevBtn.disabled = tableData.page <= 1;
        if (nextBtn) nextBtn.disabled = tableData.page >= tableData.total_pages;

        if (head && tableData.headers) {
            head.innerHTML = `<tr>${tableData.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
        }

        if (body && tableData.rows) {
            if (tableData.rows.length === 0) {
                body.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-muted">No records matching filter.</td></tr>';
            } else {
                body.innerHTML = tableData.rows.map(row => `
                    <tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>
                `).join('');
            }
        }
    }

    async function loadAiInsights() {
        if (!state.hasData) return;

        try {
            const res = await fetch('/api/ai-insights', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state.filters)
            });
            const data = await res.json();
            if (!data.success) return;

            const ai = data.insights;

            // 1. Executive Summary Narrative
            const execSumEl = document.getElementById('ai-executive-summary');
            const previewEl = document.getElementById('report-narrative-preview');
            if (execSumEl) execSumEl.textContent = ai.executive_summary;
            if (previewEl) previewEl.textContent = ai.executive_summary;

            // 2. Trend CMGR Metrics
            const trends = ai.trends;
            if (trends && trends.has_trends) {
                const rCmgr = document.getElementById('ai-rev-cmgr');
                const rBadge = document.getElementById('ai-rev-trend-badge');
                const eCmgr = document.getElementById('ai-exp-cmgr');
                const eBadge = document.getElementById('ai-exp-trend-badge');
                const momText = document.getElementById('ai-momentum-text');

                if (rCmgr) rCmgr.textContent = `${trends.revenue_cmgr_pct > 0 ? '+' : ''}${trends.revenue_cmgr_pct.toFixed(1)}%`;
                if (rBadge) rBadge.textContent = trends.revenue_trend;
                if (eCmgr) eCmgr.textContent = `${trends.expense_cmgr_pct > 0 ? '+' : ''}${trends.expense_cmgr_pct.toFixed(1)}%`;
                if (eBadge) eBadge.textContent = trends.expense_trend;
                if (momText) {
                    momText.textContent = trends.margin_expansion 
                        ? 'Operating leverage positive: Revenue growth trajectory exceeds expenditure velocity.'
                        : 'Margin compression warning: Expenditures are outpacing revenue acceleration.';
                }
            }

            // 3. Anomaly Table
            const anoCount = document.getElementById('ai-anomaly-count');
            const anoTbody = document.getElementById('ai-anomalies-tbody');
            if (anoCount) anoCount.textContent = `${ai.anomalies.length} Anomalies Flagged`;
            if (anoTbody) {
                if (ai.anomalies.length === 0) {
                    anoTbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No high-variance anomalies detected. Transactions operate within normal parameters.</td></tr>';
                } else {
                    anoTbody.innerHTML = ai.anomalies.map(a => `
                        <tr>
                            <td class="fw-medium">${a.date}</td>
                            <td><span class="badge bg-light text-dark border">${a.category}</span></td>
                            <td>${a.metric}</td>
                            <td class="fw-bold">${formatCurrency(a.amount)}</td>
                            <td><code>${a.z_score}&sigma;</code></td>
                            <td><span class="badge ${a.severity === 'High' ? 'bg-danger-subtle text-danger' : 'bg-warning-subtle text-warning'}">${a.severity}</span></td>
                            <td class="small text-muted">${a.reason}</td>
                        </tr>
                    `).join('');
                }
            }

            // 4. Strategic Financial Risks
            const riskContainer = document.getElementById('ai-risks-container');
            if (riskContainer) {
                riskContainer.innerHTML = ai.risks.map(r => `
                    <div class="risk-card severity-${r.severity}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="fw-bold small text-dark">${r.title}</span>
                            <span class="badge ${r.severity === 'Critical' || r.severity === 'High' ? 'bg-danger text-white' : 'bg-warning text-dark'}">${r.severity}</span>
                        </div>
                        <p class="small text-muted mb-1">${r.description}</p>
                        <span class="small fw-semibold text-navy"><i class="fa-solid fa-shield me-1"></i>Mitigation: ${r.mitigation}</span>
                    </div>
                `).join('');
            }

            // 5. Actionable Recommendations
            const recsContainer = document.getElementById('ai-recommendations-container');
            const recsReportList = document.getElementById('report-recs-list');
            if (recsContainer) {
                recsContainer.innerHTML = ai.recommendations.map(rec => `
                    <div class="col-md-6">
                        <div class="rec-card h-100">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge bg-primary-subtle text-primary">${rec.category}</span>
                                <i class="fa-solid fa-arrow-trend-up text-muted"></i>
                            </div>
                            <h6 class="fw-bold text-navy mb-1">${rec.title}</h6>
                            <p class="small text-muted mb-2">${rec.action}</p>
                            <span class="small fw-bold text-success"><i class="fa-solid fa-circle-check me-1"></i>${rec.impact}</span>
                        </div>
                    </div>
                `).join('');
            }
            if (recsReportList) {
                recsReportList.innerHTML = ai.recommendations.map(rec => `
                    <div class="list-group-item px-0 py-2 border-bottom">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="fw-bold small text-navy">${rec.title}</span>
                            <span class="badge bg-light text-muted border">${rec.category}</span>
                        </div>
                        <p class="small text-muted mb-1 mt-1">${rec.action}</p>
                        <span class="small text-success fw-semibold"><i class="fa-solid fa-bullseye me-1"></i>${rec.impact}</span>
                    </div>
                `).join('');
            }
        } catch (err) {
            console.error('Failed to load AI insights:', err);
        }
    }

    // =========================================================================
    // 5. FILE UPLOAD & DRAG-AND-DROP
    // =========================================================================
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadForm = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadSpinner = document.getElementById('upload-spinner');
    const selectedFileName = document.getElementById('selected-file-name');

    if (browseBtn && fileInput) {
        browseBtn.addEventListener('click', () => fileInput.click());
    }

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                if (selectedFileName) selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                if (uploadBtn) uploadBtn.disabled = false;
            }
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });
        });
        dropzone.addEventListener('drop', (e) => {
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                const file = fileInput.files[0];
                if (selectedFileName) selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                if (uploadBtn) uploadBtn.disabled = false;
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            if (uploadBtn) uploadBtn.disabled = true;
            if (uploadSpinner) uploadSpinner.classList.remove('d-none');

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (data.success) {
                    state.hasData = true;
                    if (activeFilePill) activeFilePill.textContent = data.filename;
                    if (data.quality_report) {
                        updateQualityUI(data.quality_report);
                        handleDiagnostics(data.quality_report);
                    }
                    navigateTo('dashboard');
                } else {
                    alert(`Upload Error: ${data.error || 'Failed to process dataset.'}`);
                }
            } catch (err) {
                alert(`Network error during upload: ${err.message}`);
            } finally {
                if (uploadBtn) uploadBtn.disabled = false;
                if (uploadSpinner) uploadSpinner.classList.add('d-none');
            }
        });
    }

    // =========================================================================
    // 6. SAMPLE DATASET QUICK-LOADER
    // =========================================================================
    document.querySelectorAll('.sample-loader-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const sampleKey = btn.getAttribute('data-sample');

            try {
                const res = await fetch('/api/load-sample', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sample: sampleKey })
                });
                const data = await res.json();

                if (data.success) {
                    state.hasData = true;
                    if (activeFilePill) activeFilePill.textContent = data.filename;
                    if (data.quality_report) {
                        updateQualityUI(data.quality_report);
                        handleDiagnostics(data.quality_report);
                    }
                    navigateTo('dashboard');
                } else {
                    alert(`Error loading sample: ${data.error}`);
                }
            } catch (err) {
                alert(`Network error: ${err.message}`);
            }
        });
    });

    // =========================================================================
    // 7. FILTERS & EVENT LISTENERS
    // =========================================================================
    const btnApplyFilters = document.getElementById('btn-apply-filters');
    const btnResetFilters = document.getElementById('btn-reset-filters');
    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');
    const categorySelect = document.getElementById('filter-category');
    const tableSearch = document.getElementById('table-search');

    if (btnApplyFilters) {
        btnApplyFilters.addEventListener('click', () => {
            state.filters.startDate = startDateInput ? startDateInput.value : '';
            state.filters.endDate = endDateInput ? endDateInput.value : '';
            state.filters.category = categorySelect ? categorySelect.value : 'all';
            const activeFreq = document.querySelector('input[name="frequency-radio"]:checked');
            state.filters.frequency = activeFreq ? activeFreq.value : 'monthly';
            state.filters.page = 1;
            loadDashboardData();
        });
    }

    if (btnResetFilters) {
        btnResetFilters.addEventListener('click', () => {
            if (startDateInput) startDateInput.value = '';
            if (endDateInput) endDateInput.value = '';
            if (categorySelect) categorySelect.value = 'all';
            const defaultFreq = document.getElementById('freq-monthly');
            if (defaultFreq) defaultFreq.checked = true;

            state.filters.startDate = '';
            state.filters.endDate = '';
            state.filters.category = 'all';
            state.filters.frequency = 'monthly';
            state.filters.page = 1;
            loadDashboardData();
        });
    }

    document.querySelectorAll('input[name="frequency-radio"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.filters.frequency = e.target.value;
            loadDashboardData();
        });
    });

    // Debounced Table Search
    let searchTimeout;
    if (tableSearch) {
        tableSearch.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                state.filters.search = e.target.value;
                state.filters.page = 1;
                loadDashboardData();
            }, 300);
        });
    }

    // Pagination
    const prevBtn = document.getElementById('table-prev-page');
    const nextBtn = document.getElementById('table-next-page');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (state.filters.page > 1) {
                state.filters.page--;
                loadDashboardData();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            state.filters.page++;
            loadDashboardData();
        });
    }

    // Reset dataset buttons
    const btnResetDataset = document.getElementById('btn-reset-dataset');
    const btnSettingsReset = document.getElementById('btn-settings-reset');

    async function triggerReset() {
        if (!confirm('Are you sure you want to reset the active dataset?')) return;
        try {
            await fetch('/api/reset', { method: 'POST' });
            state.hasData = false;
            fetchStatus();
            navigateTo('upload');
        } catch (err) {
            console.error(err);
        }
    }

    if (btnResetDataset) btnResetDataset.addEventListener('click', triggerReset);
    if (btnSettingsReset) btnSettingsReset.addEventListener('click', triggerReset);

    // Currency Setting Selection
    document.querySelectorAll('input[name="curr-sym"]').forEach(radio => {
        radio.addEventListener('change', async (e) => {
            state.currency = e.target.value;
            try {
                await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ currency: state.currency })
                });
                loadDashboardData();
            } catch (err) {
                console.error(err);
            }
        });
    });

    // Sensitivity Slider
    const sensSlider = document.getElementById('anomaly-sensitivity');
    const sensVal = document.getElementById('sensitivity-val');
    if (sensSlider && sensVal) {
        sensSlider.addEventListener('input', (e) => {
            sensVal.textContent = `${e.target.value}%`;
        });
    }

    // =========================================================================
    // 8. AUTHENTICATION ENGINE (LOGIN & REGISTRATION)
    // =========================================================================
    const authModalEl = document.getElementById('authModal');
    const authModal = authModalEl ? new bootstrap.Modal(authModalEl) : null;
    const authLoggedOut = document.getElementById('auth-logged-out');
    const authLoggedIn = document.getElementById('auth-logged-in');
    const userAvatarInitial = document.getElementById('user-avatar-initial');
    const userDisplayName = document.getElementById('user-display-name');
    const userDropdownUsername = document.getElementById('user-dropdown-username');
    const authAlert = document.getElementById('auth-alert');

    const btnOpenLogin = document.getElementById('btn-open-auth-login');
    const btnOpenRegister = document.getElementById('btn-open-auth-register');
    const tabLoginBtn = document.getElementById('tab-login-btn');
    const tabRegisterBtn = document.getElementById('tab-register-btn');
    const btnFillDemo = document.getElementById('btn-fill-demo');
    const btnLogout = document.getElementById('btn-logout');

    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const loginSpinner = document.getElementById('login-spinner');
    const registerSpinner = document.getElementById('register-spinner');

    function showAuthAlert(message, type = 'danger') {
        if (!authAlert) return;
        authAlert.className = `alert alert-${type} py-2 px-3 small mb-3`;
        authAlert.textContent = message;
        authAlert.classList.remove('d-none');
    }

    function clearAuthAlert() {
        if (!authAlert) return;
        authAlert.classList.add('d-none');
        authAlert.textContent = '';
    }

    async function checkAuth() {
        try {
            const res = await fetch('/api/auth/me');
            const data = await res.json();

            if (data.authenticated && data.user) {
                const u = data.user;
                if (authLoggedOut) authLoggedOut.classList.add('d-none');
                if (authLoggedIn) authLoggedIn.classList.remove('d-none');

                const initial = (u.full_name || u.username || 'A').charAt(0).toUpperCase();
                if (userAvatarInitial) userAvatarInitial.textContent = initial;
                if (userDisplayName) userDisplayName.textContent = u.full_name || u.username;
                if (userDropdownUsername) userDropdownUsername.textContent = `@${u.username}`;
            } else {
                if (authLoggedOut) authLoggedOut.classList.remove('d-none');
                if (authLoggedIn) authLoggedIn.classList.add('d-none');
            }
        } catch (err) {
            console.error('Failed to check auth state:', err);
        }
    }

    if (btnOpenLogin && authModal) {
        btnOpenLogin.addEventListener('click', () => {
            clearAuthAlert();
            if (tabLoginBtn) tabLoginBtn.click();
            authModal.show();
        });
    }

    if (btnOpenRegister && authModal) {
        btnOpenRegister.addEventListener('click', () => {
            clearAuthAlert();
            if (tabRegisterBtn) tabRegisterBtn.click();
            authModal.show();
        });
    }

    document.querySelectorAll('.toggle-password-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (!input) return;
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                if (icon) icon.className = 'fa-solid fa-eye-slash';
            } else {
                input.type = 'password';
                if (icon) icon.className = 'fa-solid fa-eye';
            }
        });
    });

    if (btnFillDemo) {
        btnFillDemo.addEventListener('click', () => {
            const uInput = document.getElementById('login-username');
            const pInput = document.getElementById('login-password');
            if (uInput) uInput.value = 'admin';
            if (pInput) pInput.value = 'admin123';
            clearAuthAlert();
        });
    }

    if (formLogin) {
        formLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const username = document.getElementById('login-username')?.value.trim();
            const password = document.getElementById('login-password')?.value;

            if (!username || !password) {
                showAuthAlert('Please enter both username and password.');
                return;
            }

            if (loginSpinner) loginSpinner.classList.remove('d-none');

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();

                if (data.success) {
                    if (authModal) authModal.hide();
                    formLogin.reset();
                    await checkAuth();
                } else {
                    showAuthAlert(data.error || 'Invalid credentials.');
                }
            } catch (err) {
                showAuthAlert(`Network error: ${err.message}`);
            } finally {
                if (loginSpinner) loginSpinner.classList.add('d-none');
            }
        });
    }

    if (formRegister) {
        formRegister.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const full_name = document.getElementById('register-fullname')?.value.trim();
            const username = document.getElementById('register-username')?.value.trim();
            const password = document.getElementById('register-password')?.value;
            const confirmPassword = document.getElementById('register-confirm-password')?.value;

            if (password !== confirmPassword) {
                showAuthAlert('Passwords do not match. Please verify your entry.');
                return;
            }

            if (password.length < 6) {
                showAuthAlert('Password must be at least 6 characters long.');
                return;
            }

            if (registerSpinner) registerSpinner.classList.remove('d-none');

            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, full_name })
                });
                const data = await res.json();

                if (data.success) {
                    if (authModal) authModal.hide();
                    formRegister.reset();
                    await checkAuth();
                } else {
                    showAuthAlert(data.error || 'Failed to register account.');
                }
            } catch (err) {
                showAuthAlert(`Network error: ${err.message}`);
            } finally {
                if (registerSpinner) registerSpinner.classList.add('d-none');
            }
        });
    }

    if (btnLogout) {
        btnLogout.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                await checkAuth();
            } catch (err) {
                console.error('Logout error:', err);
            }
        });
    }

    // Initial Boot
    checkAuth();
    fetchStatus();
});
