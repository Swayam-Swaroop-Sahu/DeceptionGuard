import { analyzeEmail, fetchEvaluationSummary, processBatch, fetchRobustnessSummary } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emailInput = document.getElementById('emailInput');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMsg = document.getElementById('errorMsg');

    const resultsCard = document.getElementById('resultsCard');
    const emailViewCard = document.getElementById('emailViewCard');

    const riskScore = document.getElementById('riskScore');
    const riskBadge = document.getElementById('riskBadge');
    const riskDonutFill = document.getElementById('riskDonutFill');
    const riskRecommendation = document.getElementById('riskRecommendation');
    const factorWaterfall = document.getElementById('factorWaterfall');
    const evidenceTableBody = document.getElementById('evidenceTableBody');
    const intentGraphGrid = document.getElementById('intentGraphGrid');
    const emailContent = document.getElementById('emailContent');

    function defang(text) {
        if (!text) return '';
        // Defang URLs and sanitize HTML by replacing < and >
        return text.replace(/http/gi, 'hxxp')
            .replace(/\./g, '[.]')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function renderResults(data) {
        resultsCard.classList.remove('hidden');
        emailViewCard.classList.remove('hidden');

        // Risk Score & Badge
        riskScore.textContent = data.score;
        riskBadge.textContent = data.level;
        riskBadge.className = `badge badge-${data.level.toLowerCase()}`;

        // Update Donut
        const maxDash = 339.292;
        const offset = maxDash - (Math.min(data.score, 100) / 100) * maxDash;
        setTimeout(() => {
            riskDonutFill.style.strokeDashoffset = offset;

            let strokeColor = 'var(--color-risk-low)';
            if (data.level === 'MEDIUM') strokeColor = 'var(--color-risk-medium)';
            else if (data.level === 'HIGH' || data.level === 'CRITICAL') strokeColor = 'var(--color-risk-high)';
            else if (data.level === 'MINIMAL') strokeColor = 'var(--color-risk-minimal)';

            riskDonutFill.style.stroke = strokeColor;
            if (riskRecommendation) {
                riskRecommendation.style.borderLeftColor = strokeColor;
            }
        }, 50);

        if (riskRecommendation) {
            riskRecommendation.classList.remove('hidden');
            if (data.level === 'CRITICAL' || data.level === 'HIGH') {
                riskRecommendation.innerHTML = `<span style="color: var(--color-risk-high);">⚠️ <strong>CAUTION:</strong> High risk detected! Do not click any links or download attachments. Report to IT immediately.</span>`;
            } else if (data.level === 'MEDIUM') {
                riskRecommendation.innerHTML = `<span style="color: var(--color-risk-medium);">🤔 <strong>SUSPICIOUS:</strong> Proceed with caution. Verify the sender's identity before taking any requested actions.</span>`;
            } else {
                riskRecommendation.innerHTML = `<span style="color: var(--color-risk-minimal);">✅ <strong>SAFE:</strong> No significant threats detected. It appears safe to interact with this email.</span>`;
            }
        }

        // Factor Waterfall
        factorWaterfall.innerHTML = '';
        if (data.factors.length === 0) {
            factorWaterfall.innerHTML = '<div class="text-muted">No risk factors triggered.</div>';
        } else {
            data.factors.forEach(f => {
                const bar = document.createElement('div');
                bar.className = 'factor-bar';

                const fill = document.createElement('div');
                fill.className = `factor-fill ${f.category}`;
                // relative width out of 100 max
                fill.style.width = `${f.contribution}%`;
                fill.textContent = `${f.name} (+${f.contribution})`;

                bar.appendChild(fill);
                factorWaterfall.appendChild(bar);
            });
        }

        // Evidence
        evidenceTableBody.innerHTML = '';
        if (data.evidence.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="3" class="text-muted">No evidence found</td>`;
            evidenceTableBody.appendChild(tr);
        } else {
            data.evidence.forEach(e => {
                let icon = 'ℹ️';
                if (e.severity === 'HIGH') icon = '🚨';
                else if (e.severity === 'MEDIUM') icon = '⚠️';
                else if (e.severity === 'CRITICAL') icon = '☠️';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 500;">${defang(e.evidence_type)}</td>
                    <td><span class="badge badge-${e.severity.toLowerCase()}">${icon} ${e.severity}</span></td>
                    <td>${defang(e.explanation)}</td>
                `;
                evidenceTableBody.appendChild(tr);
            });
        }

        // Intent Graph Cards
        intentGraphGrid.innerHTML = '';
        if (data.graph) {
            const formatValue = (val) => {
                if (typeof val === 'boolean') return val ? 'Yes' : 'No';
                if (Array.isArray(val)) return val.length > 0 ? val.join(', ') : 'None';
                if (val === null || val === '') return 'Unknown';
                return val.toString().replace(/_/g, ' ');
            };

            const importantKeys = ['urgency_level', 'tone', 'requested_actions', 'financial_request', 'suspicious_links_present'];

            importantKeys.forEach(key => {
                if (data.graph[key] !== undefined) {
                    const card = document.createElement('div');
                    card.className = 'intent-card';
                    card.innerHTML = `
                        <div class="intent-card-label">${key.replace(/_/g, ' ')}</div>
                        <div class="intent-card-value">${formatValue(data.graph[key])}</div>
                    `;
                    intentGraphGrid.appendChild(card);
                }
            });

            // Add any remaining keys
            Object.keys(data.graph).forEach(key => {
                if (!importantKeys.includes(key) && typeof data.graph[key] !== 'object') {
                    const card = document.createElement('div');
                    card.className = 'intent-card';
                    card.innerHTML = `
                        <div class="intent-card-label">${key.replace(/_/g, ' ')}</div>
                        <div class="intent-card-value">${formatValue(data.graph[key])}</div>
                    `;
                    intentGraphGrid.appendChild(card);
                }
            });
        } else {
            intentGraphGrid.innerHTML = '<div class="text-muted">No semantic intent extracted.</div>';
        }

        // Sanitized Email
        emailContent.innerHTML = `<strong>Sender:</strong> ${defang(data.record.sender)}<br>` +
            `<strong>Subject:</strong> ${defang(data.record.subject)}<br><br>` +
            `${defang(data.record.body_text)}`;
    }

    analyzeBtn.addEventListener('click', async () => {
        const content = emailInput.value.trim();
        if (!content) return;

        analyzeBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        errorMsg.classList.add('hidden');
        if (riskRecommendation) {
            riskRecommendation.classList.add('hidden');
        }

        // Reset donut state
        if (riskDonutFill) {
            riskDonutFill.style.strokeDashoffset = 339.292;
        }

        resultsCard.classList.add('hidden');
        emailViewCard.classList.add('hidden');

        try {
            const result = await analyzeEmail(content);
            renderResults(result);
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        } finally {
            analyzeBtn.disabled = false;
            loadingIndicator.classList.add('hidden');
        }
    });

    // Tab Navigation
    const tabs = ['Overview', 'Analyze', 'Batch', 'Evaluation', 'Robustness', 'Methodology', 'Settings'];

    function switchTab(tabId) {
        tabs.forEach(t => {
            const nav = document.getElementById(`nav${t}`);
            const view = document.getElementById(`view${t}`);
            if (t.toLowerCase() === tabId.toLowerCase()) {
                nav.classList.add('active');
                nav.style.color = 'var(--color-text-inverse)';
                nav.style.fontWeight = 'bold';
                view.classList.remove('hidden');
            } else {
                nav.classList.remove('active');
                nav.style.color = 'rgba(255,255,255,0.7)';
                nav.style.fontWeight = 'normal';
                view.classList.add('hidden');
            }
        });
    }

    tabs.forEach(t => {
        document.getElementById(`nav${t}`).addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(t);
        });
    });

    // Batch Processing
    const batchFileInput = document.getElementById('batchFileInput');
    const batchProcessBtn = document.getElementById('batchProcessBtn');
    const batchLoadingIndicator = document.getElementById('batchLoadingIndicator');
    const batchProgress = document.getElementById('batchProgress');
    const batchError = document.getElementById('batchError');
    const batchResultsCard = document.getElementById('batchResultsCard');
    const batchTableBody = document.getElementById('batchTableBody');
    const exportBatchBtn = document.getElementById('exportBatchBtn');
    let lastBatchResults = [];

    batchProcessBtn.addEventListener('click', async () => {
        const file = batchFileInput.files[0];
        if (!file) {
            batchError.textContent = "Please select an .mbox file.";
            batchError.classList.remove('hidden');
            return;
        }

        batchProcessBtn.disabled = true;
        batchLoadingIndicator.classList.remove('hidden');
        batchProgress.classList.remove('hidden');
        batchError.classList.add('hidden');
        batchResultsCard.classList.add('hidden');

        try {
            const text = await file.text();
            const data = await processBatch(text);
            lastBatchResults = data.results;

            batchTableBody.innerHTML = '';
            lastBatchResults.forEach(res => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${defang(res.subject)}</td>
                    <td>${defang(res.sender)}</td>
                    <td>${res.score}</td>
                    <td><span class="badge badge-${res.level.toLowerCase()}">${res.level}</span></td>
                `;
                batchTableBody.appendChild(tr);
            });
            batchResultsCard.classList.remove('hidden');
        } catch (err) {
            batchError.textContent = err.message;
            batchError.classList.remove('hidden');
        } finally {
            batchProcessBtn.disabled = false;
            batchLoadingIndicator.classList.add('hidden');
            batchProgress.classList.add('hidden');
        }
    });

    exportBatchBtn.addEventListener('click', () => {
        if (!lastBatchResults || lastBatchResults.length === 0) return;
        const blob = new Blob([JSON.stringify(lastBatchResults, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "batch_results.json";
        a.click();
        URL.revokeObjectURL(url);
    });

    // Load Evaluation

    const loadEvalBtn = document.getElementById('loadEvalBtn');
    const evalError = document.getElementById('evalError');
    const evalContent = document.getElementById('evalContent');
    const evalTableBody = document.getElementById('evalTableBody');
    const mcnemarResult = document.getElementById('mcnemarResult');

    loadEvalBtn.addEventListener('click', async () => {
        evalError.classList.add('hidden');
        evalContent.classList.add('hidden');
        loadEvalBtn.textContent = 'Loading...';
        loadEvalBtn.disabled = true;

        try {
            const data = await fetchEvaluationSummary();
            renderEvaluation(data);
        } catch (err) {
            evalError.textContent = err.message;
            evalError.classList.remove('hidden');
        } finally {
            loadEvalBtn.textContent = 'Load results/summary.json';
            loadEvalBtn.disabled = false;
        }
    });

    function renderEvaluation(data) {
        evalTableBody.innerHTML = '';

        const formatCI = (mean, lower, upper) => {
            if (mean === undefined) return '-';
            return `${mean.toFixed(4)} <span class="text-muted" style="font-size: 0.75rem;">[${lower.toFixed(4)}, ${upper.toFixed(4)}]</span>`;
        };

        ['baseline', 'evidence_only', 'graph_only', 'full_pipeline'].forEach(ablation => {
            if (!data[ablation]) return;
            const res = data[ablation];
            const ci = res.confidence_intervals || {};

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${ablation}</strong></td>
                <td>${formatCI(res.f1, ci.f1?.ci_lower, ci.f1?.ci_upper)}</td>
                <td>${formatCI(res.roc_auc, ci.roc_auc?.ci_lower, ci.roc_auc?.ci_upper)}</td>
                <td>${res.ece ? res.ece.toFixed(4) : '-'}</td>
            `;
            evalTableBody.appendChild(tr);
        });

        if (data.mcnemar_baseline_vs_full !== undefined) {
            const p = data.mcnemar_baseline_vs_full;
            mcnemarResult.innerHTML = `p-value = ${p.toFixed(5)} ${p < 0.05 ? '<span class="badge badge-high">Significant</span>' : '<span class="badge badge-minimal">Not Significant</span>'}`;
        } else {
            mcnemarResult.textContent = 'N/A';
        }

        evalContent.classList.remove('hidden');
    }

    // Robustness
    const loadRobustnessBtn = document.getElementById('loadRobustnessBtn');
    const robustnessTable = document.getElementById('robustnessTable');
    const robustnessTableBody = document.getElementById('robustnessTableBody');

    loadRobustnessBtn.addEventListener('click', async () => {
        loadRobustnessBtn.textContent = 'Loading...';
        loadRobustnessBtn.disabled = true;
        robustnessTable.classList.add('hidden');

        try {
            const data = await fetchRobustnessSummary();
            robustnessTableBody.innerHTML = '';

            if (data.attacks) {
                for (const [strategy, res] of Object.entries(data.attacks)) {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${strategy}</strong></td>
                        <td>${res.metrics.f1 ? res.metrics.f1.toFixed(4) : '-'}</td>
                        <td style="color: var(--color-risk-high);">${res.degradation.recall_drop ? (res.degradation.recall_drop * 100).toFixed(2) + '%' : '-'}</td>
                    `;
                    robustnessTableBody.appendChild(tr);
                }
            }
            robustnessTable.classList.remove('hidden');
        } catch (err) {
            alert(err.message);
        } finally {
            loadRobustnessBtn.textContent = 'Load Robustness Results';
            loadRobustnessBtn.disabled = false;
        }
    });

});
