document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('pipeline-form');
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
            const data = await makeApiCall('/analyze', url); // Use analyze API
            const results = data;

            // Summary
            document.getElementById('summary-url').textContent = results.url;
            let issues = [];
            if (results.link_check.is_suspicious) issues.push('Suspicious Link');
            if (results.clickbait.is_clickbait) issues.push('Clickbait');
            if (results.sensitive_language.detected) issues.push('Sensitive Language');
            if (results.fake_news.is_fake) issues.push('Fake News');
            
            // Update trust level display
            document.getElementById('trust-level').textContent = 
                issues.length > 0 ? `High Risk (${issues.join(', ')})` : 'Low Risk';
            document.getElementById('trust-level').classList.add(
                issues.length > 0 ? 'text-red-600' : 'text-green-600'
            );

            // Link Check
            document.getElementById('link-suspicious').textContent = 
                results.link_check.is_suspicious ? 'Yes' : 'No';
            document.getElementById('link-suspicious').classList.add(
                results.link_check.is_suspicious ? 'text-red-600' : 'text-green-600'
            );
            document.getElementById('link-redirected').textContent = 
                results.link_check.redirected_url || 'N/A';
            document.getElementById('link-explanation').textContent = 
                results.link_check.explanation?.trim() || 'N/A';

            // Clickbait Check
            document.getElementById('clickbait-is').textContent = results.clickbait.is_clickbait ? 'Yes' : 'No';
            document.getElementById('clickbait-is').classList.add(results.clickbait.is_clickbait ? 'text-red-600' : 'text-green-600');
            document.getElementById('clickbait-title').textContent = results.clickbait.title || 'N/A';
            document.getElementById('clickbait-explanation').textContent = results.clickbait.explanation || 'N/A';

            // Sensitive Language Check
            document.getElementById('sensitive-is').textContent = 
                results.sensitive_language.detected ? 'Yes' : 'No';
            document.getElementById('sensitive-is').classList.add(
                results.sensitive_language.detected ? 'text-red-600' : 'text-green-600'
            );
            document.getElementById('sensitive-label').textContent = 
                results.sensitive_language.main_label || 
                results.sensitive_language.conclusion || 'N/A';
            document.getElementById('sensitive-explanation').textContent = 
                results.sensitive_language.explanation || 'N/A';

            // Fake News Check
            document.getElementById('fake-is').textContent = results.fake_news.is_fake ? 'Yes' : 'No';
            document.getElementById('fake-is').classList.add(results.fake_news.is_fake ? 'text-red-600' : 'text-green-600');
            document.getElementById('fake-title').textContent = results.fake_news.input_title || 'N/A';
            
            // Update similar titles display to match check-fake.html
            const similarTitles = document.getElementById('fake-similar');
            similarTitles.innerHTML = '';
            results.fake_news.similar_titles?.forEach((title, i) => {
                const li = document.createElement('li');
                const score = results.fake_news.similarity_scores[i]?.toFixed(2) || 'N/A';
                const articleUrl = results.fake_news.urls?.[i] || '#';
                
                li.innerHTML = `
                    <div class="mb-2">
                        <div>${title} (Score: ${score})</div>
                        <a href="${articleUrl}" target="_blank" class="text-blue-600 hover:underline text-sm">
                            ${articleUrl}
                        </a>
                    </div>
                `;
                similarTitles.appendChild(li);
            });
            
            // Update explanation to be in a styled div instead of a span
            document.getElementById('fake-explanation').textContent = results.fake_news.explanation || 'N/A';

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});
