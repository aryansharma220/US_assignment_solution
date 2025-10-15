"""
Update existing product image URLs to use working placeholders
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Product

def update_image_urls():
    """Update product image URLs to use working placeholder service"""
    print("🖼️ Updating product image URLs...")
    
    app = create_app()
    
    with app.app_context():
        products = Product.query.all()
        
        category_colors = {
            'Electronics': '3B82F6/FFFFFF',  # Blue
            'Fashion': 'EC4899/FFFFFF',      # Pink  
            'Home & Kitchen': '10B981/FFFFFF', # Green
            'Books': 'F59E0B/FFFFFF',        # Orange
            'Beauty': 'A855F7/FFFFFF'        # Purple
        }
        
        updated_count = 0
        
        for product in products:
            # Get color for category
            color = category_colors.get(product.category, 'E5E7EB/6B7280')
            
            # Create a better placeholder URL
            category_text = product.subcategory or product.category
            new_url = f"https://via.placeholder.com/400x400/{color}?text={category_text.replace(' ', '+')}"
            
            if product.image_url != new_url:
                product.image_url = new_url
                updated_count += 1
        
        db.session.commit()
        print(f"   ✅ Updated {updated_count} product image URLs")
        print("   🎨 Using category-colored placeholders:")
        for category, color in category_colors.items():
            count = Product.query.filter_by(category=category).count()
            print(f"      {category}: {count} products with {color.split('/')[0]} backgrounds")

if __name__ == '__main__':
    update_image_urls()