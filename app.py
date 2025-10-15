"""
ShopSmart AI - Intelligent E-commerce Recommendation Platform
Production-ready Flask application with AI-powered product recommendations
"""
from flask import request, jsonify, render_template
from app import create_app, db
from app.models import Product, User, UserInteraction
from app.services.recommendation_service import RecommendationService
from app.services.gemini_service import GeminiService
from config import config
from sqlalchemy import func
import os
import json

# Create Flask application with appropriate configuration
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)


# Frontend Routes

@app.route('/')
def index_page():
    """Home page"""
    return render_template('index.html')


@app.route('/recommendations')
def recommendations_page():
    """Recommendations page"""
    return render_template('recommendations.html')


@app.route('/products')
def products_page():
    """Products page"""
    return render_template('products.html')


@app.route('/about')
def about_page():
    """About page"""
    return render_template('about.html')


# API Routes

@app.route('/health')
def health_check():
    """Railway health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'ShopSmart AI',
        'version': '2.0.0'
    }

@app.route('/api')
def index():
    """API health check endpoint"""
    return {
        'status': 'success',
        'message': 'E-commerce Product Recommender API is running',
        'version': '2.0.0',
        'endpoints': {
            'health': '/health',
            'stats': '/api/stats',
            'products': '/api/products',
            'users': '/api/users',
            'recommendations': {
                'get': '/api/recommend/<user_id>',
                'post': '/api/recommend',
                'similar': '/api/similar/<product_id>',
                'test_gemini': '/api/gemini/test'
            }
        }
    }


@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'database': 'connected',
        'gemini_api': 'configured' if Config.GEMINI_API_KEY else 'not configured'
    }


@app.route('/api/stats')
def stats():
    """Get database statistics"""
    try:
        stats_data = {
            'products': {
                'total': Product.query.count(),
                'available': Product.query.filter_by(is_available=True).count(),
                'on_sale': Product.query.filter(Product.original_price.isnot(None)).count(),
                'average_price': float(db.session.query(func.avg(Product.price)).scalar() or 0)
            },
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'verified': User.query.filter_by(is_verified=True).count()
            },
            'interactions': {
                'total': UserInteraction.query.count(),
                'purchases': UserInteraction.query.filter_by(interaction_type='purchase').count(),
                'views': UserInteraction.query.filter_by(interaction_type='view').count(),
                'cart_adds': UserInteraction.query.filter_by(interaction_type='cart_add').count()
            }
        }
        return {'status': 'success', 'data': stats_data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/products')
def get_products():
    """
    Get all products with advanced filtering and pagination
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - category: Filter by category
        - search: Search in product name and description
        - price_min: Minimum price (INR)
        - price_max: Maximum price (INR)
        - brands: Comma-separated brand names (e.g., "Realme,Samsung")
        - min_rating: Minimum average rating (0-5)
        - in_stock: Filter by stock availability (true/false)
        - sort_by: Sort field (price_asc, price_desc, rating, newest, popular)
    """
    try:
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Filter parameters
        category = request.args.get('category')
        search = request.args.get('search')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        brands = request.args.get('brands')  # Comma-separated
        min_rating = request.args.get('min_rating', type=float)
        in_stock = request.args.get('in_stock')
        sort_by = request.args.get('sort_by', 'newest')
        
        # Build query
        query = Product.query
        
        # Category filter
        if category:
            query = query.filter_by(category=category)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.tags.ilike(search_term)
                )
            )
        
        # Price range filter
        if price_min is not None:
            query = query.filter(Product.price >= price_min)
        if price_max is not None:
            query = query.filter(Product.price <= price_max)
        
        # Brand filter (multi-select)
        if brands:
            brand_list = [b.strip() for b in brands.split(',')]
            query = query.filter(Product.brand.in_(brand_list))
        
        # Rating filter
        if min_rating is not None:
            query = query.filter(Product.average_rating >= min_rating)
        
        # Stock filter
        if in_stock is not None:
            is_in_stock = in_stock.lower() == 'true'
            if is_in_stock:
                query = query.filter(Product.is_available == True, Product.stock_quantity > 0)
            else:
                query = query.filter(db.or_(Product.is_available == False, Product.stock_quantity == 0))
        
        # Sorting
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'rating':
            query = query.order_by(Product.average_rating.desc(), Product.review_count.desc())
        elif sort_by == 'popular':
            # Sort by review count as proxy for popularity
            query = query.order_by(Product.review_count.desc())
        elif sort_by == 'newest':
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.id.desc())
        
        # Paginate results
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'status': 'success',
            'data': [p.to_dict() for p in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages
            }
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/products/filters')
def get_filter_options():
    """Get available filter options for products"""
    try:
        # Get all unique brands with product count
        brands_query = db.session.query(
            Product.brand,
            db.func.count(Product.id).label('count')
        ).filter(
            Product.brand.isnot(None)
        ).group_by(Product.brand).order_by(db.text('count DESC')).all()
        
        brands = [{'name': brand, 'count': count} for brand, count in brands_query]
        
        # Get price range
        price_stats = db.session.query(
            db.func.min(Product.price).label('min_price'),
            db.func.max(Product.price).label('max_price')
        ).first()
        
        # Get all categories with product count
        categories_query = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category).order_by(db.text('count DESC')).all()
        
        categories = [{'name': category, 'count': count} for category, count in categories_query]
        
        # Get rating distribution
        rating_dist = {
            '4+': Product.query.filter(Product.average_rating >= 4.0).count(),
            '3+': Product.query.filter(Product.average_rating >= 3.0).count(),
            '2+': Product.query.filter(Product.average_rating >= 2.0).count(),
        }
        
        return {
            'status': 'success',
            'data': {
                'brands': brands,
                'price_range': {
                    'min': float(price_stats.min_price) if price_stats.min_price else 0,
                    'max': float(price_stats.max_price) if price_stats.max_price else 100000
                },
                'categories': categories,
                'rating_distribution': rating_dist,
                'total_products': Product.query.count()
            }
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get a specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        return {'status': 'success', 'data': product.to_dict()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 404


@app.route('/api/products/<int:product_id>/similar')
def get_similar_products(product_id):
    """Get products similar to the specified product using content-based filtering"""
    try:
        # Get the target product
        target_product = Product.query.get_or_404(product_id)
        
        # Get all other products
        all_products = Product.query.filter(
            Product.id != product_id,
            Product.is_available == True
        ).all()
        
        if not all_products:
            return {'status': 'success', 'data': []}
        
        # Calculate similarity scores
        similar_products = []
        for product in all_products:
            score = calculate_similarity_score(target_product, product)
            if score > 0.1:  # Minimum similarity threshold
                similar_products.append({
                    'product': product.to_dict(),
                    'similarity_score': round(score, 3)
                })
        
        # Sort by similarity score (highest first) and limit to top 6
        similar_products.sort(key=lambda x: x['similarity_score'], reverse=True)
        result = [item['product'] for item in similar_products[:6]]
        
        return {'status': 'success', 'data': result}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


def calculate_similarity_score(product1, product2):
    """Calculate similarity score between two products using multiple factors"""
    score = 0.0
    
    # Category similarity (40% weight)
    if product1.category == product2.category:
        score += 0.4
        # Bonus for same subcategory
        if product1.subcategory == product2.subcategory:
            score += 0.1
    
    # Brand similarity (20% weight)
    if product1.brand and product2.brand and product1.brand == product2.brand:
        score += 0.2
    
    # Price similarity (20% weight) - closer prices get higher scores
    if product1.price and product2.price:
        price_diff = abs(product1.price - product2.price)
        max_price = max(product1.price, product2.price)
        if max_price > 0:
            price_similarity = 1 - (price_diff / max_price)
            # Only give points if prices are reasonably close (within 50% difference)
            if price_similarity > 0.5:
                score += 0.2 * price_similarity
    
    # Rating similarity (10% weight) - products with similar ratings
    if product1.average_rating and product2.average_rating:
        rating_diff = abs(product1.average_rating - product2.average_rating)
        rating_similarity = 1 - (rating_diff / 5.0)  # Rating is out of 5
        score += 0.1 * rating_similarity
    
    # Tag similarity (10% weight)
    if product1.tags and product2.tags:
        tags1 = set(tag.strip().lower() for tag in product1.tags.split(',') if tag.strip())
        tags2 = set(tag.strip().lower() for tag in product2.tags.split(',') if tag.strip())
        
        if tags1 and tags2:
            intersection = len(tags1.intersection(tags2))
            union = len(tags1.union(tags2))
            if union > 0:
                jaccard_similarity = intersection / union
                score += 0.1 * jaccard_similarity
    
    return min(score, 1.0)  # Cap at 1.0


@app.route('/api/products/<int:product_id>/frequently-bought')
def get_frequently_bought_together(product_id):
    """Get products frequently bought together with the specified product"""
    try:
        # Get the target product
        target_product = Product.query.get_or_404(product_id)
        
        # For now, we'll use a simplified approach since we don't have purchase data
        # We'll recommend products that are:
        # 1. In the same category but different subcategory (complementary items)
        # 2. Have similar price ranges (affordable combinations)
        # 3. Have good ratings (quality items)
        
        frequently_bought = Product.query.filter(
            Product.id != product_id,
            Product.is_available == True,
            Product.category == target_product.category,
            Product.subcategory != target_product.subcategory,  # Different subcategory for variety
            Product.average_rating >= 3.5,  # Good quality items
            Product.price <= target_product.price * 1.5,  # Within reasonable price range
            Product.price >= target_product.price * 0.3
        ).order_by(
            Product.average_rating.desc(),
            Product.review_count.desc()
        ).limit(4).all()
        
        # If no complementary items found, fallback to similar items in same subcategory
        if not frequently_bought:
            frequently_bought = Product.query.filter(
                Product.id != product_id,
                Product.is_available == True,
                Product.category == target_product.category,
                Product.average_rating >= 3.0,
                Product.price <= target_product.price * 2.0,
                Product.price >= target_product.price * 0.2
            ).order_by(
                Product.average_rating.desc(),
                Product.review_count.desc()
            ).limit(4).all()
        
        result = [product.to_dict() for product in frequently_bought]
        return {'status': 'success', 'data': result}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/products/trending')
def get_trending_products():
    """Get trending products, optionally filtered by city"""
    try:
        city = request.args.get('city', '').strip()
        limit = int(request.args.get('limit', 8))
        
        # Base query for trending products
        query = Product.query.filter(Product.is_available == True)
        
        # If city is provided, we could filter by popular products in that region
        # For now, we'll use a trending algorithm based on:
        # 1. High average rating (4.0+)
        # 2. Good number of reviews (popularity indicator)
        # 3. Recent products (created in last 6 months simulate trending)
        
        # Calculate a trending score: (rating * review_count) with recent boost
        from datetime import datetime, timedelta
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        trending_products = query.filter(
            Product.average_rating >= 3.5,
            Product.review_count >= 5
        ).all()
        
        # Calculate trending scores
        scored_products = []
        for product in trending_products:
            # Base score: rating * log(review_count) to prevent skew from very high review counts
            import math
            base_score = product.average_rating * math.log(max(product.review_count, 1))
            
            # Recency boost: newer products get up to 20% boost
            recency_boost = 1.0
            if product.created_at >= six_months_ago:
                days_old = (datetime.utcnow() - product.created_at).days
                recency_boost = 1.0 + (0.2 * (180 - days_old) / 180)
            
            final_score = base_score * recency_boost
            scored_products.append((product, final_score))
        
        # Sort by trending score and limit results
        scored_products.sort(key=lambda x: x[1], reverse=True)
        result = [product.to_dict() for product, score in scored_products[:limit]]
        
        response_data = {
            'products': result,
            'city': city if city else 'All Cities',
            'algorithm': 'rating_popularity_recency'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/products/budget-suggestions')
def get_budget_suggestions():
    """Get product suggestions based on budget constraints"""
    try:
        min_price = float(request.args.get('min_price', 0))
        max_price = float(request.args.get('max_price', 100000))
        category = request.args.get('category', '').strip()
        limit = int(request.args.get('limit', 8))
        
        # Build query for budget-friendly products
        query = Product.query.filter(
            Product.is_available == True,
            Product.price >= min_price,
            Product.price <= max_price,
            Product.average_rating >= 3.0  # Only suggest well-rated products
        )
        
        # Filter by category if provided
        if category:
            query = query.filter(Product.category == category)
        
        # Get products and calculate value scores
        products = query.all()
        scored_products = []
        
        for product in products:
            # Calculate value score: quality vs price ratio
            # Higher rating and lower price within budget = better value
            price_normalized = (product.price - min_price) / max(max_price - min_price, 1)
            rating_score = product.average_rating / 5.0
            review_boost = min(product.review_count / 50.0, 1.0)  # Up to 50 reviews for full boost
            
            # Value score: prioritize rating, penalize high price within budget
            value_score = (rating_score * 0.6 + review_boost * 0.2 + (1 - price_normalized) * 0.2)
            
            scored_products.append((product, value_score))
        
        # Sort by value score and limit results
        scored_products.sort(key=lambda x: x[1], reverse=True)
        result = [product.to_dict() for product, score in scored_products[:limit]]
        
        response_data = {
            'products': result,
            'budget_range': {'min': min_price, 'max': max_price},
            'category': category if category else 'All Categories',
            'algorithm': 'value_based_scoring'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


# AI Enhancement Endpoints

@app.route('/api/products/<int:product_id>/ai-description')
def get_ai_product_description(product_id):
    """Generate AI-enhanced product description using Gemini"""
    try:
        # Get the product
        product = Product.query.get_or_404(product_id)
        
        # Check if we want to regenerate or use cached
        regenerate = request.args.get('regenerate', 'false').lower() == 'true'
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Create product context for AI
        product_context = {
            'name': product.name,
            'category': product.category,
            'subcategory': product.subcategory,
            'brand': product.brand,
            'price': product.price,
            'original_price': product.original_price,
            'currency': product.currency,
            'rating': product.average_rating,
            'review_count': product.review_count,
            'tags': product.tags,
            'features': product.features,
            'current_description': product.description
        }
        
        # Generate AI description
        ai_description = gemini_service.generate_product_description(
            product_context, 
            target_market='Indian'
        )
        
        response_data = {
            'product_id': product_id,
            'original_description': product.description,
            'ai_description': ai_description,
            'enhanced_by': 'Gemini AI',
            'target_market': 'Indian consumers'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': f'AI description generation failed: {str(e)}'}, 500


@app.route('/api/products/<int:product_id>/sentiment')
def get_review_sentiment(product_id):
    """Analyze review sentiment using Gemini AI"""
    try:
        # Get the product
        product = Product.query.get_or_404(product_id)
        
        # For demo purposes, we'll create sample reviews
        # In a real app, you'd have a reviews table
        sample_reviews = [
            "This product is amazing! Great quality and fast delivery. Highly recommended for Indian families.",
            "Good value for money. Works well but could be better. Decent purchase overall.",
            "Excellent product! Love the design and functionality. Perfect for my needs.",
            "Not satisfied with the quality. Expected better for this price. Customer service was poor.",
            "Outstanding! Best purchase I've made this year. Will definitely buy again."
        ]
        
        # Initialize Gemini service  
        gemini_service = GeminiService()
        
        # Analyze sentiment
        sentiment_analysis = gemini_service.analyze_sentiment(
            reviews=sample_reviews,
            product_name=product.name,
            product_category=product.category
        )
        
        response_data = {
            'product_id': product_id,
            'product_name': product.name,
            'total_reviews_analyzed': len(sample_reviews),
            'sentiment_analysis': sentiment_analysis,
            'analyzed_by': 'Gemini AI'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': f'Sentiment analysis failed: {str(e)}'}, 500


@app.route('/api/chat/product', methods=['POST'])
def product_chat():
    """Smart product Q&A using Gemini AI"""
    try:
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        question = data.get('question', '').strip()
        product_id = data.get('product_id')
        
        if not question:
            return {'status': 'error', 'message': 'Question is required'}, 400
        
        # Get product context if product_id provided
        product_context = None
        if product_id:
            product = Product.query.get(product_id)
            if product:
                product_context = {
                    'name': product.name,
                    'category': product.category,
                    'brand': product.brand,
                    'price': product.price,
                    'description': product.description,
                    'features': product.features,
                    'rating': product.average_rating
                }
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Get AI answer
        ai_answer = gemini_service.answer_product_question(
            question=question,
            product_context=product_context
        )
        
        response_data = {
            'question': question,
            'answer': ai_answer,
            'product_id': product_id,
            'answered_by': 'Gemini AI Assistant',
            'context': 'Indian e-commerce'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': f'Chat failed: {str(e)}'}, 500


@app.route('/api/chat/general', methods=['POST'])
def general_chat():
    """General shopping assistant using Gemini AI"""
    try:
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', None)
        
        if not message:
            return {'status': 'error', 'message': 'Message is required'}, 400
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Get AI response for general shopping assistance
        ai_response = gemini_service.general_shopping_assistant(
            message=message,
            conversation_id=conversation_id
        )
        
        response_data = {
            'message': message,
            'response': ai_response,
            'conversation_id': conversation_id,
            'assistant': 'AI Shopping Assistant',
            'context': 'Indian e-commerce platform'
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': f'General chat failed: {str(e)}'}, 500


@app.route('/api/search/natural', methods=['POST'])
def natural_language_search():
    """Natural language product search using Gemini AI"""
    try:
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        query = data.get('query', '').strip()
        limit = int(data.get('limit', 12))
        
        if not query:
            return {'status': 'error', 'message': 'Search query is required'}, 400
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Parse natural language query into search parameters
        search_params = gemini_service.parse_natural_search(query)
        
        # Build database query based on AI-parsed parameters
        base_query = Product.query.filter(Product.is_available == True)
        
        # Apply AI-suggested filters
        if search_params.get('category'):
            base_query = base_query.filter(Product.category.ilike(f"%{search_params['category']}%"))
        
        if search_params.get('min_price'):
            base_query = base_query.filter(Product.price >= search_params['min_price'])
        
        if search_params.get('max_price'):
            base_query = base_query.filter(Product.price <= search_params['max_price'])
        
        if search_params.get('brand'):
            base_query = base_query.filter(Product.brand.ilike(f"%{search_params['brand']}%"))
        
        if search_params.get('keywords'):
            for keyword in search_params['keywords']:
                base_query = base_query.filter(
                    db.or_(
                        Product.name.ilike(f"%{keyword}%"),
                        Product.description.ilike(f"%{keyword}%"),
                        Product.tags.ilike(f"%{keyword}%")
                    )
                )
        
        # Apply sorting
        sort_by = search_params.get('sort_by', 'popular')
        if sort_by == 'price_asc':
            base_query = base_query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            base_query = base_query.order_by(Product.price.desc())
        elif sort_by == 'rating':
            base_query = base_query.order_by(Product.average_rating.desc())
        else:  # popular
            base_query = base_query.order_by(Product.review_count.desc())
        
        # Get results
        products = base_query.limit(limit).all()
        product_list = [product.to_dict() for product in products]
        
        response_data = {
            'original_query': query,
            'parsed_intent': search_params,
            'products': product_list,
            'total_found': len(product_list),
            'ai_interpretation': search_params.get('interpretation', 'Standard product search')
        }
        
        return {'status': 'success', 'data': response_data}
    except Exception as e:
        return {'status': 'error', 'message': f'Natural search failed: {str(e)}'}, 500


@app.route('/api/users')
def get_users():
    """Get all users with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'status': 'success',
            'data': [u.to_dict() for u in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        return {'status': 'success', 'data': user.to_dict()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 404


# Recommendation Endpoints

@app.route('/api/recommend/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get personalized recommendations with AI-powered explanations for a user
    
    Query Parameters:
        - limit: Number of recommendations (default: 5, max: 20)
        - strategy: Recommendation strategy ('auto', 'hybrid', 'collaborative', 'content')
        - explain: Include AI explanations (default: true)
    
    Example: /api/recommend/1?limit=5&strategy=auto&explain=true
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 5)), 20)
        strategy = request.args.get('strategy', 'auto')
        include_explanations = request.args.get('explain', 'true').lower() == 'true'
        
        # Validate strategy
        valid_strategies = ['auto', 'hybrid', 'collaborative', 'content']
        if strategy not in valid_strategies:
            return jsonify({
                'status': 'error',
                'message': f'Invalid strategy. Must be one of: {", ".join(valid_strategies)}'
            }), 400
        
        # Get recommendations
        rec_service = RecommendationService()
        result = rec_service.get_recommendations_with_explanations(
            user_id=user_id,
            limit=limit,
            strategy=strategy,
            include_explanations=include_explanations
        )
        
        if result['success']:
            return jsonify({'status': 'success', 'data': result})
        else:
            return jsonify({'status': 'error', 'message': result.get('error')}), 404
            
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def get_recommendations_post():
    """
    Get personalized recommendations (POST version for complex requests)
    
    Request Body:
        {
            "user_id": 1,
            "limit": 5,
            "strategy": "auto",
            "include_explanations": true
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'user_id is required in request body'
            }), 400
        
        user_id = data['user_id']
        limit = min(data.get('limit', 5), 20)
        strategy = data.get('strategy', 'auto')
        include_explanations = data.get('include_explanations', True)
        
        # Get recommendations
        rec_service = RecommendationService()
        result = rec_service.get_recommendations_with_explanations(
            user_id=user_id,
            limit=limit,
            strategy=strategy,
            include_explanations=include_explanations
        )
        
        if result['success']:
            return jsonify({'status': 'success', 'data': result})
        else:
            return jsonify({'status': 'error', 'message': result.get('error')}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/gemini/test', methods=['GET'])
def test_gemini():
    """
    Test Gemini API connection
    
    Returns status of Gemini integration
    """
    try:
        rec_service = RecommendationService()
        result = rec_service.test_gemini_connection()
        
        status_code = 200 if result['success'] else 503
        return jsonify({'status': 'success' if result['success'] else 'error', 'data': result}), status_code
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'data': {'available': False}
        }), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
