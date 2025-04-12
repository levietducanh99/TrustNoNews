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

            result.innerHTML = `
        <div class="result-card" role="region" aria-live="polite">
          <div class="accordion-container" role="tablist" aria-orientation="horizontal">
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="true" aria-controls="link-status" role="tab">
                <h3 class="flex items-center">
                  <span class="mr-2">${
                data.is_suspicious
                    ? '<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
                    : '<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
            }</span>
                  Status
                </h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="link-status" class="accordion-content" aria-expanded="true">
                <div class="status-indicator ${
                data.is_suspicious ? 'status-danger' : 'status-safe'
            }">
                  ${data.is_suspicious ? 'Potentially Unsafe' : 'Safe Link'}
                </div>
              </div>
            </div>
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="false" aria-controls="link-details" role="tab">
                <h3>Details</h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="link-details" class="accordion-content scrollable-content" aria-expanded="false">
                <div class="space-y-2">
                  <p><strong>Redirected URL:</strong> <span class="text-gray-800">${
                data.redirected_url || 'N/A'
            }</span></p>
                  <p><strong>Reason:</strong> <span class="text-gray-800">${
                data.reason?.trim() || 'N/A'
            }</span></p>
                </div>
              </div>
            </div>
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="false" aria-controls="link-explanation" role="tab">
                <h3>Explanation</h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="link-explanation" class="accordion-content scrollable-content explanation" aria-expanded="false">
                <p>${data.explanation?.trim() || 'No additional information available.'}</p>
              </div>
            </div>
          </div>
        </div>
      `;

            setupAccordions(result);

            hideLoading(loading);
            showResult(result);
            result.scrollIntoView({ behavior: 'smooth', block: 'start' });
            result.querySelector('.accordion-header').focus();
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message || 'Failed to analyze the URL.');
        }
    });

    function setupAccordions(container) {
        const headers = container.querySelectorAll('.accordion-header');
        headers.forEach((header) => {
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                const isExpanded = content.getAttribute('aria-expanded') === 'true';
                content.setAttribute('aria-expanded', !isExpanded);
                header.setAttribute('aria-expanded', !isExpanded);
                header.querySelector('svg').classList.toggle('rotate-180');
            });
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    header.click();
                }
            });
        });
    }
});
