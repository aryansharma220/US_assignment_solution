// ============================================
// PRODUCTS PAGE JAVASCRIPT
// ============================================

(function() {
    'use strict';
    
    // Use utilities from main.js (window.AppUtils)
    const { $, $$, fetchAPI, formatCurrency, formatStars, showNotification, showLoading, showError } = window.AppUtils;

    let allProducts = [];
    let filteredProducts = [];
    let currentPage = 1;
    let productsPerPage = 12;
let categories = [];

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadProducts();
    setupEventListeners();
    setupModal();
});

// Load products
async function loadProducts() {
    const loading = $('#loadingProducts');
    loading.style.display = 'block';
    
    try {
        const data = await fetchAPI('/api/products?per_page=100');
        
        if (data.status === 'success') {
            allProducts = data.data;
            filteredProducts = [...allProducts];
            
            // Extract unique categories
            categories = [...new Set(allProducts.map(p => p.category))].sort();
            populateCategoryFilter();
            
            displayProducts();
        }
    } catch (error) {
        showError($('#productsGrid'), 'Failed to load products');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

// Populate category filter
function populateCategoryFilter() {
    const filter = $('#categoryFilter');
    filter.innerHTML = '<option value="">All Categories</option>' +
        categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
}

// Setup event listeners
function setupEventListeners() {
    $('#categoryFilter').addEventListener('change', filterProducts);
    $('#sortSelect').addEventListener('change', sortProducts);
    $('#searchInput').addEventListener('input', window.AppUtils.debounce(searchProducts, 300));
}

// Filter products by category
function filterProducts() {
    const category = $('#categoryFilter').value;
    const searchTerm = $('#searchInput').value.toLowerCase();
    
    filteredProducts = allProducts.filter(product => {
        const matchesCategory = !category || product.category === category;
        const matchesSearch = !searchTerm || 
            product.name.toLowerCase().includes(searchTerm) ||
            product.brand.toLowerCase().includes(searchTerm) ||
            product.description.toLowerCase().includes(searchTerm);
        
        return matchesCategory && matchesSearch;
    });
    
    currentPage = 1;
    sortProducts();
}

// Sort products
function sortProducts() {
    const sortBy = $('#sortSelect').value;
    
    switch (sortBy) {
        case 'name':
            filteredProducts.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'price-asc':
            filteredProducts.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            filteredProducts.sort((a, b) => b.price - a.price);
            break;
        case 'rating':
            filteredProducts.sort((a, b) => b.average_rating - a.average_rating);
            break;
    }
    
    displayProducts();
}

// Search products
function searchProducts() {
    filterProducts();
}

// Display products
function displayProducts() {
    const grid = $('#productsGrid');
    
    if (filteredProducts.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No Products Found</h3>
                <p>Try adjusting your filters or search term.</p>
            </div>
        `;
        $('#pagination').innerHTML = '';
        return;
    }
    
    // Calculate pagination
    const totalPages = Math.ceil(filteredProducts.length / productsPerPage);
    const startIndex = (currentPage - 1) * productsPerPage;
    const endIndex = startIndex + productsPerPage;
    const productsToShow = filteredProducts.slice(startIndex, endIndex);
    
    // Display products
    grid.innerHTML = productsToShow.map(product => createProductCard(product)).join('');
    
    // Display pagination
    displayPagination(totalPages);
    
    // Add click listeners
    $$('.product-card').forEach(card => {
        card.addEventListener('click', () => {
            const productId = card.dataset.productId;
            showProductDetail(productId);
        });
    });
}

// Create product card
function createProductCard(product) {
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
    const onSale = product.original_price && product.original_price > product.price;
    
    return `
        <div class="product-card" data-product-id="${product.id}">
            ${onSale ? '<div class="sale-badge">SALE</div>' : ''}
            <div class="product-image">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="product-content">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-brand">${product.brand}</div>
                <div class="product-rating">
                    <div class="rating-stars">${formatStars(product.average_rating)}</div>
                    <span>${product.average_rating.toFixed(1)}</span>
                </div>
                <div class="product-price-section">
                    <div class="product-price">${formatCurrency(product.price)}</div>
                    ${onSale ? `<div class="product-original-price">${formatCurrency(product.original_price)}</div>` : ''}
                </div>
                ${product.stock_quantity < 10 && product.stock_quantity > 0 ? 
                    `<div class="stock-warning">Only ${product.stock_quantity} left!</div>` : ''}
                ${product.stock_quantity === 0 ? '<div class="out-of-stock">Out of Stock</div>' : ''}
            </div>
        </div>
    `;
}

// Display pagination
function displayPagination(totalPages) {
    const pagination = $('#pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `
        <button class="pagination-btn ${currentPage === 1 ? 'disabled' : ''}" 
                onclick="changePage(${currentPage - 1})"
                ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i> Previous
        </button>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `
                <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                        onclick="changePage(${i})">
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span class="pagination-ellipsis">...</span>';
        }
    }
    
    // Next button
    html += `
        <button class="pagination-btn ${currentPage === totalPages ? 'disabled' : ''}"
                onclick="changePage(${currentPage + 1})"
                ${currentPage === totalPages ? 'disabled' : ''}>
            Next <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    pagination.innerHTML = html;
}

// Change page
window.changePage = function(page) {
    currentPage = page;
    displayProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

// Show product detail in modal
async function showProductDetail(productId) {
    const modal = $('#productModal');
    const detail = $('#productDetail');
    
    modal.style.display = 'block';
    detail.innerHTML = '<div class="spinner"></div>';
    
    try {
        const data = await fetchAPI(`/api/products/${productId}`);
        
        if (data.status === 'success') {
            const product = data.data;
            detail.innerHTML = createProductDetail(product);
        }
    } catch (error) {
        detail.innerHTML = '<p class="error-text">Failed to load product details</p>';
        console.error(error);
    }
}

// Create product detail HTML
function createProductDetail(product) {
    const onSale = product.original_price && product.original_price > product.price;
    const discount = onSale ? Math.round((1 - product.price / product.original_price) * 100) : 0;
    
    return `
        <div class="product-detail-container">
            <div class="product-detail-header">
                <h2>${product.name}</h2>
                <div class="product-detail-category">${product.category} • ${product.brand}</div>
            </div>
            
            <div class="product-detail-content">
                <div class="product-detail-info">
                    <div class="detail-section">
                        <h3>Price</h3>
                        <div class="price-large">${formatCurrency(product.price)}</div>
                        ${onSale ? `
                            <div class="original-price-large">${formatCurrency(product.original_price)}</div>
                            <div class="discount-badge">Save ${discount}%</div>
                        ` : ''}
                    </div>
                    
                    <div class="detail-section">
                        <h3>Rating</h3>
                        <div class="rating-large">
                            ${formatStars(product.average_rating)}
                            <span>${product.average_rating.toFixed(1)} out of 5</span>
                        </div>
                        <div class="review-count">${product.review_count} reviews</div>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Description</h3>
                        <p>${product.description}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Details</h3>
                        <ul class="detail-list">
                            ${product.color ? `<li><strong>Color:</strong> ${product.color}</li>` : ''}
                            ${product.size ? `<li><strong>Size:</strong> ${product.size}</li>` : ''}
                            ${product.material ? `<li><strong>Material:</strong> ${product.material}</li>` : ''}
                            <li><strong>Stock:</strong> ${product.stock_quantity} available</li>
                            <li><strong>Subcategory:</strong> ${product.subcategory}</li>
                        </ul>
                    </div>
                    
                    ${product.features ? `
                        <div class="detail-section">
                            <h3>Features</h3>
                            <p>${product.features}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Setup modal
function setupModal() {
    const modal = $('#productModal');
    const closeBtn = $('.modal-close');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

})(); // End of IIFE
