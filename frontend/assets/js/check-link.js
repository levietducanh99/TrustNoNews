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

            // Set basic information
            const statusElement = document.getElementById('is-suspicious');
            statusElement.textContent = data.is_suspicious ? 'Yes' : 'No';
            statusElement.className = data.is_suspicious ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold';
            
            // Update the redirected URL with proper styling
            const redirectedUrlElement = document.getElementById('redirected-url');
            redirectedUrlElement.textContent = data.redirected_url || 'N/A';
            redirectedUrlElement.className = 'break-all text-sm';
            
            document.getElementById('reason').textContent = data.reason?.trim() || 'N/A';
            document.getElementById('explanation').textContent = data.explanation?.trim() || 'N/A';

            // Compact view for non-suspicious links
            const resultContainer = document.getElementById('result');
            const resultGrid = document.getElementById('result-grid');
            
            if (!data.is_suspicious) {
                resultContainer.classList.add('compact-result');
                resultGrid.classList.remove('md:grid-cols-2');
                resultGrid.classList.add('md:grid-cols-1');
                document.getElementById('redirect-section').classList.add('hidden');
            } else {
                resultContainer.classList.remove('compact-result');
                resultGrid.classList.add('md:grid-cols-2');
                resultGrid.classList.remove('md:grid-cols-1');
                
                // Show redirect section only if there's redirect data and the link is suspicious
                if (data.redirect_chain && data.redirect_chain.length > 0) {
                    document.getElementById('redirect-section').classList.remove('hidden');
                } else {
                    document.getElementById('redirect-section').classList.add('hidden');
                }
            }

            // Handle redirect chain
            const redirectChainContainer = document.getElementById('redirect-chain');
            redirectChainContainer.innerHTML = '';
            
            if (data.redirect_chain && data.redirect_chain.length > 0 && data.is_suspicious) {
                // Create table header
                const table = document.createElement('table');
                table.className = 'min-w-full bg-white border border-gray-200';
                
                const thead = document.createElement('thead');
                thead.innerHTML = `
                    <tr class="bg-gray-100">
                        <th class="border px-4 py-2">Step</th>
                        <th class="border px-4 py-2">Type</th>
                        <th class="border px-4 py-2">URL</th>
                    </tr>
                `;
                table.appendChild(thead);
                
                const tbody = document.createElement('tbody');
                data.redirect_chain.forEach(redirect => {
                    const row = document.createElement('tr');
                    
                    // Step column
                    const stepCell = document.createElement('td');
                    stepCell.className = 'border px-4 py-2 text-center';
                    stepCell.textContent = redirect.step;
                    row.appendChild(stepCell);
                    
                    // Type column
                    const typeCell = document.createElement('td');
                    typeCell.className = 'border px-4 py-2';
                    typeCell.textContent = redirect.type;
                    row.appendChild(typeCell);
                    
                    // URL column
                    const urlCell = document.createElement('td');
                    urlCell.className = 'border px-4 py-2 break-all';
                    
                    const urlLink = document.createElement('a');
                    urlLink.href = redirect.url;
                    urlLink.textContent = redirect.url;
                    urlLink.className = 'text-blue-600 hover:underline';
                    urlLink.target = '_blank';
                    urlLink.rel = 'noopener noreferrer';
                    
                    urlCell.appendChild(urlLink);
                    row.appendChild(urlCell);
                    
                    tbody.appendChild(row);
                });
                
                table.appendChild(tbody);
                redirectChainContainer.appendChild(table);
            }

            hideLoading(loading);
            showResult(result);
        } catch (err) {
            hideLoading(loading);
            showError(error, err.message);
        }
    });
});
