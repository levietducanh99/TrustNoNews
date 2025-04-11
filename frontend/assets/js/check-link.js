document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('link-form');
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
            const data = await makeApiCall('/check-link', url);

            document.getElementById('is-suspicious').textContent = data.is_suspicious ? 'Yes' : 'No';
            document.getElementById('is-suspicious').classList.add(data.is_suspicious ? 'text-red-600' : 'text-green-600');
            document.getElementById('redirected-url').textContent = data.redirected_url || 'N/A';
            document.getElementById('reason').textContent = data.reason?.trim() || 'N/A';
            document.getElementById('explanation').textContent = data.explanation?.trim() || 'N/A';

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});
