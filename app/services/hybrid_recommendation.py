"""
Hybrid Recommendation Service
Combines collaborative and content-based filtering for optimal recommendations
"""
from app.services.collaborative_filtering import CollaborativeFilteringService
from app.services.content_based_filtering import ContentBasedFilteringService
from app.models import User, Product
from collections import defaultdict


class HybridRecommendationService:
    """
    Hybrid recommendation system that combines multiple approaches
    """
    
    def __init__(self, collaborative_weight=0.6, content_weight=0.4):
        """
        Initialize hybrid recommendation service
        
        Args:
            collaborative_weight: Weight for collaborative filtering (0-1)
            content_weight: Weight for content-based filtering (0-1)
        """
        self.collaborative_service = CollaborativeFilteringService()
        self.content_service = ContentBasedFilteringService()
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
    
    def recommend_products(self, user_id, limit=5, exclude_interacted=True, strategy='hybrid'):
        """
        Get hybrid recommendations combining multiple approaches
        
        Args:
            user_id: Target user ID
            limit: Maximum number of recommendations
            exclude_interacted: Whether to exclude already interacted products
            strategy: 'hybrid', 'collaborative', 'content', or 'auto'
            
        Returns:
            List of (product, score, reason) tuples
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Determine strategy automatically if needed
        if strategy == 'auto':
            strategy = self._determine_best_strategy(user_id)
        
        if strategy == 'collaborative':
            return self.collaborative_service.recommend_products(user_id, limit, exclude_interacted)
        elif strategy == 'content':
            return self.content_service.recommend_products(user_id, limit, exclude_interacted)
        else:  # hybrid
            return self._hybrid_recommend(user_id, limit, exclude_interacted)
    
    def _hybrid_recommend(self, user_id, limit, exclude_interacted):
        """
        Combine collaborative and content-based recommendations
        
        Args:
            user_id: Target user ID
            limit: Maximum recommendations
            exclude_interacted: Exclude interacted products
            
        Returns:
            List of (product, score, reason) tuples
        """
        # Get recommendations from both methods
        collab_recs = self.collaborative_service.recommend_products(
            user_id, limit=limit*2, exclude_interacted=exclude_interacted
        )
        content_recs = self.content_service.recommend_products(
            user_id, limit=limit*2, exclude_interacted=exclude_interacted
        )
        
        # Normalize scores to 0-100 range
        collab_scores = self._normalize_scores([(p, s, r) for p, s, r in collab_recs])
        content_scores = self._normalize_scores([(p, s, r) for p, s, r in content_recs])
        
        # Combine scores
        combined_scores = defaultdict(lambda: {'score': 0, 'reasons': []})
        
        for product, score, reason in collab_scores:
            combined_scores[product.id]['score'] += score * self.collaborative_weight
            combined_scores[product.id]['product'] = product
            combined_scores[product.id]['reasons'].append({
                'method': 'collaborative',
                'score': round(score, 2),
                **reason
            })
        
        for product, score, reason in content_scores:
            combined_scores[product.id]['score'] += score * self.content_weight
            combined_scores[product.id]['product'] = product
            combined_scores[product.id]['reasons'].append({
                'method': 'content_based',
                'score': round(score, 2),
                **reason
            })
        
        # Sort by combined score
        sorted_recommendations = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Format recommendations
        recommendations = []
        for product_id, data in sorted_recommendations[:limit]:
            product = data['product']
            score = data['score']
            
            # Create combined reason
            reason = {
                'type': 'hybrid',
                'combined_score': round(score, 2),
                'collaborative_weight': self.collaborative_weight,
                'content_weight': self.content_weight,
                'methods_used': [r['method'] for r in data['reasons']],
                'details': data['reasons']
            }
            
            recommendations.append((product, score, reason))
        
        return recommendations
    
    def _normalize_scores(self, recommendations):
        """
        Normalize scores to 0-100 range
        
        Args:
            recommendations: List of (product, score, reason) tuples
            
        Returns:
            List with normalized scores
        """
        if not recommendations:
            return []
        
        scores = [score for _, score, _ in recommendations]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [(p, 50, r) for p, _, r in recommendations]
        
        normalized = []
        for product, score, reason in recommendations:
            normalized_score = ((score - min_score) / (max_score - min_score)) * 100
            normalized.append((product, normalized_score, reason))
        
        return normalized
    
    def _determine_best_strategy(self, user_id):
        """
        Automatically determine the best recommendation strategy for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Strategy name ('collaborative', 'content', or 'hybrid')
        """
        from app.models import UserInteraction
        
        # Count user's interactions
        interaction_count = UserInteraction.query.filter_by(user_id=user_id).count()
        
        # Find if there are similar users
        similar_users = self.collaborative_service.find_similar_users(user_id, limit=1)
        
        # Decision logic
        if interaction_count < 3:
            # New user: use content-based
            return 'content'
        elif not similar_users:
            # No similar users: use content-based
            return 'content'
        elif interaction_count < 10:
            # Some interactions but not many: prefer content
            return 'hybrid'  # But lean more on content
        else:
            # Experienced user with similar users: use hybrid
            return 'hybrid'
    
    def get_recommendations_with_diversity(self, user_id, limit=10, diversity_factor=0.3):
        """
        Get diverse recommendations across categories
        
        Args:
            user_id: User ID
            limit: Number of recommendations
            diversity_factor: 0-1, higher means more category diversity
            
        Returns:
            List of diverse recommendations
        """
        # Get more recommendations than needed
        recommendations = self.recommend_products(user_id, limit=limit*3, strategy='hybrid')
        
        # Group by category
        category_recs = defaultdict(list)
        for rec in recommendations:
            product, score, reason = rec
            category_recs[product.category].append(rec)
        
        # Select diverse recommendations
        diverse_recs = []
        categories = list(category_recs.keys())
        
        # Calculate items per category
        if diversity_factor > 0 and len(categories) > 1:
            items_per_category = max(1, int(limit * diversity_factor / len(categories)))
        else:
            items_per_category = limit
        
        # Round-robin selection from categories
        category_index = 0
        while len(diverse_recs) < limit and any(category_recs.values()):
            category = categories[category_index % len(categories)]
            
            if category_recs[category]:
                diverse_recs.append(category_recs[category].pop(0))
            
            category_index += 1
            
            # Remove empty categories
            if not category_recs[category]:
                categories.remove(category)
                if not categories:
                    break
        
        return diverse_recs[:limit]
    
    def get_explanation_context(self, user_id, recommendations):
        """
        Get comprehensive context for LLM explanation
        
        Args:
            user_id: User ID
            recommendations: List of recommendations
            
        Returns:
            Dictionary with context information
        """
        user = User.query.get(user_id)
        
        # Get context from both services
        similar_users = self.collaborative_service.find_similar_users(user_id)
        collab_context = self.collaborative_service.get_explanation_context(user_id, similar_users)
        
        preferences = self.content_service.extract_user_preferences(user_id)
        content_context = self.content_service.get_explanation_context(user_id, preferences)
        
        # Extract recommendation details
        recommended_products = []
        for product, score, reason in recommendations[:5]:  # Top 5
            recommended_products.append({
                'name': product.name,
                'category': product.category,
                'brand': product.brand,
                'price': product.price,
                'rating': product.average_rating,
                'score': round(score, 2),
                'reason_type': reason.get('type', 'unknown')
            })
        
        return {
            'user': collab_context['user'],
            'collaborative_context': {
                'similar_users_count': collab_context['similar_users_count'],
                'avg_similarity': collab_context.get('similar_users_avg_similarity', 0)
            },
            'content_context': content_context['preferences'],
            'recommendations': recommended_products,
            'strategy': 'hybrid',
            'weights': {
                'collaborative': self.collaborative_weight,
                'content': self.content_weight
            }
        }
