document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fake-form');
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
            const data = await makeApiCall('/check-fake-news', url);

            document.getElementById('is-fake').textContent = data.is_fake ? 'Yes' : 'No';
            document.getElementById('is-fake').classList.add(data.is_fake ? 'text-red-600' : 'text-green-600');
            document.getElementById('input-title').textContent = data.input_title || 'N/A';
            const similarTitles = document.getElementById('similar-titles');
            similarTitles.innerHTML = '';
            data.similar_titles?.forEach((title, i) => {
                const li = document.createElement('li');
                li.textContent = `${title} (Score: ${data.similarity_scores[i]?.toFixed(2) || 'N/A'})`;
                similarTitles.appendChild(li);
            });
            document.getElementById('explanation').textContent = data.explanation || 'N/A';

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});