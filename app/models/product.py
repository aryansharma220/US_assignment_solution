"""
Product Model - Stores product catalog information
"""
from datetime import datetime
from app import db


class Product(db.Model):
    """
    Product model representing items in the e-commerce catalog
    """
    __tablename__ = 'products'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    subcategory = db.Column(db.String(100), nullable=True)
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)  # For discounts
    currency = db.Column(db.String(3), default='USD')
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True, index=True)
    
    # Product Attributes
    brand = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    
    # Ratings & Reviews
    average_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    
    # Product Features (for content-based filtering)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    features = db.Column(db.Text, nullable=True)  # JSON string of features
    
    # Metadata
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = db.relationship('UserInteraction', back_populates='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': self.price,
            'original_price': self.original_price,
            'currency': self.currency,
            'stock_quantity': self.stock_quantity,
            'is_available': self.is_available,
            'brand': self.brand,
            'color': self.color,
            'size': self.size,
            'material': self.material,
            'average_rating': self.average_rating,
            'review_count': self.review_count,
            'tags': self.tags.split(',') if self.tags else [],
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if applicable"""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 2)
        return 0
    
    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.original_price and self.original_price > self.price
    
    @property
    def tag_list(self):
        """Get tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []
