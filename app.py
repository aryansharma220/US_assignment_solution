"""
Main application entry point for E-commerce Product Recommender
"""
from flask import request, jsonify, render_template
from app import create_app, db
from app.models import Product, User, UserInteraction
from app.services.recommendation_service import RecommendationService
from config import Config
from sqlalchemy import func

# Create Flask application
app = create_app()


# ============================================================================
# FRONTEND ROUTES
# ============================================================================

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


# ============================================================================
# API ROUTES
# ============================================================================

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
    """Get all products with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        category = request.args.get('category')
        
        query = Product.query
        if category:
            query = query.filter_by(category=category)
        
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


@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get a specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        return {'status': 'success', 'data': product.to_dict()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 404


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


# ============================================================================
# RECOMMENDATION ENDPOINTS WITH GEMINI LLM EXPLANATIONS
# ============================================================================

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


@app.route('/api/similar/<int:product_id>', methods=['GET'])
def get_similar_products(product_id):
    """
    Get similar products with explanations
    
    Query Parameters:
        - limit: Number of similar products (default: 5, max: 20)
        - explain: Include AI explanations (default: true)
    
    Example: /api/similar/1?limit=5&explain=true
    """
    try:
        limit = min(int(request.args.get('limit', 5)), 20)
        include_explanations = request.args.get('explain', 'true').lower() == 'true'
        
        # Get similar products
        rec_service = RecommendationService()
        result = rec_service.get_similar_products_with_explanations(
            product_id=product_id,
            limit=limit,
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
        # Create database tables
        db.create_all()
        print("✅ Database tables created successfully!")
    
    print(f"🚀 Starting E-commerce Product Recommender API...")
    print(f"📍 Running on http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    
    if not Config.GEMINI_API_KEY:
        print("⚠️  WARNING: Gemini API key not configured!")
        print("   Please set GEMINI_API_KEY in your .env file")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
