import { analyzeEmail, fetchEvaluationSummary } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emailInput = document.getElementById('emailInput');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMsg = document.getElementById('errorMsg');
    
    const resultsCard = document.getElementById('resultsCard');
    const emailViewCard = document.getElementById('emailViewCard');
    
    const riskScore = document.getElementById('riskScore');
    const riskBadge = document.getElementById('riskBadge');
    const factorWaterfall = document.getElementById('factorWaterfall');
    const evidenceTableBody = document.getElementById('evidenceTableBody');
    const intentGraphJson = document.getElementById('intentGraphJson');
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
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${defang(e.evidence_type)}</td>
                    <td><span class="badge badge-${e.severity.toLowerCase()}">${e.severity}</span></td>
                    <td>${defang(e.explanation)}</td>
                `;
                evidenceTableBody.appendChild(tr);
            });
        }

        // Intent Graph
        intentGraphJson.textContent = JSON.stringify(data.graph, null, 2);

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
    
    // Evaluation Tab Navigation
    const navAnalyze = document.getElementById('navAnalyze');
    const navEvaluation = document.getElementById('navEvaluation');
    const viewAnalyze = document.getElementById('viewAnalyze');
    const viewEvaluation = document.getElementById('viewEvaluation');
    
    function switchTab(tab) {
        if (tab === 'analyze') {
            navAnalyze.classList.add('active');
            navAnalyze.style.color = 'var(--color-text-inverse)';
            navAnalyze.style.fontWeight = 'bold';
            
            navEvaluation.classList.remove('active');
            navEvaluation.style.color = 'rgba(255,255,255,0.7)';
            navEvaluation.style.fontWeight = 'normal';
            
            viewAnalyze.classList.remove('hidden');
            viewEvaluation.classList.add('hidden');
        } else {
            navEvaluation.classList.add('active');
            navEvaluation.style.color = 'var(--color-text-inverse)';
            navEvaluation.style.fontWeight = 'bold';
            
            navAnalyze.classList.remove('active');
            navAnalyze.style.color = 'rgba(255,255,255,0.7)';
            navAnalyze.style.fontWeight = 'normal';
            
            viewEvaluation.classList.remove('hidden');
            viewAnalyze.classList.add('hidden');
        }
    }
    
    navAnalyze.addEventListener('click', (e) => { e.preventDefault(); switchTab('analyze'); });
    navEvaluation.addEventListener('click', (e) => { e.preventDefault(); switchTab('evaluation'); });

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
});
