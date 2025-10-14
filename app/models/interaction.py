"""
User Interaction Model - Tracks user behavior with products
"""
from datetime import datetime
from app import db


class UserInteraction(db.Model):
    """
    UserInteraction model representing user actions on products
    Types: view, purchase, cart_add, wishlist, rating, review
    """
    __tablename__ = 'user_interactions'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    
    # Interaction Details
    interaction_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: 'view', 'purchase', 'cart_add', 'cart_remove', 'wishlist_add', 
    #        'wishlist_remove', 'rating', 'review', 'search', 'click'
    
    # Interaction Metadata
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars (if applicable)
    review_text = db.Column(db.Text, nullable=True)  # Review content (if applicable)
    quantity = db.Column(db.Integer, default=1)  # For purchases or cart
    price_at_interaction = db.Column(db.Float, nullable=True)  # Price when interaction occurred
    
    # Context Information
    session_id = db.Column(db.String(100), nullable=True)  # Track sessions
    device_type = db.Column(db.String(50), nullable=True)  # desktop, mobile, tablet
    referrer = db.Column(db.String(200), nullable=True)  # How they found the product
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='interactions')
    product = db.relationship('Product', back_populates='interactions')
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_user_product', 'user_id', 'product_id'),
        db.Index('idx_interaction_type_date', 'interaction_type', 'created_at'),
        db.Index('idx_user_type_date', 'user_id', 'interaction_type', 'created_at'),
    )
    
    def __repr__(self):
        return f'<UserInteraction {self.id}: User {self.user_id} - Product {self.product_id} ({self.interaction_type})>'
    
    def to_dict(self):
        """Convert interaction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'interaction_type': self.interaction_type,
            'rating': self.rating,
            'review_text': self.review_text,
            'quantity': self.quantity,
            'price_at_interaction': self.price_at_interaction,
            'session_id': self.session_id,
            'device_type': self.device_type,
            'referrer': self.referrer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_interaction_weight(interaction_type):
        """
        Get weight for different interaction types (for recommendation scoring)
        Higher weight = stronger interest signal
        """
        weights = {
            'purchase': 10,
            'rating': 8,
            'review': 8,
            'cart_add': 6,
            'wishlist_add': 5,
            'click': 3,
            'view': 2,
            'search': 1,
            'cart_remove': -2,
            'wishlist_remove': -1
        }
        return weights.get(interaction_type, 1)
    
    @property
    def interaction_weight(self):
        """Get the weight of this interaction"""
        return self.get_interaction_weight(self.interaction_type)
    
    @staticmethod
    def interaction_types():
        """Get list of valid interaction types"""
        return [
            'view',
            'purchase',
            'cart_add',
            'cart_remove',
            'wishlist_add',
            'wishlist_remove',
            'rating',
            'review',
            'search',
            'click'
        ]
