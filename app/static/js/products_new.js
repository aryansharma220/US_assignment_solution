// ============================================
// PRODUCTS PAGE WITH ADVANCED FILTERS
// ============================================

(function() {
    'use strict';
    
    // Use utilities from main.js
    const { $, $$, fetchAPI, formatCurrency, formatStars, showNotification, showLoading, showError } = window.AppUtils;

    // State management
    let filterOptions = {
        brands: [],
        categories: [],
        priceRange: { min: 299, max: 89999 }
    };
    
    let activeFilters = {
        search: '',
        category: '',
        price_min: 299,
        price_max: 89999,
        brands: [],
        min_rating: null,
        in_stock: null,
        sort_by: 'newest'
    };
    
    let currentPage = 1;
    let productsPerPage = 12;
    let totalProducts = 0;

    // Initialize
    document.addEventListener('DOMContentLoaded', async () => {
        await loadFilterOptions();
        await loadProducts();
        setupEventListeners();
        setupModal();
    });

    // Load filter options from API
    async function loadFilterOptions() {
        try {
            const data = await fetchAPI('/api/products/filters');
            if (data.status === 'success') {
                filterOptions = data.data;
                populateBrandFilters();
                populateCategoryFilter();
                setupPriceSliders();
            }
        } catch (error) {
            console.error('Failed to load filter options:', error);
        }
    }

    // Populate brand filters
    function populateBrandFilters() {
        const container = $('#brandFilters');
        container.innerHTML = filterOptions.brands.map(brand => `
            <label class="checkbox-label">
                <input type="checkbox" value="${brand.name}" class="brand-checkbox">
                <span>${brand.name} <span class="count">(${brand.count})</span></span>
            </label>
        `).join('');

        // Add event listeners to brand checkboxes
        $$('.brand-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', handleBrandFilterChange);
        });
    }

    // Populate category filter
    function populateCategoryFilter() {
        const filter = $('#categoryFilter');
        filter.innerHTML = '<option value="">All Categories</option>' +
            filterOptions.categories.map(cat => 
                `<option value="${cat.name}">${cat.name} (${cat.count})</option>`
            ).join('');
    }

    // Setup price range sliders
    function setupPriceSliders() {
        const priceMin = $('#priceMin');
        const priceMax = $('#priceMax');
        const priceMinDisplay = $('#priceMinDisplay');
        const priceMaxDisplay = $('#priceMaxDisplay');

        priceMin.min = filterOptions.priceRange.min;
        priceMin.max = filterOptions.priceRange.max;
        priceMax.min = filterOptions.priceRange.min;
        priceMax.max = filterOptions.priceRange.max;
        
        priceMin.value = filterOptions.priceRange.min;
        priceMax.value = filterOptions.priceRange.max;

        function updatePriceDisplay() {
            let minVal = parseInt(priceMin.value);
            let maxVal = parseInt(priceMax.value);

            // Prevent overlap
            if (minVal > maxVal - 500) {
                minVal = maxVal - 500;
                priceMin.value = minVal;
            }

            activeFilters.price_min = minVal;
            activeFilters.price_max = maxVal;

            priceMinDisplay.textContent = formatCurrency(minVal);
            priceMaxDisplay.textContent = formatCurrency(maxVal);
        }

        priceMin.addEventListener('input', updatePriceDisplay);
        priceMax.addEventListener('input', updatePriceDisplay);
        
        // Apply filter on change (not input for better performance)
        priceMin.addEventListener('change', () => {
            loadProducts();
            updateActiveFilterTags();
        });
        priceMax.addEventListener('change', () => {
            loadProducts();
            updateActiveFilterTags();
        });

        updatePriceDisplay();
    }

    // Setup event listeners
    function setupEventListeners() {
        // Search
        $('#searchInput').addEventListener('input', window.AppUtils.debounce(() => {
            activeFilters.search = $('#searchInput').value;
            currentPage = 1;
            loadProducts();
            updateActiveFilterTags();
        }, 500));

        // Category filter
        $('#categoryFilter').addEventListener('change', (e) => {
            activeFilters.category = e.target.value;
            currentPage = 1;
            loadProducts();
            updateActiveFilterTags();
        });

        // Sort
        $('#sortSelect').addEventListener('change', (e) => {
            activeFilters.sort_by = e.target.value;
            loadProducts();
        });

        // Rating filter
        $$('input[name="rating"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                activeFilters.min_rating = e.target.value ? parseFloat(e.target.value) : null;
                currentPage = 1;
                loadProducts();
                updateActiveFilterTags();
            });
        });

        // In stock filter
        $('#inStockOnly').addEventListener('change', (e) => {
            activeFilters.in_stock = e.target.checked ? true : null;
            currentPage = 1;
            loadProducts();
            updateActiveFilterTags();
        });

        // Brand search
        $('#brandSearch').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            $$('.brand-checkbox').forEach(checkbox => {
                const label = checkbox.closest('.checkbox-label');
                const brandName = checkbox.value.toLowerCase();
                label.style.display = brandName.includes(searchTerm) ? 'flex' : 'none';
            });
        });

        // Clear all filters
        $('#clearAllFilters').addEventListener('click', clearAllFilters);
    }

    // Handle brand filter change
    function handleBrandFilterChange() {
        const selectedBrands = Array.from($$('.brand-checkbox:checked')).map(cb => cb.value);
        activeFilters.brands = selectedBrands;
        currentPage = 1;
        loadProducts();
        updateActiveFilterTags();
    }

    // Load products with current filters
    async function loadProducts() {
        const loading = $('#loadingProducts');
        const grid = $('#productsGrid');
        
        loading.style.display = 'block';
        grid.style.display = 'none';
        
        try {
            // Build query parameters
            const params = new URLSearchParams({
                page: currentPage,
                per_page: productsPerPage,
                sort_by: activeFilters.sort_by
            });

            if (activeFilters.search) params.append('search', activeFilters.search);
            if (activeFilters.category) params.append('category', activeFilters.category);
            if (activeFilters.price_min !== filterOptions.priceRange.min) {
                params.append('price_min', activeFilters.price_min);
            }
            if (activeFilters.price_max !== filterOptions.priceRange.max) {
                params.append('price_max', activeFilters.price_max);
            }
            if (activeFilters.brands.length > 0) {
                params.append('brands', activeFilters.brands.join(','));
            }
            if (activeFilters.min_rating !== null) {
                params.append('min_rating', activeFilters.min_rating);
            }
            if (activeFilters.in_stock !== null) {
                params.append('in_stock', 'true');
            }

            const data = await fetchAPI(`/api/products?${params.toString()}`);
            
            if (data.status === 'success') {
                totalProducts = data.pagination.total;
                displayProducts(data.data);
                displayPagination(data.pagination);
                updateResultsCount(data.data.length, totalProducts);
            }
        } catch (error) {
            showError(grid, 'Failed to load products. Please try again.');
            console.error(error);
        } finally {
            loading.style.display = 'none';
            grid.style.display = 'grid';
        }
    }

    // Display products
    function displayProducts(products) {
        const grid = $('#productsGrid');
        
        if (products.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-box-open"></i>
                    <h3>No Products Found</h3>
                    <p>Try adjusting your filters or search terms</p>
                    <button class="btn-primary" onclick="location.reload()">Reset Filters</button>
                </div>
            `;
            return;
        }

        grid.innerHTML = products.map(product => `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-image">
                    <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                         alt="${product.name}" 
                         loading="lazy">
                    ${product.original_price ? '<span class="sale-badge">SALE</span>' : ''}
                    ${!product.is_available || product.stock_quantity === 0 ? 
                        '<span class="out-of-stock-badge">Out of Stock</span>' : ''}
                </div>
                <div class="product-info">
                    <div class="product-brand">${product.brand || 'Generic'}</div>
                    <h3 class="product-name">${product.name}</h3>
                    <div class="product-rating">
                        ${formatStars(product.average_rating)}
                        <span class="rating-count">(${product.review_count})</span>
                    </div>
                    <div class="product-price">
                        <span class="current-price">${formatCurrency(product.price)}</span>
                        ${product.original_price ? 
                            `<span class="original-price">${formatCurrency(product.original_price)}</span>
                             <span class="discount">${Math.round((1 - product.price / product.original_price) * 100)}% OFF</span>` 
                            : ''}
                    </div>
                    <div class="product-category">
                        <i class="fas fa-tag"></i> ${product.category}
                    </div>
                </div>
                <button class="btn-view-product" data-product-id="${product.id}">
                    View Details
                </button>
            </div>
        `).join('');

        // Add click listeners to view buttons
        $$('.btn-view-product').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const productId = e.target.dataset.productId;
                showProductDetail(productId);
            });
        });
    }

    // Display pagination
    function displayPagination(pagination) {
        const container = $('#pagination');
        const { page, pages, total } = pagination;

        if (pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '<div class="pagination-controls">';

        // Previous button
        if (page > 1) {
            paginationHTML += `<button class="btn-page" data-page="${page - 1}">
                <i class="fas fa-chevron-left"></i> Previous
            </button>`;
        }

        // Page numbers
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(pages, page + 2);

        if (startPage > 1) {
            paginationHTML += `<button class="btn-page" data-page="1">1</button>`;
            if (startPage > 2) paginationHTML += '<span class="pagination-dots">...</span>';
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `<button class="btn-page ${i === page ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        if (endPage < pages) {
            if (endPage < pages - 1) paginationHTML += '<span class="pagination-dots">...</span>';
            paginationHTML += `<button class="btn-page" data-page="${pages}">${pages}</button>`;
        }

        // Next button
        if (page < pages) {
            paginationHTML += `<button class="btn-page" data-page="${page + 1}">
                Next <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        paginationHTML += '</div>';
        container.innerHTML = paginationHTML;

        // Add click listeners
        $$('.btn-page').forEach(btn => {
            btn.addEventListener('click', (e) => {
                currentPage = parseInt(e.target.dataset.page);
                loadProducts();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }

    // Update results count
    function updateResultsCount(showing, total) {
        $('#resultCount').textContent = showing;
        $('#totalCount').textContent = total;
    }

    // Update active filter tags
    function updateActiveFilterTags() {
        const container = $('#activeFilters');
        const tags = [];

        if (activeFilters.search) {
            tags.push({ type: 'search', label: `Search: "${activeFilters.search}"`, value: '' });
        }
        if (activeFilters.category) {
            tags.push({ type: 'category', label: activeFilters.category, value: '' });
        }
        if (activeFilters.price_min !== filterOptions.priceRange.min || 
            activeFilters.price_max !== filterOptions.priceRange.max) {
            tags.push({ 
                type: 'price', 
                label: `${formatCurrency(activeFilters.price_min)} - ${formatCurrency(activeFilters.price_max)}`,
                value: '' 
            });
        }
        activeFilters.brands.forEach(brand => {
            tags.push({ type: 'brand', label: brand, value: brand });
        });
        if (activeFilters.min_rating) {
            tags.push({ type: 'rating', label: `${activeFilters.min_rating}+ Stars`, value: '' });
        }
        if (activeFilters.in_stock) {
            tags.push({ type: 'stock', label: 'In Stock Only', value: '' });
        }

        if (tags.length === 0) {
            container.innerHTML = '';
            return;
        }

        container.innerHTML = '<div class="filter-tags">' + 
            tags.map(tag => `
                <span class="filter-tag" data-type="${tag.type}" data-value="${tag.value}">
                    ${tag.label}
                    <i class="fas fa-times"></i>
                </span>
            `).join('') +
            '</div>';

        // Add click listeners to remove tags
        $$('.filter-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                const type = e.currentTarget.dataset.type;
                const value = e.currentTarget.dataset.value;
                removeFilter(type, value);
            });
        });
    }

    // Remove individual filter
    function removeFilter(type, value) {
        switch (type) {
            case 'search':
                activeFilters.search = '';
                $('#searchInput').value = '';
                break;
            case 'category':
                activeFilters.category = '';
                $('#categoryFilter').value = '';
                break;
            case 'price':
                activeFilters.price_min = filterOptions.priceRange.min;
                activeFilters.price_max = filterOptions.priceRange.max;
                $('#priceMin').value = filterOptions.priceRange.min;
                $('#priceMax').value = filterOptions.priceRange.max;
                $('#priceMinDisplay').textContent = formatCurrency(filterOptions.priceRange.min);
                $('#priceMaxDisplay').textContent = formatCurrency(filterOptions.priceRange.max);
                break;
            case 'brand':
                activeFilters.brands = activeFilters.brands.filter(b => b !== value);
                $$('.brand-checkbox').forEach(cb => {
                    if (cb.value === value) cb.checked = false;
                });
                break;
            case 'rating':
                activeFilters.min_rating = null;
                $$('input[name="rating"]').forEach(r => r.checked = false);
                break;
            case 'stock':
                activeFilters.in_stock = null;
                $('#inStockOnly').checked = false;
                break;
        }
        currentPage = 1;
        loadProducts();
        updateActiveFilterTags();
    }

    // Clear all filters
    function clearAllFilters() {
        activeFilters = {
            search: '',
            category: '',
            price_min: filterOptions.priceRange.min,
            price_max: filterOptions.priceRange.max,
            brands: [],
            min_rating: null,
            in_stock: null,
            sort_by: 'newest'
        };

        // Reset UI
        $('#searchInput').value = '';
        $('#categoryFilter').value = '';
        $('#priceMin').value = filterOptions.priceRange.min;
        $('#priceMax').value = filterOptions.priceRange.max;
        $('#priceMinDisplay').textContent = formatCurrency(filterOptions.priceRange.min);
        $('#priceMaxDisplay').textContent = formatCurrency(filterOptions.priceRange.max);
        $$('.brand-checkbox').forEach(cb => cb.checked = false);
        $$('input[name="rating"]').forEach(r => r.checked = false);
        $('#inStockOnly').checked = false;
        $('#sortSelect').value = 'newest';
        $('#brandSearch').value = '';

        currentPage = 1;
        loadProducts();
        updateActiveFilterTags();
        showNotification('All filters cleared!', 'info');
    }

    // Show product detail modal
    async function showProductDetail(productId) {
        try {
            const data = await fetchAPI(`/api/products/${productId}`);
            if (data.status === 'success') {
                const product = data.data;
                const modal = $('#productModal');
                const detail = $('#productDetail');

                detail.innerHTML = `
                    <div class="product-detail-content">
                        <div class="product-detail-image">
                            <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${product.name}">
                        </div>
                        <div class="product-detail-info">
                            <div class="product-brand-large">${product.brand || 'Generic'}</div>
                            <h2>${product.name}</h2>
                            <div class="product-rating-large">
                                ${formatStars(product.average_rating)}
                                <span>${product.average_rating.toFixed(1)}</span>
                                <span class="rating-count">(${product.review_count} reviews)</span>
                            </div>
                            <div class="product-price-large">
                                <span class="current-price">${formatCurrency(product.price)}</span>
                                ${product.original_price ? 
                                    `<span class="original-price">${formatCurrency(product.original_price)}</span>
                                     <span class="discount-badge">${Math.round((1 - product.price / product.original_price) * 100)}% OFF</span>` 
                                    : ''}
                            </div>
                            <div class="product-meta">
                                <div class="meta-item">
                                    <i class="fas fa-tag"></i>
                                    <span>Category: ${product.category}</span>
                                </div>
                                <div class="meta-item">
                                    <i class="fas fa-warehouse"></i>
                                    <span>Stock: ${product.stock_quantity > 0 ? `${product.stock_quantity} available` : 'Out of stock'}</span>
                                </div>
                                ${product.color ? `
                                <div class="meta-item">
                                    <i class="fas fa-palette"></i>
                                    <span>Color: ${product.color}</span>
                                </div>` : ''}
                                ${product.size ? `
                                <div class="meta-item">
                                    <i class="fas fa-ruler"></i>
                                    <span>Size: ${product.size}</span>
                                </div>` : ''}
                            </div>
                            <div class="product-description">
                                <h3>Description</h3>
                                <p>${product.description || 'No description available.'}</p>
                            </div>
                            <div class="product-actions">
                                <button class="btn-primary" ${product.stock_quantity === 0 ? 'disabled' : ''}>
                                    <i class="fas fa-shopping-cart"></i> Add to Cart
                                </button>
                                <button class="btn-secondary">
                                    <i class="fas fa-heart"></i> Add to Wishlist
                                </button>
                            </div>
                        </div>
                    </div>
                `;

                modal.style.display = 'block';
            }
        } catch (error) {
            showNotification('Failed to load product details', 'error');
            console.error(error);
        }
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

})();
