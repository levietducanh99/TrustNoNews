// Shared utility functions
const API_BASE_URL = 'http://localhost:8000';

function showLoading(loadingElement) {
    loadingElement.classList.remove('hidden');
}

function hideLoading(loadingElement) {
    loadingElement.classList.add('hidden');
}

function showError(errorElement, message) {
    errorElement.textContent = message || 'Something went wrong';
    errorElement.classList.remove('hidden');
}

function hideError(errorElement) {
    errorElement.classList.add('hidden');
}

function showResult(resultElement) {
    resultElement.classList.remove('hidden');
}

function hideResult(resultElement) {
    resultElement.classList.add('hidden');
}

async function makeApiCall(endpoint, url) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }) // Ensure the payload matches the API's expected format
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'API error'); // Adjust error handling for FastAPI responses
        }
        return data;
    } catch (err) {
        throw err;
    }
}
