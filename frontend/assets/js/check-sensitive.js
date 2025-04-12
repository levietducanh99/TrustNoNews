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

            // Unhide the result div after successful API response
            result.classList.remove('hidden');
            result.innerHTML = `
        <div class="result-card" role="region" aria-live="polite">
          <div class="accordion-container" role="tablist">
            <div class="accordion w-full" role="tabpanel">
              <button class="accordion-header w-full" type="button" aria-expanded="true" aria-controls="sensitive-status" role="tab">
                <h3 class="flex items-center">
                  <span class="mr-2">${
                data.detected
                    ? '<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
                    : '<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
            }</span>
                  Status
                </h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="sensitive-status" class="accordion-content" aria-expanded="true">
                <div class="status-indicator ${
                data.detected ? 'status-danger' : 'status-safe'
            }">
                  ${data.detected ? 'Sensitive Content Detected' : 'Content Appropriate'}
                </div>
                <div class="mt-2">
                  <p><strong>Label:</strong> <span class="text-gray-800">${
                data.main_label || data.conclusion || 'N/A'
            }</span></p>
                  <p><strong>Explanation:</strong> <span class="text-gray-800">${
                data.explanation || 'No explanation available'
            }</span></p>
                </div>
              </div>
            </div>
            
            <div class="accordion w-full" role="tabpanel">
              <button class="accordion-header w-full" type="button" aria-expanded="true" aria-controls="sensitive-criteria" role="tab">
                <h3>Criteria Analysis</h3>
                <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div id="sensitive-criteria" class="accordion-content" aria-expanded="true">
                <div class="overflow-x-auto">
                  <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead class="bg-gray-100">
                      <tr>
                        <th class="py-2 px-4 text-left border-b">Criteria</th>
                        <th class="py-2 px-4 text-left border-b">Description</th>
                        <th class="py-2 px-4 text-left border-b">Probability</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${data.criteria.map(item => `
                        <tr class="${item.probability > 0.5 ? 'bg-red-100' : 'bg-green-100'}">
                          <td class="py-2 px-4 border-b">${item.label}</td>
                          <td class="py-2 px-4 border-b">${item.description}</td>
                          <td class="py-2 px-4 border-b">${(item.probability * 100).toFixed(2)}%</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
            
            // Initialize accordions after content is added
            initAccordions();
            
        } catch (err) {
            showError(error, err.message || 'An error occurred');
        } finally {
            hideLoading(loading);
        }
    });

    function initAccordions() {
        const accordionHeaders = document.querySelectorAll('.accordion-header');
        
        accordionHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const content = this.nextElementSibling;
                const isExpanded = content.getAttribute('aria-expanded') === 'true';
                
                content.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
                
                // Update icon rotation
                const icon = this.querySelector('svg');
                if (icon) {
                    if (isExpanded) {
                        icon.classList.remove('rotate-180');
                    } else {
                        icon.classList.add('rotate-180');
                    }
                }
            });
        });
    }

    function showLoading(element) {
        element.classList.remove('hidden');
    }

    function hideLoading(element) {
        element.classList.add('hidden');
    }

    function hideResult(element) {
        element.classList.add('hidden');
    }

    function showError(element, message) {
        element.classList.remove('hidden');
        element.innerHTML = `<p>${message}</p>`;
    }

    function hideError(element) {
        element.classList.add('hidden');
    }
});
