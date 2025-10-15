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
            if (data.status === 'success' && data.data) {
                filterOptions = data.data;
                
                // Update active filters with actual price range
                if (filterOptions.priceRange) {
                    activeFilters.price_min = filterOptions.priceRange.min;
                    activeFilters.price_max = filterOptions.priceRange.max;
                }
                
                populateBrandFilters();
                populateCategoryFilter();
                setupPriceSliders();
            }
        } catch (error) {
            console.error('Failed to load filter options:', error);
            showNotification('Failed to load filters. Using defaults.', 'error');
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

        // Guard against undefined priceRange with fallback values
        if (!filterOptions.priceRange || typeof filterOptions.priceRange.min === 'undefined') {
            console.warn('Price range not available, using default values');
            filterOptions.priceRange = { min: 100, max: 100000 };
        }

        // Ensure elements exist before setting properties
        if (!priceMin || !priceMax || !priceMinDisplay || !priceMaxDisplay) {
            console.warn('Price slider elements not found');
            return;
        }

        priceMin.min = filterOptions.priceRange.min;
        priceMin.max = filterOptions.priceRange.max;
        priceMax.min = filterOptions.priceRange.min;
        priceMax.max = filterOptions.priceRange.max;
        
        priceMin.value = activeFilters.price_min || filterOptions.priceRange.min;
        priceMax.value = activeFilters.price_max || filterOptions.priceRange.max;

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
        
        // Show skeleton loaders instead of generic loading
        showSkeletonLoaders();
        loading.style.display = 'none';
        
        try {
            // Build query parameters
            const params = new URLSearchParams({
                page: currentPage,
                per_page: productsPerPage,
                sort_by: activeFilters.sort_by
            });

            if (activeFilters.search) params.append('search', activeFilters.search);
            if (activeFilters.category) params.append('category', activeFilters.category);
            
            // Only add price filters if they differ from defaults and filterOptions is loaded
            if (filterOptions.priceRange) {
                if (activeFilters.price_min !== null && activeFilters.price_min !== filterOptions.priceRange.min) {
                    params.append('price_min', activeFilters.price_min);
                }
                if (activeFilters.price_max !== null && activeFilters.price_max !== filterOptions.priceRange.max) {
                    params.append('price_max', activeFilters.price_max);
                }
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

        grid.innerHTML = products.map(product => {
            // Determine category icon for placeholder
            const categoryIcon = getCategoryIcon(product.category);
            const discountPercentage = product.original_price ? 
                Math.round((1 - product.price / product.original_price) * 100) : 0;
            const hasDiscount = discountPercentage > 0;
            
            return `
                <div class="product-card" data-product-id="${product.id}">
                    <div class="product-image-container">
                        <div class="product-image">
                            <div class="image-placeholder" style="display: flex;">
                                <div class="placeholder-icon">
                                    <i class="fas ${categoryIcon}"></i>
                                </div>
                                <div class="placeholder-text">${product.category || 'Product'}</div>
                            </div>
                        </div>
                        
                        <!-- Badges -->
                        <div class="product-badges">
                            ${hasDiscount ? `<span class="sale-badge">-${discountPercentage}%</span>` : ''}
                            ${!product.is_available || product.stock_quantity === 0 ? 
                                '<span class="out-of-stock-badge">Out of Stock</span>' : ''}
                            ${product.is_featured ? '<span class="featured-badge">Featured</span>' : ''}
                        </div>
                        
                        <!-- Quick Actions -->
                        <div class="quick-actions">
                            <button class="quick-action-btn wishlist-btn" title="Add to Wishlist" onclick="toggleWishlist(${product.id}, event)">
                                <i class="far fa-heart"></i>
                            </button>
                            <button class="quick-action-btn compare-btn" title="Compare" onclick="addToCompare(${product.id}, event)">
                                <i class="fas fa-balance-scale"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="product-info">
                        <div class="product-header">
                            <div class="product-brand">${product.brand || 'Generic'}</div>
                            <div class="product-category-tag">
                                <i class="fas fa-tag"></i>
                                ${product.category}
                            </div>
                        </div>
                        
                        <h3 class="product-name" title="${product.name}">${product.name}</h3>
                        
                        <div class="product-rating">
                            <div class="stars">${formatStars(product.average_rating)}</div>
                            <span class="rating-text">
                                ${product.average_rating > 0 ? product.average_rating.toFixed(1) : 'New'}
                                ${product.review_count > 0 ? `(${product.review_count})` : ''}
                            </span>
                        </div>
                        
                        <div class="product-price-section">
                            <div class="price-group">
                                <span class="current-price">${formatCurrency(product.price)}</span>
                                ${product.original_price ? 
                                    `<span class="original-price">${formatCurrency(product.original_price)}</span>` 
                                    : ''}
                            </div>
                            ${hasDiscount ? `<div class="savings">Save ${formatCurrency(product.original_price - product.price)}</div>` : ''}
                        </div>
                        
                        <div class="product-meta">
                            ${product.stock_quantity > 0 && product.stock_quantity <= 5 ? 
                                `<div class="stock-warning">⚠️ Only ${product.stock_quantity} left</div>` : ''}
                            ${product.free_shipping ? '<div class="shipping-info">🚚 Free Shipping</div>' : ''}
                        </div>
                    </div>
                    
                    <div class="product-actions">
                        <button class="btn-view-product primary" data-product-id="${product.id}">
                            <i class="fas fa-eye"></i>
                            View Details
                        </button>
                        ${product.is_available && product.stock_quantity > 0 ? `
                            <button class="btn-add-cart secondary" data-product-id="${product.id}">
                                <i class="fas fa-shopping-cart"></i>
                                Add to Cart
                            </button>
                        ` : `
                            <button class="btn-notify secondary" data-product-id="${product.id}">
                                <i class="fas fa-bell"></i>
                                Notify Me
                            </button>
                        `}
                    </div>
                </div>
            `;
        }).join('');

        // Add click listeners to view buttons
        $$('.btn-view-product').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const productId = e.target.dataset.productId;
                showProductDetail(productId);
            });
        });
        
        // Add click listeners to add cart buttons
        $$('.btn-add-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                const productId = e.target.dataset.productId;
                showNotification('Added to cart!', 'success');
                // Implement cart functionality here
            });
        });
        
        // Add click listeners to notify buttons
        $$('.btn-notify').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                const productId = e.target.dataset.productId;
                showNotification('You will be notified when this item is back in stock', 'info');
                // Implement notification signup here
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
        
        // Only show price tag if filterOptions is loaded and prices differ from defaults
        if (filterOptions.priceRange && 
            (activeFilters.price_min !== null && activeFilters.price_min !== filterOptions.priceRange.min) || 
            (activeFilters.price_max !== null && activeFilters.price_max !== filterOptions.priceRange.max)) {
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
        // Guard against uninitialized filterOptions
        const minPrice = filterOptions.priceRange ? filterOptions.priceRange.min : 299;
        const maxPrice = filterOptions.priceRange ? filterOptions.priceRange.max : 89999;
        
        activeFilters = {
            search: '',
            category: '',
            price_min: minPrice,
            price_max: maxPrice,
            brands: [],
            min_rating: null,
            in_stock: null,
            sort_by: 'newest'
        };

        // Reset UI
        $('#searchInput').value = '';
        $('#categoryFilter').value = '';
        $('#priceMin').value = minPrice;
        $('#priceMax').value = maxPrice;
        $('#priceMinDisplay').textContent = formatCurrency(minPrice);
        $('#priceMaxDisplay').textContent = formatCurrency(maxPrice);
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

    // ============================================
    // PHASE 2: VISUAL IMPROVEMENTS
    // ============================================

    // Show skeleton loaders
    function showSkeletonLoaders() {
        const grid = $('#productsGrid');
        grid.style.display = 'grid';
        
        const skeletons = Array(12).fill(null).map(() => `
            <div class="skeleton-card">
                <div class="skeleton-image skeleton"></div>
                <div class="skeleton-content">
                    <div class="skeleton-text subtitle skeleton"></div>
                    <div class="skeleton-text title skeleton"></div>
                    <div class="skeleton-text skeleton"></div>
                    <div class="skeleton-text skeleton"></div>
                    <div class="skeleton-text price skeleton"></div>
                </div>
            </div>
        `).join('');
        
        grid.innerHTML = skeletons;
    }

    // Recently Viewed Products - LocalStorage management
    const RecentlyViewed = {
        key: 'recentlyViewed',
        maxItems: 6,
        
        add(product) {
            let items = this.get();
            
            // Remove if already exists
            items = items.filter(item => item.id !== product.id);
            
            // Add to beginning
            items.unshift({
                id: product.id,
                name: product.name,
                price: product.price,
                image_url: product.image_url,
                brand: product.brand
            });
            
            // Keep only max items
            items = items.slice(0, this.maxItems);
            
            localStorage.setItem(this.key, JSON.stringify(items));
            this.display();
        },
        
        get() {
            try {
                return JSON.parse(localStorage.getItem(this.key) || '[]');
            } catch {
                return [];
            }
        },
        
        clear() {
            localStorage.removeItem(this.key);
            this.display();
        },
        
        display() {
            const items = this.get();
            if (items.length === 0) return;
            
            let container = $('.recently-viewed-section');
            
            // Create section if it doesn't exist
            if (!container) {
                container = document.createElement('div');
                container.className = 'recently-viewed-section fade-in';
                $('#productsGrid').parentElement.appendChild(container);
            }
            
            container.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h3><i class="fas fa-history"></i> Recently Viewed</h3>
                    <button class="btn-clear-filters" onclick="window.RecentlyViewed.clear()">
                        Clear History
                    </button>
                </div>
                <div class="recently-viewed-grid">
                    ${items.map(item => `
                        <div class="recently-viewed-item" data-product-id="${item.id}">
                            <img src="${item.image_url || '/static/images/placeholder.jpg'}" 
                                 alt="${item.name}" loading="lazy">
                            <h4>${item.name}</h4>
                            <div class="price">${formatCurrency(item.price)}</div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            // Add click listeners
            $$('.recently-viewed-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    const productId = e.currentTarget.dataset.productId;
                    showProductDetail(productId);
                });
            });
        }
    };
    
    // Expose globally for button onclick
    window.RecentlyViewed = RecentlyViewed;
    
    // Display recently viewed on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => RecentlyViewed.display());
    } else {
        RecentlyViewed.display();
    }

    // Add to recently viewed when viewing product detail
    const originalShowProductDetail = showProductDetail;
    showProductDetail = async function(productId) {
        try {
            const data = await fetchAPI(`/api/products/${productId}`);
            if (data.status === 'success') {
                const product = data.data;
                
                // Add to recently viewed
                RecentlyViewed.add(product);
                
                // Show modal (existing code)
                const modal = $('#productModal');
                const detail = $('#productDetail');

                detail.innerHTML = `
                    <div class="product-detail-content">
                        <div class="product-detail-image">
                            <div class="modal-main-image">
                                <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                                     alt="${product.name}"
                                     id="modalMainImage">
                            </div>
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
                modal.classList.add('fade-in');
            }
        } catch (error) {
            showNotification('Failed to load product details', 'error');
            console.error(error);
        }
    };

    // Add wishlist functionality to product cards
    function addWishlistButtons() {
        $$('.product-card').forEach(card => {
            const wishlistBtn = document.createElement('button');
            wishlistBtn.className = 'btn-wishlist';
            wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
            
            wishlistBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                wishlistBtn.classList.toggle('active');
                
                if (wishlistBtn.classList.contains('active')) {
                    wishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
                    showNotification('Added to wishlist! ❤️', 'success');
                } else {
                    wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
                    showNotification('Removed from wishlist', 'info');
                }
            });
            
            const imageContainer = card.querySelector('.product-image');
            if (imageContainer) {
                imageContainer.appendChild(wishlistBtn);
            }
        });
    }

    // Add quick action buttons
    function addQuickActions() {
        $$('.product-card').forEach(card => {
            const productId = card.dataset.productId;
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'product-quick-actions';
            actionsDiv.innerHTML = `
                <button class="quick-action-btn" title="Quick View" data-action="view">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="quick-action-btn" title="Add to Cart" data-action="cart">
                    <i class="fas fa-shopping-cart"></i>
                </button>
            `;
            
            // Add event listeners
            actionsDiv.querySelector('[data-action="view"]').addEventListener('click', (e) => {
                e.stopPropagation();
                showProductDetail(productId);
            });
            
            actionsDiv.querySelector('[data-action="cart"]').addEventListener('click', (e) => {
                e.stopPropagation();
                showNotification('Added to cart! 🛒', 'success');
            });
            
            const imageContainer = card.querySelector('.product-image');
            if (imageContainer) {
                imageContainer.appendChild(actionsDiv);
            }
        });
    }

    // Enhance display products to add visual improvements
    const originalDisplayProducts = displayProducts;
    displayProducts = function(products) {
        originalDisplayProducts(products);
        
        // Add enhancements after products are displayed
        setTimeout(() => {
            addWishlistButtons();
            addQuickActions();
        }, 50);
    };

    // ============================================
    // PHASE 3: RECOMMENDATION FUNCTIONS
    // ============================================

    // Load trending products on page load
    async function loadTrendingProducts() {
        try {
            const container = $('#trendingProducts');
            if (!container) return;
            
            container.innerHTML = '<div class="recommendation-loading"><div class="spinner"></div>Loading trending products...</div>';
            
            const data = await fetchAPI('/api/products/trending?limit=6');
            if (data.status === 'success' && data.data.products) {
                displayRecommendationProducts(data.data.products, container, 'trending');
            } else {
                container.innerHTML = '<div class="recommendation-empty">No trending products available.</div>';
            }
        } catch (error) {
            console.error('Failed to load trending products:', error);
            const container = $('#trendingProducts');
            if (container) {
                container.innerHTML = '<div class="recommendation-empty">Failed to load trending products.</div>';
            }
        }
    }

    // Load similar products for product detail modal
    async function loadSimilarProducts(productId) {
        try {
            const container = $('#similarProducts');
            if (!container) return;
            
            container.innerHTML = '<div class="recommendation-loading"><div class="spinner"></div>Finding similar products...</div>';
            
            const data = await fetchAPI(`/api/products/${productId}/similar`);
            if (data.status === 'success' && data.data.length > 0) {
                displayRecommendationProducts(data.data, container, 'similar');
            } else {
                container.innerHTML = '<div class="recommendation-empty">No similar products found.</div>';
            }
        } catch (error) {
            console.error('Failed to load similar products:', error);
            const container = $('#similarProducts');
            if (container) {
                container.innerHTML = '<div class="recommendation-empty">Failed to load similar products.</div>';
            }
        }
    }

    // Load frequently bought together products
    async function loadFrequentlyBought(productId) {
        try {
            const container = $('#frequentlyBought');
            if (!container) return;
            
            container.innerHTML = '<div class="recommendation-loading"><div class="spinner"></div>Loading frequently bought items...</div>';
            
            const data = await fetchAPI(`/api/products/${productId}/frequently-bought`);
            if (data.status === 'success' && data.data.length > 0) {
                displayRecommendationProducts(data.data, container, 'frequently-bought');
            } else {
                container.innerHTML = '<div class="recommendation-empty">No frequently bought items found.</div>';
            }
        } catch (error) {
            console.error('Failed to load frequently bought products:', error);
            const container = $('#frequentlyBought');
            if (container) {
                container.innerHTML = '<div class="recommendation-empty">Failed to load frequently bought items.</div>';
            }
        }
    }

    // Display recommendation products in a grid
    function displayRecommendationProducts(products, container, type) {
        if (!products || products.length === 0) {
            container.innerHTML = '<div class="recommendation-empty">No products available.</div>';
            return;
        }

        const productsHTML = products.map((product, index) => {
            const salePercent = product.original_price ? 
                Math.round((1 - product.price / product.original_price) * 100) : 0;
            
            return `
                <div class="recommendation-card" data-product-id="${product.id}" onclick="openRecommendationProduct(${product.id})">
                    <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                         alt="${product.name}" 
                         class="recommendation-card-image"
                         loading="lazy">
                    
                    ${salePercent > 0 ? `<div class="sale-badge">${salePercent}% OFF</div>` : ''}
                    
                    <div class="recommendation-card-brand">${product.brand || 'Generic'}</div>
                    <h4 class="recommendation-card-title">${product.name}</h4>
                    
                    <div class="recommendation-card-price">
                        ${formatCurrency(product.price)}
                        ${product.original_price ? 
                            `<span class="original-price">${formatCurrency(product.original_price)}</span>` : ''
                        }
                    </div>
                    
                    ${product.average_rating > 0 ? `
                        <div class="recommendation-card-rating">
                            <span class="stars">${formatStars(product.average_rating)}</span>
                            <span class="rating-count">(${product.review_count || 0})</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        container.innerHTML = productsHTML;
    }

    // Open recommendation product (for click handling)
    window.openRecommendationProduct = function(productId) {
        showProductDetail(productId);
    };

    // Enhanced showProductDetail to load recommendations
    const originalShowProductDetailFn = showProductDetail;
    showProductDetail = async function(productId) {
        // Call original function
        await originalShowProductDetailFn(productId);
        
        // Load recommendations after modal opens
        setTimeout(() => {
            loadSimilarProducts(productId);
            loadFrequentlyBought(productId);
        }, 300);
    };

    // Load trending products when page loads
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(loadTrendingProducts, 1000); // Load after initial products
    });

    // ============================================
    // PHASE 4: AI ENHANCEMENT FUNCTIONS
    // ============================================

    // Load AI-enhanced product description
    window.loadAIDescription = async function(productId) {
        const content = $('#aiEnhancementContent');
        const button = event.target;
        
        try {
            button.disabled = true;
            button.innerHTML = '⏳ Generating...';
            
            content.innerHTML = '<div class="ai-loading">🤖 AI is generating enhanced description...</div>';
            
            const data = await fetchAPI(`/api/products/${productId}/ai-description`);
            if (data.status === 'success') {
                const aiData = data.data;
                content.innerHTML = `
                    <div class="ai-description-result">
                        <h5>🤖 AI-Enhanced Description</h5>
                        <div class="ai-description-content">
                            ${aiData.ai_description}
                        </div>
                        <div class="ai-attribution">
                            Generated by ${aiData.enhanced_by} for ${aiData.target_market}
                        </div>
                        <div class="description-comparison">
                            <details>
                                <summary>Compare with original description</summary>
                                <div class="original-description">
                                    <strong>Original:</strong> ${aiData.original_description}
                                </div>
                            </details>
                        </div>
                    </div>
                `;
            } else {
                content.innerHTML = '<div class="ai-error">Failed to generate AI description. Please try again.</div>';
            }
        } catch (error) {
            content.innerHTML = '<div class="ai-error">Error loading AI description. Please try again.</div>';
            console.error('AI Description Error:', error);
        } finally {
            button.disabled = false;
            button.innerHTML = '🤖 Enhanced Description';
        }
    };

    // Load sentiment analysis
    window.loadSentimentAnalysis = async function(productId) {
        const content = $('#aiEnhancementContent');
        const button = event.target;
        
        try {
            button.disabled = true;
            button.innerHTML = '⏳ Analyzing...';
            
            content.innerHTML = '<div class="ai-loading">📊 AI is analyzing customer sentiment...</div>';
            
            const data = await fetchAPI(`/api/products/${productId}/sentiment`);
            if (data.status === 'success') {
                const sentiment = data.data.sentiment_analysis;
                content.innerHTML = `
                    <div class="sentiment-analysis-result">
                        <h5>📊 Customer Sentiment Analysis</h5>
                        <div class="sentiment-score">
                            <div class="score-circle">
                                <span class="score">${sentiment.overall_sentiment_score}</span>
                                <span class="score-label">Overall Score</span>
                            </div>
                        </div>
                        <div class="sentiment-distribution">
                            <div class="sentiment-bar">
                                <div class="positive" style="width: ${sentiment.sentiment_distribution.positive}%">
                                    ${sentiment.sentiment_distribution.positive}% Positive
                                </div>
                                <div class="neutral" style="width: ${sentiment.sentiment_distribution.neutral}%">
                                    ${sentiment.sentiment_distribution.neutral}% Neutral
                                </div>
                                <div class="negative" style="width: ${sentiment.sentiment_distribution.negative}%">
                                    ${sentiment.sentiment_distribution.negative}% Negative
                                </div>
                            </div>
                        </div>
                        <div class="sentiment-insights">
                            <h6>AI Insights:</h6>
                            <div class="analysis-text">${sentiment.analysis}</div>
                        </div>
                        <div class="ai-attribution">
                            Analysis by ${data.data.analyzed_by} • ${data.data.total_reviews_analyzed} reviews analyzed
                        </div>
                    </div>
                `;
            } else {
                content.innerHTML = '<div class="ai-error">Failed to analyze sentiment. Please try again.</div>';
            }
        } catch (error) {
            content.innerHTML = '<div class="ai-error">Error loading sentiment analysis. Please try again.</div>';
            console.error('Sentiment Analysis Error:', error);
        } finally {
            button.disabled = false;
            button.innerHTML = '📊 Review Sentiment';
        }
    };

    // Open product chat interface
    window.openProductChat = function(productId) {
        const content = $('#aiEnhancementContent');
        
        content.innerHTML = `
            <div class="product-chat-interface">
                <h5>💬 Ask AI About This Product</h5>
                <div class="chat-container" id="chatContainer">
                    <div class="chat-message ai-message">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">
                            Hi! I'm your AI shopping assistant. Ask me anything about this product - features, compatibility, usage, or comparisons!
                        </div>
                    </div>
                </div>
                <div class="chat-input-container">
                    <input type="text" id="chatInput" placeholder="Ask about features, compatibility, usage..." 
                           onkeypress="if(event.key==='Enter') sendChatMessage(${productId})">
                    <button onclick="sendChatMessage(${productId})" class="btn-chat-send">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Focus the input
        setTimeout(() => $('#chatInput').focus(), 100);
    };

    // Send chat message
    window.sendChatMessage = async function(productId) {
        const input = $('#chatInput');
        const question = input.value.trim();
        
        if (!question) return;
        
        const chatContainer = $('#chatContainer');
        
        // Add user message
        chatContainer.innerHTML += `
            <div class="chat-message user-message">
                <div class="message-content">${question}</div>
                <div class="message-avatar">👤</div>
            </div>
        `;
        
        // Add loading message
        chatContainer.innerHTML += `
            <div class="chat-message ai-message loading" id="loadingMessage">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                    Thinking...
                </div>
            </div>
        `;
        
        // Clear input and scroll
        input.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        try {
            const response = await fetch('/api/chat/product', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    product_id: productId
                })
            });
            
            const data = await response.json();
            
            // Remove loading message
            const loadingMsg = $('#loadingMessage');
            if (loadingMsg) loadingMsg.remove();
            
            if (data.status === 'success') {
                chatContainer.innerHTML += `
                    <div class="chat-message ai-message">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">${data.data.answer}</div>
                    </div>
                `;
            } else {
                chatContainer.innerHTML += `
                    <div class="chat-message ai-message error">
                        <div class="message-avatar">❌</div>
                        <div class="message-content">Sorry, I couldn't answer that question. Please try again.</div>
                    </div>
                `;
            }
        } catch (error) {
            // Remove loading message
            const loadingMsg = $('#loadingMessage');
            if (loadingMsg) loadingMsg.remove();
            
            chatContainer.innerHTML += `
                <div class="chat-message ai-message error">
                    <div class="message-avatar">❌</div>
                    <div class="message-content">Sorry, I'm having trouble right now. Please try again later.</div>
                </div>
            `;
            console.error('Chat Error:', error);
        }
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    // Helper functions for product cards
    function getCategoryIcon(category) {
        const categoryIcons = {
            'Electronics': 'fa-microchip',
            'Smartphones': 'fa-mobile-alt',
            'Laptops': 'fa-laptop',
            'Computers': 'fa-desktop',
            'Audio': 'fa-headphones',
            'Gaming': 'fa-gamepad',
            'Cameras': 'fa-camera',
            'Accessories': 'fa-plug',
            'Fashion': 'fa-tshirt',
            'Home': 'fa-home',
            'Books': 'fa-book',
            'Sports': 'fa-running',
            'Beauty': 'fa-spa',
            'Health': 'fa-heartbeat',
            'Toys': 'fa-puzzle-piece',
            'Automotive': 'fa-car',
            'Garden': 'fa-leaf',
            'Tools': 'fa-tools',
            'Jewelry': 'fa-gem',
            'Watches': 'fa-clock'
        };
        
        // Try exact match first
        if (categoryIcons[category]) {
            return categoryIcons[category];
        }
        
        // Try partial matches
        const lowerCategory = category.toLowerCase();
        for (const [key, icon] of Object.entries(categoryIcons)) {
            if (lowerCategory.includes(key.toLowerCase()) || key.toLowerCase().includes(lowerCategory)) {
                return icon;
            }
        }
        
        // Default icon
        return 'fa-box';
    }
    
    // Global functions for product actions
    window.toggleWishlist = function(productId, event) {
        event.stopPropagation();
        event.preventDefault();
        
        const btn = event.target.closest('.wishlist-btn');
        const icon = btn.querySelector('i');
        
        // Toggle wishlist state
        const isWishlisted = icon.classList.contains('fas');
        
        if (isWishlisted) {
            icon.classList.remove('fas');
            icon.classList.add('far');
            showNotification('Removed from wishlist', 'info');
        } else {
            icon.classList.remove('far');
            icon.classList.add('fas');
            showNotification('Added to wishlist', 'success');
        }
        
        // Here you would typically make an API call to update the backend
        // await fetchAPI(`/api/wishlist/${productId}`, { method: isWishlisted ? 'DELETE' : 'POST' });
    };
    
    window.addToCompare = function(productId, event) {
        event.stopPropagation();
        event.preventDefault();
        
        showNotification('Added to comparison list', 'info');
        // Implement comparison functionality
    };

})();
