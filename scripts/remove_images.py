"""
Remove all image URLs from products to eliminate network requests
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Product

def remove_image_urls():
    """Remove all image URLs from products"""
    print("🗑️ Removing all product image URLs...")
    
    app = create_app()
    
    with app.app_context():
        # Update all products to have no image_url
        updated_count = Product.query.update({Product.image_url: None})
        db.session.commit()
        
        print(f"   ✅ Removed image URLs from {updated_count} products")
        print("   🎨 Products will now use category-specific icon placeholders")
        
        # Show category distribution
        categories = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category).order_by(db.text('count DESC')).all()
        
        print("\n📊 Category Distribution:")
        for category, count in categories:
            print(f"   {category}: {count} products")

if __name__ == '__main__':
    remove_image_urls()