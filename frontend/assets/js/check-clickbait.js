document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('clickbait-form');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('url').value;
        
        // Clear previous results
        result.innerHTML = '';
        result.classList.add('hidden');
        error.innerHTML = '';
        error.classList.add('hidden');
        loading.classList.remove('hidden');
        
        try {
            const response = await fetch('http://localhost:8000/api/check-clickbait', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred');
            }
            
            loading.classList.add('hidden');
            result.classList.remove('hidden');
            
            // Create result HTML
            let resultHTML = `
                <div class="result-card ${data.is_clickbait ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}">
                    <div class="flex items-start">
                        <div class="flex-shrink-0 mt-1">
                            <i class="fas ${data.is_clickbait ? 'fa-exclamation-circle text-red-500' : 'fa-check-circle text-green-500'} text-xl"></i>
                        </div>
                        <div class="ml-3 w-full">
                            <h3 class="text-lg font-semibold ${data.is_clickbait ? 'text-red-700' : 'text-green-700'}">
                                ${data.is_clickbait ? 'Clickbait Detected' : 'Not Clickbait'}
                            </h3>
                            <div class="mt-2 text-gray-600">
                                <p class="mb-2"><strong>Title:</strong> ${escapeHtml(data.title)}</p>
                                <div class="mb-4 p-3 bg-white rounded-lg">
                                    <p>${escapeHtml(data.explanation)}</p>
                                </div>
                            </div>

                            <!-- Model Prediction Details -->
                            <div class="mt-4">
                                <h4 class="text-md font-semibold mb-2">Model Prediction Details:</h4>
                                <div class="bg-white p-3 rounded-lg">
                                    <p><strong>Prediction:</strong> ${data.model_prediction.is_clickbait ? 'Clickbait' : 'Not Clickbait'}</p>
                                    <p><strong>Confidence:</strong> ${(data.model_prediction.probability * 100).toFixed(1)}%</p>
                                    ${data.model_prediction.clickbait_words.length > 0 ? 
                                        `<p><strong>Clickbait words detected:</strong> ${data.model_prediction.clickbait_words.join(', ')}</p>` : 
                                        '<p><strong>Clickbait words detected:</strong> None</p>'
                                    }
                                    <p><strong>Similarity score:</strong> ${(data.similarity_score * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                            
                            <!-- Accordion for additional details -->
                            <div class="mt-4">
                                <button class="accordion-button flex items-center justify-between w-full p-3 bg-gray-200 rounded-lg hover:bg-gray-300">
                                    <span class="font-medium">Content Summary</span>
                                    <i class="fas fa-chevron-down"></i>
                                </button>
                                <div class="accordion-content hidden p-3 bg-white rounded-lg mt-1">
                                    <div class="scrollable-content">
                                        ${escapeHtml(data.summary)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            result.innerHTML = resultHTML;
            
            // Set up accordion functionality
            const accordionButtons = document.querySelectorAll('.accordion-button');
            accordionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const content = this.nextElementSibling;
                    content.classList.toggle('hidden');
                    const icon = this.querySelector('i');
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                });
            });
            
        } catch (err) {
            loading.classList.add('hidden');
            error.classList.remove('hidden');
            error.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-red-500"></i>
                    </div>
                    <div class="ml-3">
                        <p class="font-medium">Error: ${escapeHtml(err.message)}</p>
                        <p class="mt-1">Please try again or check if the URL is valid and accessible.</p>
                    </div>
                </div>
            `;
        }
    });

    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
