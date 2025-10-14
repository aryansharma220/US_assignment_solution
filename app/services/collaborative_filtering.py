"""
Collaborative Filtering Service
Implements user-based collaborative filtering for product recommendations
"""
from sqlalchemy import func, and_
from app import db
from app.models import User, Product, UserInteraction
import numpy as np
from collections import defaultdict


class CollaborativeFilteringService:
    """
    User-based collaborative filtering recommendation service
    Finds similar users based on interaction patterns and recommends products they liked
    """
    
    def __init__(self, min_common_interactions=2):
        """
        Initialize collaborative filtering service
        
        Args:
            min_common_interactions: Minimum number of common interactions to consider users similar
        """
        self.min_common_interactions = min_common_interactions
    
    def get_user_interaction_matrix(self, user_id):
        """
        Get user's interaction history as a weighted dictionary
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of {product_id: weighted_score}
        """
        interactions = UserInteraction.query.filter_by(user_id=user_id).all()
        
        interaction_scores = defaultdict(float)
        for interaction in interactions:
            weight = UserInteraction.get_interaction_weight(interaction.interaction_type)
            interaction_scores[interaction.product_id] += weight
            
            # Boost score if there's a rating
            if interaction.rating:
                interaction_scores[interaction.product_id] += interaction.rating
        
        return dict(interaction_scores)
    
    def find_similar_users(self, user_id, limit=10):
        """
        Find users with similar interaction patterns
        
        Args:
            user_id: Target user ID
            limit: Maximum number of similar users to return
            
        Returns:
            List of (user_id, similarity_score) tuples
        """
        # Get target user's interactions
        target_interactions = self.get_user_interaction_matrix(user_id)
        target_products = set(target_interactions.keys())
        
        if not target_products:
            return []
        
        # Find users who interacted with the same products
        similar_users = db.session.query(
            UserInteraction.user_id,
            func.count(UserInteraction.product_id).label('common_count')
        ).filter(
            and_(
                UserInteraction.product_id.in_(target_products),
                UserInteraction.user_id != user_id
            )
        ).group_by(
            UserInteraction.user_id
        ).having(
            func.count(UserInteraction.product_id) >= self.min_common_interactions
        ).all()
        
        # Calculate similarity scores
        user_similarities = []
        for other_user_id, common_count in similar_users:
            other_interactions = self.get_user_interaction_matrix(other_user_id)
            other_products = set(other_interactions.keys())
            
            # Calculate Jaccard similarity
            intersection = len(target_products & other_products)
            union = len(target_products | other_products)
            jaccard_similarity = intersection / union if union > 0 else 0
            
            # Calculate weighted cosine similarity for common products
            common_products = target_products & other_products
            if common_products:
                target_vector = [target_interactions[p] for p in common_products]
                other_vector = [other_interactions[p] for p in common_products]
                
                dot_product = sum(t * o for t, o in zip(target_vector, other_vector))
                target_norm = sum(t ** 2 for t in target_vector) ** 0.5
                other_norm = sum(o ** 2 for o in other_vector) ** 0.5
                
                cosine_similarity = dot_product / (target_norm * other_norm) if target_norm > 0 and other_norm > 0 else 0
            else:
                cosine_similarity = 0
            
            # Combined similarity score (weighted average)
            combined_similarity = (0.4 * jaccard_similarity) + (0.6 * cosine_similarity)
            
            user_similarities.append((other_user_id, combined_similarity))
        
        # Sort by similarity and return top matches
        user_similarities.sort(key=lambda x: x[1], reverse=True)
        return user_similarities[:limit]
    
    def recommend_products(self, user_id, limit=5, exclude_interacted=True):
        """
        Recommend products based on similar users' preferences
        
        Args:
            user_id: Target user ID
            limit: Maximum number of recommendations
            exclude_interacted: Whether to exclude products user already interacted with
            
        Returns:
            List of (product, score, reason) tuples
        """
        # Get similar users
        similar_users = self.find_similar_users(user_id, limit=10)
        
        if not similar_users:
            # Fallback to popular products if no similar users found
            return self._get_popular_products(limit)
        
        # Get target user's interactions to exclude
        target_user_products = set()
        if exclude_interacted:
            target_interactions = UserInteraction.query.filter_by(user_id=user_id).all()
            target_user_products = {i.product_id for i in target_interactions}
        
        # Aggregate recommendations from similar users
        product_scores = defaultdict(float)
        product_recommenders = defaultdict(list)
        
        for similar_user_id, similarity_score in similar_users:
            similar_user_interactions = self.get_user_interaction_matrix(similar_user_id)
            
            for product_id, interaction_score in similar_user_interactions.items():
                if product_id not in target_user_products:
                    # Weight the score by user similarity
                    weighted_score = interaction_score * similarity_score
                    product_scores[product_id] += weighted_score
                    product_recommenders[product_id].append((similar_user_id, similarity_score))
        
        # Sort products by score
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get product details and create recommendations
        recommendations = []
        for product_id, score in sorted_products[:limit]:
            product = Product.query.get(product_id)
            if product and product.is_available:
                # Count how many similar users recommended this
                num_recommenders = len(product_recommenders[product_id])
                avg_similarity = sum(s for _, s in product_recommenders[product_id]) / num_recommenders
                
                reason = {
                    'type': 'collaborative',
                    'score': round(score, 2),
                    'similar_users_count': len(similar_users),
                    'recommenders_count': num_recommenders,
                    'avg_recommender_similarity': round(avg_similarity, 2)
                }
                
                recommendations.append((product, score, reason))
        
        return recommendations
    
    def _get_popular_products(self, limit=5):
        """
        Fallback: Get most popular products based on interactions
        
        Args:
            limit: Maximum number of products
            
        Returns:
            List of (product, score, reason) tuples
        """
        popular = db.session.query(
            Product,
            func.count(UserInteraction.id).label('interaction_count'),
            func.avg(UserInteraction.rating).label('avg_rating')
        ).join(
            UserInteraction
        ).filter(
            Product.is_available == True
        ).group_by(
            Product.id
        ).order_by(
            db.desc('interaction_count')
        ).limit(limit).all()
        
        recommendations = []
        for product, count, avg_rating in popular:
            reason = {
                'type': 'popular_fallback',
                'interaction_count': count,
                'avg_rating': round(float(avg_rating) if avg_rating else 0, 1)
            }
            score = count + (float(avg_rating) if avg_rating else 0) * 2
            recommendations.append((product, score, reason))
        
        return recommendations
    
    def get_explanation_context(self, user_id, similar_users):
        """
        Get context for LLM explanation generation
        
        Args:
            user_id: Target user ID
            similar_users: List of (user_id, similarity_score) tuples
            
        Returns:
            Dictionary with context information
        """
        user = User.query.get(user_id)
        
        # Get user's interaction patterns
        interactions = UserInteraction.query.filter_by(user_id=user_id).all()
        interaction_summary = defaultdict(int)
        for i in interactions:
            interaction_summary[i.interaction_type] += 1
        
        # Get similar users' demographics
        similar_user_ids = [uid for uid, _ in similar_users]
        similar_user_objects = User.query.filter(User.id.in_(similar_user_ids)).all()
        
        return {
            'user': {
                'username': user.username,
                'age': user.age,
                'location': user.location,
                'preferred_categories': user.preferred_category_list,
                'total_purchases': user.total_purchases
            },
            'interaction_summary': dict(interaction_summary),
            'similar_users_count': len(similar_users),
            'similar_users_avg_similarity': round(np.mean([s for _, s in similar_users]), 2) if similar_users else 0
        }
