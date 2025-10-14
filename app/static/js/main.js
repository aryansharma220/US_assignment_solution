// ============================================
// MAIN JAVASCRIPT FILE
// ============================================

// Utility Functions
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// API Base URL
const API_BASE = window.location.origin;

// Fetch wrapper with error handling
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format rating stars
function formatStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let stars = '';
    stars += '<i class="fas fa-star"></i>'.repeat(fullStars);
    if (hasHalfStar) stars += '<i class="fas fa-star-half-alt"></i>';
    stars += '<i class="far fa-star"></i>'.repeat(emptyStars);
    
    return stars;
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Loading spinner
function showLoading(element) {
    element.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
    `;
}

// Error message
function showError(element, message) {
    element.innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Oops!</h3>
            <p>${message}</p>
        </div>
    `;
}

// Empty state
function showEmpty(element, message, icon = 'box-open') {
    element.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-${icon}"></i>
            <h3>Nothing Here</h3>
            <p>${message}</p>
        </div>
    `;
}

// Smooth scroll
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Initialize tooltips (if any)
function initTooltips() {
    const tooltips = $$('[data-tooltip]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = el.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = el.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
        });
        
        el.addEventListener('mouseleave', () => {
            const tooltip = $('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

// Export functions
window.AppUtils = {
    $,
    $$,
    fetchAPI,
    formatCurrency,
    formatStars,
    showNotification,
    debounce,
    showLoading,
    showError,
    showEmpty,
    smoothScroll,
    initTooltips
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Smart Recommender Initialized');
    initTooltips();
});
