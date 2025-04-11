document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('sensitive-form');
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
            const data = await makeApiCall('/check-hatespeech', url);

            document.getElementById('is-sensitive').textContent = data.detected ? 'Yes' : 'No';
            document.getElementById('is-sensitive').classList.add(data.detected ? 'text-red-600' : 'text-green-600');
            document.getElementById('label').textContent = data.main_label || data.conclusion || 'N/A';
            document.getElementById('explanation').textContent = data.explanation || 'N/A';

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});
