"""
Recommendation Service with LLM Explanations
High-level service that combines recommendations with Gemini-powered explanations
"""
from typing import List, Dict, Any, Optional
from app.services.hybrid_recommendation import HybridRecommendationService
from app.services.gemini_service import get_gemini_service
from app.models import User


class RecommendationService:
    """
    High-level recommendation service with LLM-powered explanations
    Combines recommendation engine with Gemini for natural language explanations
    """
    
    def __init__(self):
        """Initialize recommendation service"""
        self.recommender = HybridRecommendationService()
        try:
            self.gemini = get_gemini_service()
            self.gemini_available = True
        except ValueError as e:
            print(f"Warning: Gemini not available - {str(e)}")
            self.gemini_available = False
    
    def get_recommendations_with_explanations(
        self,
        user_id: int,
        limit: int = 5,
        strategy: str = 'auto',
        include_explanations: bool = True
    ) -> Dict[str, Any]:
        """
        Get recommendations with AI-powered explanations
        
        Args:
            user_id: User ID
            limit: Number of recommendations
            strategy: Recommendation strategy ('auto', 'hybrid', 'collaborative', 'content')
            include_explanations: Whether to generate LLM explanations
            
        Returns:
            Dictionary with recommendations and metadata
        """
        # Get user
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Get recommendations
        recommendations = self.recommender.recommend_products(
            user_id=user_id,
            limit=limit,
            strategy=strategy
        )
        
        if not recommendations:
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'recommendations': [],
                'message': 'No recommendations available at this time. Try interacting with more products!'
            }
        
        # Get context for explanations
        context = self.recommender.get_explanation_context(user_id, recommendations)
        
        # Format recommendations
        results = []
        for product, score, reason in recommendations:
            product_dict = product.to_dict()
            
            # Generate explanation if requested and available
            explanation = None
            if include_explanations and self.gemini_available:
                try:
                    explanation = self.gemini.explain_recommendation(
                        product_dict,
                        context,
                        reason
                    )
                    # If Gemini returns None (rate limit or error), use fallback
                    if explanation is None:
                        explanation = self._generate_fallback_explanation(
                            product_dict,
                            reason
                        )
                except Exception as e:
                    print(f"Error generating explanation: {str(e)}")
                    explanation = self._generate_fallback_explanation(
                        product_dict,
                        reason
                    )
            else:
                explanation = self._generate_fallback_explanation(
                    product_dict,
                    reason
                )
            
            results.append({
                'product': product_dict,
                'score': round(score, 2),
                'recommendation_reason': reason,
                'explanation': explanation
            })
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'total_purchases': user.total_purchases
            },
            'strategy_used': strategy,
            'recommendations': results,
            'count': len(results),
            'gemini_enabled': self.gemini_available
        }
    
    def _generate_fallback_explanation(
        self,
        product: Dict[str, Any],
        reason: Dict[str, Any]
    ) -> str:
        """
        Generate a simple fallback explanation without LLM
        
        Args:
            product: Product dictionary
            reason: Recommendation reason
            
        Returns:
            Simple explanation text
        """
        reason_type = reason.get('type', 'unknown')
        
        if reason_type == 'collaborative':
            recommenders = reason.get('recommenders_count', 0)
            return (
                f"We recommend {product['name']} because {recommenders} users "
                f"with similar taste also liked this product. "
                f"It's in the {product['category']} category and has a {product['average_rating']:.1f} star rating."
            )
        elif reason_type == 'content_based':
            matched_category = reason.get('matched_category', False)
            matched_brand = reason.get('matched_brand', False)
            parts = [f"We recommend {product['name']}"]
            
            if matched_category:
                parts.append(f"because it matches your interest in {product['category']}")
            if matched_brand:
                parts.append(f"and it's from {product['brand']}, a brand you like")
            
            return ' '.join(parts) + '.'
        elif reason_type == 'hybrid':
            return (
                f"We recommend {product['name']} based on both your personal preferences "
                f"and what similar users enjoyed. It's highly rated ({product['average_rating']:.1f} stars) "
                f"and fits your style perfectly."
            )
        else:
            return (
                f"We think you'll love {product['name']}! "
                f"It's a popular choice in the {product['category']} category."
            )
    
    def get_similar_products_with_explanations(
        self,
        product_id: int,
        limit: int = 5,
        include_explanations: bool = True
    ) -> Dict[str, Any]:
        """
        Get similar products with explanations
        
        Args:
            product_id: Source product ID
            limit: Number of similar products
            include_explanations: Whether to generate explanations
            
        Returns:
            Dictionary with similar products
        """
        from app.models import Product
        from app.services import ContentBasedFilteringService
        
        # Get source product
        source_product = Product.query.get(product_id)
        if not source_product:
            return {
                'success': False,
                'error': 'Product not found'
            }
        
        # Get similar products
        cb_service = ContentBasedFilteringService()
        similar = cb_service.find_similar_products(product_id, limit)
        
        if not similar:
            return {
                'success': True,
                'source_product': source_product.to_dict(),
                'similar_products': [],
                'message': 'No similar products found'
            }
        
        # Format results
        results = []
        for product, score, reason in similar:
            product_dict = product.to_dict()
            
            # Generate explanation
            explanation = None
            if include_explanations and self.gemini_available:
                try:
                    prompt = f"""Explain in 1-2 sentences why {product.name} is similar to {source_product.name}.
                    
Both are in {product.category} category.
Same brand: {reason['same_brand']}
Price similarity: {reason['price_similarity']}%

Be brief and friendly:"""
                    explanation = self.gemini.generate_content(prompt)
                except Exception as e:
                    explanation = f"Similar to {source_product.name} - same category and comparable features."
            else:
                explanation = f"Similar to {source_product.name} - same category and comparable features."
            
            results.append({
                'product': product_dict,
                'similarity_score': round(score, 2),
                'reason': reason,
                'explanation': explanation
            })
        
        return {
            'success': True,
            'source_product': source_product.to_dict(),
            'similar_products': results,
            'count': len(results)
        }
    
    def test_gemini_connection(self) -> Dict[str, Any]:
        """
        Test Gemini API connection
        
        Returns:
            Status dictionary
        """
        if not self.gemini_available:
            return {
                'success': False,
                'message': 'Gemini API key not configured',
                'available': False
            }
        
        try:
            is_working = self.gemini.test_connection()
            return {
                'success': is_working,
                'message': 'Gemini API is working!' if is_working else 'Connection failed',
                'available': is_working
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'available': False
            }
