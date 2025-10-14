"""
Content-Based Filtering Service
Recommends products based on product features and user preferences
"""
from sqlalchemy import func, and_, or_
from app import db
from app.models import User, Product, UserInteraction
from collections import Counter
import re


class ContentBasedFilteringService:
    """
    Content-based recommendation service
    Analyzes product features and user preferences to make recommendations
    """
    
    def __init__(self):
        """Initialize content-based filtering service"""
        pass
    
    def extract_user_preferences(self, user_id):
        """
        Extract user preferences from their interaction history
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user preferences
        """
        user = User.query.get(user_id)
        
        # Get products user interacted with (weighted by interaction type)
        interactions = db.session.query(
            Product, UserInteraction
        ).join(
            UserInteraction, Product.id == UserInteraction.product_id
        ).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        # Aggregate preferences
        categories = Counter()
        subcategories = Counter()
        brands = Counter()
        price_points = []
        tags = Counter()
        
        for product, interaction in interactions:
            weight = UserInteraction.get_interaction_weight(interaction.interaction_type)
            
            # Weight positive interactions more
            if weight > 0:
                categories[product.category] += weight
                if product.subcategory:
                    subcategories[product.subcategory] += weight
                if product.brand:
                    brands[product.brand] += weight
                price_points.append(product.price)
                
                # Parse tags
                if product.tags:
                    for tag in product.tag_list:
                        tags[tag.lower()] += weight
        
        # Calculate price preferences
        avg_price = sum(price_points) / len(price_points) if price_points else 0
        min_price = min(price_points) if price_points else 0
        max_price = max(price_points) if price_points else float('inf')
        
        return {
            'preferred_categories': dict(categories.most_common(5)),
            'preferred_subcategories': dict(subcategories.most_common(5)),
            'preferred_brands': dict(brands.most_common(5)),
            'preferred_tags': dict(tags.most_common(10)),
            'price_range': {
                'min': min_price,
                'max': max_price,
                'avg': avg_price
            },
            'explicit_preferences': {
                'categories': user.preferred_category_list if user else [],
                'brands': user.preferred_brand_list if user else [],
                'price_min': user.price_range_min if user else None,
                'price_max': user.price_range_max if user else None
            }
        }
    
    def calculate_product_similarity(self, product, preferences):
        """
        Calculate how well a product matches user preferences
        
        Args:
            product: Product object
            preferences: User preferences dictionary
            
        Returns:
            Similarity score (0-100)
        """
        score = 0
        max_score = 0
        
        # Category match (weight: 30)
        max_score += 30
        if product.category in preferences['preferred_categories']:
            category_weight = preferences['preferred_categories'][product.category]
            score += min(category_weight * 3, 30)  # Cap at 30
        elif product.category in preferences['explicit_preferences']['categories']:
            score += 20
        
        # Subcategory match (weight: 15)
        max_score += 15
        if product.subcategory and product.subcategory in preferences['preferred_subcategories']:
            subcategory_weight = preferences['preferred_subcategories'][product.subcategory]
            score += min(subcategory_weight * 1.5, 15)
        
        # Brand match (weight: 20)
        max_score += 20
        if product.brand and product.brand in preferences['preferred_brands']:
            brand_weight = preferences['preferred_brands'][product.brand]
            score += min(brand_weight * 2, 20)
        elif product.brand and product.brand in preferences['explicit_preferences']['brands']:
            score += 15
        
        # Price match (weight: 15)
        max_score += 15
        price_range = preferences['price_range']
        if price_range['min'] <= product.price <= price_range['max']:
            # Calculate how close to average preferred price
            price_diff = abs(product.price - price_range['avg'])
            price_range_size = price_range['max'] - price_range['min']
            if price_range_size > 0:
                price_score = 15 * (1 - min(price_diff / price_range_size, 1))
                score += price_score
            else:
                score += 15
        
        # Tag match (weight: 10)
        max_score += 10
        if product.tags:
            product_tags = set(tag.lower() for tag in product.tag_list)
            preferred_tags = set(preferences['preferred_tags'].keys())
            tag_overlap = len(product_tags & preferred_tags)
            if tag_overlap > 0:
                score += min(tag_overlap * 3, 10)
        
        # Rating boost (weight: 10)
        max_score += 10
        if product.average_rating > 0:
            score += (product.average_rating / 5.0) * 10
        
        # Normalize score to 0-100
        normalized_score = (score / max_score) * 100 if max_score > 0 else 0
        
        return min(normalized_score, 100)
    
    def recommend_products(self, user_id, limit=5, exclude_interacted=True):
        """
        Recommend products based on content similarity
        
        Args:
            user_id: Target user ID
            limit: Maximum number of recommendations
            exclude_interacted: Whether to exclude products user already interacted with
            
        Returns:
            List of (product, score, reason) tuples
        """
        # Extract user preferences
        preferences = self.extract_user_preferences(user_id)
        
        # Get products to consider
        query = Product.query.filter_by(is_available=True)
        
        # Exclude already interacted products
        if exclude_interacted:
            interacted_product_ids = db.session.query(
                UserInteraction.product_id
            ).filter_by(user_id=user_id).distinct().all()
            interacted_ids = [pid[0] for pid in interacted_product_ids]
            if interacted_ids:
                query = query.filter(Product.id.notin_(interacted_ids))
        
        # Filter by preferred categories and price range
        preferred_categories = list(preferences['preferred_categories'].keys())
        if preferred_categories:
            # Include products from preferred categories or explicit preferences
            explicit_cats = preferences['explicit_preferences']['categories']
            all_categories = list(set(preferred_categories + explicit_cats))
            query = query.filter(Product.category.in_(all_categories))
        
        # Apply price range filter
        price_min = preferences['price_range']['min'] * 0.5  # 50% below min
        price_max = preferences['price_range']['max'] * 1.5  # 50% above max
        if price_max > 0:
            query = query.filter(and_(
                Product.price >= price_min,
                Product.price <= price_max
            ))
        
        products = query.all()
        
        # Calculate similarity scores
        product_scores = []
        for product in products:
            similarity_score = self.calculate_product_similarity(product, preferences)
            
            reason = {
                'type': 'content_based',
                'similarity_score': round(similarity_score, 2),
                'matched_category': product.category in preferences['preferred_categories'],
                'matched_brand': product.brand in preferences['preferred_brands'] if product.brand else False,
                'in_price_range': preferences['price_range']['min'] <= product.price <= preferences['price_range']['max'],
                'rating': product.average_rating
            }
            
            product_scores.append((product, similarity_score, reason))
        
        # Sort by similarity score
        product_scores.sort(key=lambda x: x[1], reverse=True)
        
        return product_scores[:limit]
    
    def get_explanation_context(self, user_id, preferences):
        """
        Get context for LLM explanation generation
        
        Args:
            user_id: Target user ID
            preferences: User preferences dictionary
            
        Returns:
            Dictionary with context information
        """
        user = User.query.get(user_id)
        
        top_categories = list(preferences['preferred_categories'].keys())[:3]
        top_brands = list(preferences['preferred_brands'].keys())[:3]
        
        return {
            'user': {
                'username': user.username,
                'age': user.age,
                'location': user.location
            },
            'preferences': {
                'top_categories': top_categories,
                'top_brands': top_brands,
                'price_range': preferences['price_range'],
                'favorite_tags': list(preferences['preferred_tags'].keys())[:5]
            }
        }
    
    def find_similar_products(self, product_id, limit=5):
        """
        Find products similar to a given product
        
        Args:
            product_id: Source product ID
            limit: Maximum number of similar products
            
        Returns:
            List of (product, similarity_score, reason) tuples
        """
        source_product = Product.query.get(product_id)
        if not source_product:
            return []
        
        # Find products with same category
        similar_products = Product.query.filter(
            and_(
                Product.id != product_id,
                Product.is_available == True,
                or_(
                    Product.category == source_product.category,
                    Product.brand == source_product.brand
                )
            )
        ).all()
        
        # Calculate similarity scores
        product_scores = []
        for product in similar_products:
            score = 0
            
            # Category match
            if product.category == source_product.category:
                score += 40
            
            # Subcategory match
            if product.subcategory == source_product.subcategory:
                score += 20
            
            # Brand match
            if product.brand and product.brand == source_product.brand:
                score += 25
            
            # Price similarity (within 30%)
            if source_product.price > 0:
                price_diff = abs(product.price - source_product.price) / source_product.price
                if price_diff < 0.3:
                    score += 15 * (1 - price_diff / 0.3)
            
            reason = {
                'type': 'similar_product',
                'same_category': product.category == source_product.category,
                'same_brand': product.brand == source_product.brand if product.brand else False,
                'price_similarity': round(100 - (price_diff * 100), 1) if source_product.price > 0 else 0
            }
            
            product_scores.append((product, score, reason))
        
        # Sort by similarity
        product_scores.sort(key=lambda x: x[1], reverse=True)
        
        return product_scores[:limit]
