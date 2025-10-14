// ============================================
// RECOMMENDATIONS PAGE JAVASCRIPT
// ============================================

(function() {
    'use strict';
    
    // Use utilities from main.js (window.AppUtils)
    const { $, $$, fetchAPI, formatCurrency, formatStars, showNotification, showLoading, showError } = window.AppUtils;

    let currentUser = null;
    let allUsers = [];

    // Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadUsers();
    setupEventListeners();
});

// Load users
async function loadUsers() {
    try {
        const data = await fetchAPI('/api/users?per_page=50');
        
        if (data.status === 'success') {
            allUsers = data.data;
            populateUserSelect();
        }
    } catch (error) {
        showNotification('Failed to load users', 'error');
        console.error(error);
    }
}

// Populate user select dropdown
function populateUserSelect() {
    const select = $('#userSelect');
    
    if (allUsers.length === 0) {
        select.innerHTML = '<option value="">No users found</option>';
        return;
    }
    
    select.innerHTML = '<option value="">Select a user...</option>' +
        allUsers.map(user => {
            // Use display_name for user-friendly display, fallback to full_name or username
            const displayName = user.display_name || user.full_name || user.username;
            return `<option value="${user.id}">${displayName} (${user.total_purchases} purchases)</option>`;
        }).join('');
}

// Setup event listeners
function setupEventListeners() {
    const getRecsBtn = $('#getRecommendations');
    const userSelect = $('#userSelect');
    
    getRecsBtn.addEventListener('click', handleGetRecommendations);
    
    userSelect.addEventListener('change', (e) => {
        if (e.target.value) {
            getRecsBtn.disabled = false;
        } else {
            getRecsBtn.disabled = true;
        }
    });
}

// Handle get recommendations
async function handleGetRecommendations() {
    const userId = parseInt($('#userSelect').value);
    const strategy = $('#strategySelect').value;
    const limit = parseInt($('#limitSelect').value);
    
    if (!userId) {
        showNotification('👤 Please select a user first!', 'error');
        return;
    }
    
    // Show loading with helpful message
    showLoadingState();
    hideUserInfo();
    hideError();
    
    showNotification('🔍 Analyzing preferences and generating recommendations...', 'info');
    
    try {
        const data = await fetchAPI(
            `/api/recommend/${userId}?limit=${limit}&strategy=${strategy}&explain=true`
        );
        
        if (data.status === 'success') {
            currentUser = data.data.user;
            displayUserInfo(data.data);
            displayRecommendations(data.data);
            hideLoading();
            
            // Success notification
            showNotification(`✨ Found ${data.data.count} perfect matches for ${data.data.user.username}!`, 'success');
        } else {
            throw new Error(data.message || 'Failed to get recommendations');
        }
    } catch (error) {
        hideLoading();
        displayError(error.message);
        showNotification('❌ Oops! Something went wrong. Please try again.', 'error');
    }
}

// Display user info
function displayUserInfo(data) {
    const userInfo = $('#userInfo');
    const userName = $('#userName');
    const userPurchases = $('#userPurchases');
    const userPreferences = $('#userPreferences');
    const strategyUsed = $('#strategyUsed');
    
    userName.textContent = data.user.username;
    userPurchases.textContent = data.user.total_purchases;
    userPreferences.textContent = 'View Profile';
    strategyUsed.textContent = data.strategy_used.charAt(0).toUpperCase() + data.strategy_used.slice(1);
    
    userInfo.style.display = 'flex';
}

// Display recommendations
function displayRecommendations(data) {
    const grid = $('#recommendationsGrid');
    
    if (!data.recommendations || data.recommendations.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>No Recommendations Available</h3>
                <p>Try interacting with more products or selecting a different strategy.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = data.recommendations.map((rec, index) => 
        createRecommendationCard(rec, index + 1)
    ).join('');
    
    // Add event listeners to similar product buttons
    $$('.btn-similar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const productId = e.currentTarget.dataset.productId;
            showSimilarProducts(productId);
        });
    });
}

// Create recommendation card HTML
function createRecommendationCard(rec, rank) {
    const product = rec.product;
    const reason = rec.recommendation_reason;
    
    // Determine icon based on category
    const categoryIcons = {
        'Electronics': 'laptop',
        'Fashion': 'tshirt',
        'Home & Kitchen': 'home',
        'Sports': 'dumbbell',
        'Books': 'book',
        'Beauty': 'spa',
        'Toys': 'gamepad',
        'Grocery': 'shopping-basket'
    };
    
    const icon = categoryIcons[product.category] || 'box';
    
    // Build reason tags
    let reasonTags = '';
    if (reason.type === 'collaborative' && reason.recommenders_count) {
        reasonTags += `<span class="reason-tag"><i class="fas fa-users"></i> ${reason.recommenders_count} similar users</span>`;
    }
    if (reason.matched_category) {
        reasonTags += `<span class="reason-tag"><i class="fas fa-tag"></i> Matches your interests</span>`;
    }
    if (reason.matched_brand) {
        reasonTags += `<span class="reason-tag"><i class="fas fa-award"></i> Favorite brand</span>`;
    }
    
    return `
        <div class="recommendation-card">
            <div class="recommendation-badge">
                <i class="fas fa-trophy"></i>
                #${rank} Match
            </div>
            <div class="product-image-container">
                <div class="product-image-placeholder">
                    <i class="fas fa-${icon}"></i>
                </div>
            </div>
            <div class="product-details">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-brand">
                    <i class="fas fa-tag"></i>
                    ${product.brand}
                </div>
                
                <div class="product-info">
                    <div class="product-price">${formatCurrency(product.price)}</div>
                    <div class="product-rating">
                        <div class="rating-stars">${formatStars(product.average_rating)}</div>
                        <span class="rating-value">${product.average_rating.toFixed(1)}</span>
                    </div>
                </div>
                
                <div class="product-meta">
                    <span><i class="fas fa-chart-line"></i> ${rec.score}% match</span>
                    <span><i class="fas fa-star"></i> ${product.review_count} reviews</span>
                </div>
                
                ${reasonTags ? `<div class="recommendation-reason">${reasonTags}</div>` : ''}
                
                <div class="explanation-section">
                    <div class="explanation-title">
                        <i class="fas fa-lightbulb"></i>
                        Why we recommend this
                    </div>
                    <div class="explanation-text">${rec.explanation}</div>
                </div>
                
                <div class="product-actions">
                    <button class="btn btn-primary">
                        <i class="fas fa-shopping-cart"></i> View Details
                    </button>
                    <button class="btn btn-similar" data-product-id="${product.id}">
                        <i class="fas fa-search"></i> Similar
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Show similar products (opens in modal or navigates)
function showSimilarProducts(productId) {
    showNotification(`Finding similar products to #${productId}...`, 'info');
    // TODO: Implement similar products modal
}

// UI State Management
function showLoadingState() {
    const loading = $('#loadingState');
    loading.style.display = 'block';
    $('#recommendationsGrid').innerHTML = '';
    
    // Update loading text with helpful message
    const loadingText = loading.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = 'Analyzing user preferences and finding perfect matches...';
    }
}

function hideLoading() {
    $('#loadingState').style.display = 'none';
}

function hideUserInfo() {
    $('#userInfo').style.display = 'none';
}

function displayError(message) {
    const errorState = $('#errorState');
    const errorMsg = $('#errorMessage');
    errorMsg.textContent = message || 'Something went wrong. Please try again.';
    errorState.style.display = 'block';
    
    // Add helpful suggestion
    const suggestionText = document.createElement('p');
    suggestionText.style.marginTop = '1rem';
    suggestionText.style.color = 'var(--text-secondary)';
    suggestionText.innerHTML = '<i class="fas fa-info-circle"></i> Try selecting a different user or strategy';
    if (!errorState.querySelector('p:last-child')?.textContent.includes('Try selecting')) {
        errorState.querySelector('.error-content')?.appendChild(suggestionText);
    }
}

function hideError() {
    $('#errorState').style.display = 'none';
}

})(); // End of IIFE
