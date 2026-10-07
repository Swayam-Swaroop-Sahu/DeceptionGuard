import { analyzeEmail } from './api.js';

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
});
