/** API interactions */

export async function analyzeEmail(content) {
    const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
        let errorMsg = 'Analysis failed';
        try {
            const errData = await response.json();
            errorMsg = errData.error || errorMsg;
        } catch (e) {
            errorMsg = `${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
    }
    
    return await response.json();
}

export async function fetchEvaluationSummary() {
    const response = await fetch('/api/v1/results/summary.json', {
        method: 'GET',
    });
    
    if (!response.ok) {
        throw new Error('Could not fetch summary.json (Ensure `dg evaluate --suite full` was run)');
    }
    
    return await response.json();
}

export async function processBatch(fileData) {
    const response = await fetch('/api/v1/batch', {
        method: 'POST',
        body: fileData
    });
    
    if (!response.ok) {
        let errorMsg = 'Batch processing failed';
        try {
            const errData = await response.json();
            errorMsg = errData.error || errorMsg;
        } catch (e) {
            errorMsg = `${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
    }
    
    return await response.json();
}

export async function fetchRobustnessSummary() {
    const response = await fetch('/api/v1/results/adversarial_robustness.json', {
        method: 'GET',
    });
    
    if (!response.ok) {
        throw new Error('Could not fetch adversarial_robustness.json');
    }
    
    return await response.json();
}
