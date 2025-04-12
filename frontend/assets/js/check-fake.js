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

            result.innerHTML = `
        <div class="result-card" role="region" aria-live="polite">
          <div class="accordion-container" role="tablist" aria-orientation="horizontal">
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="true" aria-controls="fake-status" role="tab">
                <h3 class="flex items-center">
                  <span class="mr-2">${
                data.is_fake
                    ? '<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
                    : '<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
            }</span>
                  Status
                </h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="fake-status" class="accordion-content" aria-expanded="true">
                <div class="status-indicator ${
                data.is_fake ? 'status-danger' : 'status-safe'
            }">
                  ${data.is_fake ? 'Potential Misinformation' : 'Likely Authentic'}
                </div>
              </div>
            </div>
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="false" aria-controls="fake-articles" role="tab">
                <h3>Articles</h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="fake-articles" class="accordion-content scrollable-content" aria-expanded="false">
                <div class="space-y-2">
                  <p><strong>Title:</strong> <span class="text-gray-800">${
                data.input_title || 'N/A'
            }</span></p>
                  <p><strong>Similar Articles:</strong></p>
                  <ul class="list-disc pl-6">
                    ${
                data.similar_titles?.length
                    ? data.similar_titles
                        .map(
                            (title, i) => `
                            <li class="flex flex-col mb-2">
                              <div class="flex justify-between">
                                <a href="${data.urls[i]}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">
                                  ${title}
                                </a>
                                <span class="text-gray-600">${
                                  data.similarity_scores[i]
                                      ? `${(data.similarity_scores[i] * 100).toFixed(0)}% match`
                                      : 'N/A'
                                }</span>
                              </div>
                              <span class="text-xs text-gray-500 truncate">${data.urls[i] || ''}</span>
                            </li>
                          `
                        )
                        .join('')
                    : '<li>No similar articles found.</li>'
            }
                  </ul>
                </div>
              </div>
            </div>
            <div class="accordion" role="tabpanel">
              <button class="accordion-header" type="button" aria-expanded="false" aria-controls="fake-explanation" role="tab">
                <h3>Explanation</h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="fake-explanation" class="accordion-content scrollable-content" aria-expanded="false">
                <p>${data.explanation || 'No additional information available.'}</p>
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
