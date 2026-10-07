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
