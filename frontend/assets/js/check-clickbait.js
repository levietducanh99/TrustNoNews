document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('clickbait-form');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('url').value;

        showLoading(loading);
        hideResult(result);
        hideError(error);

        try {
            const data = await makeApiCall('/check-clickbait', url);

            document.getElementById('is-clickbait').textContent = data.is_clickbait ? 'Yes' : 'No';
            document.getElementById('is-clickbait').classList.add(data.is_clickbait ? 'text-red-600' : 'text-green-600');
            document.getElementById('title').textContent = data.title || 'N/A';
            document.getElementById('summary').textContent = data.summary || 'N/A';
            document.getElementById('similarity-score').textContent = 
                data.similarity_score ? data.similarity_score.toFixed(2) : 'N/A';
            document.getElementById('explanation').textContent = data.explanation || 'N/A';

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});
