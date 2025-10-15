// ============================================
// FLOATING CHATBOT WIDGET
// AI-Powered Shopping Assistant
// ============================================

(function() {
    'use strict';
    
    // Use utilities from main.js
    const { $, fetchAPI, showNotification } = window.AppUtils;
    
    // Chatbot state
    let isChatOpen = false;
    let conversationId = null;
    let isTyping = false;
    
    // Initialize chatbot when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        initializeChatbot();
        loadConversationHistory();
        setupEventListeners();
    });
    
    function initializeChatbot() {
        // Generate unique conversation ID
        conversationId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Add notification badge animation
        const badge = $('#chatBadge');
        if (badge) {
            setTimeout(() => {
                badge.style.animation = 'pulse 2s infinite';
            }, 3000);
        }
    }
    
    function setupEventListeners() {
        // Handle Enter key in chat input
        const input = $('#chatbotInput');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChatbotMessage();
                }
            });
        }
        
        // Handle escape key to close chat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isChatOpen) {
                toggleChatbot();
            }
        });
    }
    
    // Toggle chatbot visibility
    window.toggleChatbot = function() {
        const chatWindow = $('#chatWindow');
        const chatToggle = $('#chatToggle');
        
        if (!chatWindow || !chatToggle) return;
        
        isChatOpen = !isChatOpen;
        
        if (isChatOpen) {
            chatWindow.classList.remove('hidden');
            chatToggle.style.transform = 'scale(0.9)';
            
            // Focus input after animation
            setTimeout(() => {
                const input = $('#chatbotInput');
                if (input) input.focus();
            }, 300);
            
            // Remove notification badge
            const badge = $('#chatBadge');
            if (badge) badge.style.display = 'none';
            
        } else {
            chatWindow.classList.add('hidden');
            chatToggle.style.transform = 'scale(1)';
        }
    };
    
    // Send suggestion message
    window.sendSuggestion = function(message) {
        const input = $('#chatbotInput');
        if (input) {
            input.value = message;
            sendChatbotMessage();
        }
    };
    
    // Send chatbot message
    window.sendChatbotMessage = async function() {
        const input = $('#chatbotInput');
        const sendBtn = $('#chatbotSend');
        const chatBody = $('#chatBody');
        
        if (!input || !sendBtn || !chatBody) return;
        
        const message = input.value.trim();
        if (!message || isTyping) return;
        
        // Disable input while processing
        input.disabled = true;
        sendBtn.disabled = true;
        isTyping = true;
        
        // Add user message
        addMessage(message, 'user');
        
        // Clear input
        input.value = '';
        
        // Determine if this is a search query or general chat
        const isSearchQuery = isProductSearch(message);
        
        try {
            let response;
            
            if (isSearchQuery) {
                // Use natural language search
                response = await fetch('/api/search/natural', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: message,
                        limit: 6
                    })
                });
            } else {
                // Use general chat
                response = await fetch('/api/chat/general', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: conversationId
                    })
                });
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                if (isSearchQuery && data.data.products) {
                    // Display search results
                    displaySearchResults(data.data);
                } else {
                    // Display chat response
                    addMessage(data.data.response || data.data.answer, 'bot');
                }
                
                // Save to conversation history
                saveToHistory(message, data.data.response || data.data.answer || 'Search results displayed');
                
            } else {
                addMessage("I'm sorry, I couldn't process that request. Please try again!", 'bot', true);
            }
            
        } catch (error) {
            console.error('Chatbot error:', error);
            addMessage("I'm having trouble right now. Please try again in a moment!", 'bot', true);
        } finally {
            // Re-enable input
            input.disabled = false;
            sendBtn.disabled = false;
            isTyping = false;
            input.focus();
        }
    };
    
    // Add message to chat
    function addMessage(content, sender, isError = false) {
        const chatBody = $('#chatBody');
        if (!chatBody) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message${isError ? ' error' : ''}`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const timestamp = new Date().toLocaleTimeString('en-IN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${content}</p>
                <span class="message-time">${timestamp}</span>
            </div>
        `;
        
        chatBody.appendChild(messageDiv);
        
        // Scroll to bottom
        chatBody.scrollTop = chatBody.scrollHeight;
        
        // Add smooth animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
    }
    
    // Display search results in chat
    function displaySearchResults(searchData) {
        const chatBody = $('#chatBody');
        if (!chatBody) return;
        
        const products = searchData.products;
        const interpretation = searchData.ai_interpretation;
        
        if (products.length === 0) {
            addMessage("I couldn't find any products matching your search. Try different keywords or browse our categories!", 'bot');
            return;
        }
        
        // Create search results message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot-message search-results';
        
        const productsHTML = products.slice(0, 3).map(product => `
            <div class="search-result-item" onclick="openProductFromChat(${product.id})">
                <img src="${product.image_url || '/static/images/placeholder.jpg'}" 
                     alt="${product.name}" loading="lazy">
                <div class="result-info">
                    <h5>${product.name}</h5>
                    <p class="result-brand">${product.brand || 'Generic'}</p>
                    <p class="result-price">₹${product.price.toLocaleString('en-IN')}</p>
                    ${product.average_rating > 0 ? 
                        `<p class="result-rating">⭐ ${product.average_rating.toFixed(1)} (${product.review_count} reviews)</p>` 
                        : ''}
                </div>
            </div>
        `).join('');
        
        const moreResults = products.length > 3 ? products.length - 3 : 0;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content search-content">
                <p><strong>Found ${products.length} products!</strong></p>
                <p><em>${interpretation}</em></p>
                <div class="search-results-grid">
                    ${productsHTML}
                </div>
                ${moreResults > 0 ? 
                    `<p class="more-results">
                        <a href="/products?search=${encodeURIComponent(searchData.original_query)}" target="_blank">
                            View ${moreResults} more results →
                        </a>
                    </p>` 
                    : ''}
                <p class="search-suggestion">💡 <em>Click any product to see details, or ask me to compare specific items!</em></p>
            </div>
        `;
        
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    // Check if message is a product search query
    function isProductSearch(message) {
        const searchKeywords = [
            'show', 'find', 'search', 'looking for', 'need', 'want',
            'phone', 'laptop', 'mobile', 'computer', 'electronics',
            'under', 'below', 'budget', 'cheap', 'affordable',
            'best', 'top', 'trending', 'popular', 'recommend'
        ];
        
        const lowerMessage = message.toLowerCase();
        return searchKeywords.some(keyword => lowerMessage.includes(keyword));
    }
    
    // Open product from chat search results
    window.openProductFromChat = function(productId) {
        // Close chatbot
        if (isChatOpen) {
            toggleChatbot();
        }
        
        // Navigate to products page or open product modal
        if (typeof showProductDetail === 'function') {
            showProductDetail(productId);
        } else {
            window.location.href = `/products?product=${productId}`;
        }
    };
    
    // Save conversation to localStorage
    function saveToHistory(userMessage, botResponse) {
        try {
            const history = JSON.parse(localStorage.getItem('chatbot_history') || '[]');
            history.push({
                timestamp: Date.now(),
                user: userMessage,
                bot: botResponse,
                conversation_id: conversationId
            });
            
            // Keep only last 50 messages
            if (history.length > 50) {
                history.splice(0, history.length - 50);
            }
            
            localStorage.setItem('chatbot_history', JSON.stringify(history));
        } catch (error) {
            console.warn('Could not save chat history:', error);
        }
    }
    
    // Load conversation history
    function loadConversationHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('chatbot_history') || '[]');
            const recentHistory = history.slice(-5); // Show last 5 exchanges
            
            if (recentHistory.length > 0) {
                const chatBody = $('#chatBody');
                if (chatBody) {
                    // Add history indicator
                    const historyDiv = document.createElement('div');
                    historyDiv.className = 'chat-history-indicator';
                    historyDiv.innerHTML = `
                        <div class="history-divider">
                            <span>Recent conversation</span>
                        </div>
                    `;
                    chatBody.appendChild(historyDiv);
                    
                    // Add recent messages
                    recentHistory.forEach(item => {
                        addMessage(item.user, 'user');
                        addMessage(item.bot, 'bot');
                    });
                }
            }
        } catch (error) {
            console.warn('Could not load chat history:', error);
        }
    }
    
    // Add CSS for search results (injected dynamically)
    const searchResultsCSS = `
        .search-results-grid {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin: 1rem 0;
        }
        
        .search-result-item {
            display: flex;
            gap: 0.75rem;
            padding: 0.75rem;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .search-result-item:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-1px);
        }
        
        .search-result-item img {
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: var(--radius-sm);
        }
        
        .result-info h5 {
            margin: 0 0 0.25rem 0;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .result-info p {
            margin: 0;
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .result-price {
            font-weight: 600;
            color: var(--accent-color);
        }
        
        .search-result-item:hover .result-price {
            color: white;
        }
        
        .more-results a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }
        
        .search-suggestion {
            font-style: italic;
            opacity: 0.8;
            margin-top: 0.5rem;
        }
        
        .chat-history-indicator {
            text-align: center;
            margin: 1rem 0;
        }
        
        .history-divider {
            position: relative;
            color: var(--text-muted);
            font-size: 0.8rem;
        }
        
        .history-divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--glass-border);
            z-index: 1;
        }
        
        .history-divider span {
            background: var(--bg-primary);
            padding: 0 0.75rem;
            position: relative;
            z-index: 2;
        }
        
        .message-time {
            font-size: 0.7rem;
            opacity: 0.6;
            margin-top: 0.25rem;
            display: block;
        }
    `;
    
    // Inject search results CSS
    const styleSheet = document.createElement('style');
    styleSheet.textContent = searchResultsCSS;
    document.head.appendChild(styleSheet);
    
})();