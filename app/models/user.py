"""
User Model - Stores user profile information
"""
from datetime import datetime
from app import db


class User(db.Model):
    """
    User model representing customers in the e-commerce platform
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=True)
    
    # Demographics (for personalization)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # User Preferences
    preferred_categories = db.Column(db.String(500), nullable=True)  # Comma-separated
    preferred_brands = db.Column(db.String(500), nullable=True)  # Comma-separated
    price_range_min = db.Column(db.Float, nullable=True)
    price_range_max = db.Column(db.Float, nullable=True)
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Activity Metrics
    total_purchases = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = db.relationship('UserInteraction', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.id}: {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'preferred_categories': self.preferred_categories.split(',') if self.preferred_categories else [],
            'preferred_brands': self.preferred_brands.split(',') if self.preferred_brands else [],
            'price_range': {
                'min': self.price_range_min,
                'max': self.price_range_max
            } if self.price_range_min or self.price_range_max else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'total_purchases': self.total_purchases,
            'total_spent': self.total_spent,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def update_activity(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    def add_purchase(self, amount):
        """Update purchase metrics"""
        self.total_purchases += 1
        self.total_spent += amount
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    @property
    def average_order_value(self):
        """Calculate average order value"""
        if self.total_purchases > 0:
            return round(self.total_spent / self.total_purchases, 2)
        return 0.0
    
    @property
    def preferred_category_list(self):
        """Get preferred categories as a list"""
        return [cat.strip() for cat in self.preferred_categories.split(',') if cat.strip()] if self.preferred_categories else []
    
    @property
    def preferred_brand_list(self):
        """Get preferred brands as a list"""
        return [brand.strip() for brand in self.preferred_brands.split(',') if brand.strip()] if self.preferred_brands else []
