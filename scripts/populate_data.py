"""
Sample data population script
Generates realistic e-commerce data for testing
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Product, User, UserInteraction


# Sample data for products
CATEGORIES = {
    'Electronics': ['Smartphones', 'Laptops', 'Headphones', 'Cameras', 'Smartwatches'],
    'Fashion': ['T-Shirts', 'Jeans', 'Dresses', 'Shoes', 'Accessories'],
    'Home & Kitchen': ['Cookware', 'Furniture', 'Decor', 'Appliances', 'Bedding'],
    'Sports': ['Fitness Equipment', 'Sportswear', 'Outdoor Gear', 'Yoga', 'Cycling'],
    'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics', 'Self-Help'],
    'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrances', 'Tools'],
    'Toys': ['Action Figures', 'Board Games', 'Educational', 'Outdoor', 'Puzzles'],
    'Grocery': ['Snacks', 'Beverages', 'Organic', 'Frozen', 'Dairy']
}

BRANDS = ['Samsung', 'Apple', 'Sony', 'Nike', 'Adidas', 'Zara', 'H&M', 'Levi\'s', 
          'Canon', 'Nikon', 'Philips', 'LG', 'Dell', 'HP', 'Asus', 'Generic']

COLORS = ['Black', 'White', 'Blue', 'Red', 'Green', 'Gray', 'Silver', 'Gold', 'Pink', 'Purple']

SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size']

PRODUCT_TEMPLATES = [
    'Premium {adj} {item}',
    'Professional {item}',
    '{brand} {item}',
    'Luxury {adj} {item}',
    'Budget {item}',
    '{adj} {item} Pro',
    'Classic {item}',
    'Modern {item}',
]

ADJECTIVES = ['Smart', 'Ultra', 'Pro', 'Elite', 'Advanced', 'Essential', 'Premium', 
              'Deluxe', 'Standard', 'Basic', 'High-Performance', 'Stylish', 'Comfortable']


def generate_products(num_products=100):
    """Generate sample products"""
    print(f"\n📦 Generating {num_products} products...")
    products = []
    
    for i in range(num_products):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        brand = random.choice(BRANDS)
        
        # Generate product name
        template = random.choice(PRODUCT_TEMPLATES)
        adj = random.choice(ADJECTIVES)
        name = template.format(
            adj=adj,
            item=subcategory,
            brand=brand
        )
        
        # Generate pricing
        base_price = round(random.uniform(10, 1000), 2)
        is_on_sale = random.random() < 0.3  # 30% chance of sale
        original_price = round(base_price * random.uniform(1.1, 1.5), 2) if is_on_sale else None
        
        # Generate ratings
        avg_rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 500)
        
        # Generate tags
        tags = [
            category.lower(),
            subcategory.lower(),
            brand.lower(),
            random.choice(['trending', 'bestseller', 'new', 'popular', 'featured'])
        ]
        
        product = Product(
            name=name,
            description=f"High-quality {subcategory.lower()} from {brand}. {adj} design with premium features.",
            category=category,
            subcategory=subcategory,
            price=base_price if not is_on_sale else original_price * random.uniform(0.7, 0.9),
            original_price=original_price,
            stock_quantity=random.randint(0, 200),
            is_available=random.random() < 0.95,  # 95% available
            brand=brand,
            color=random.choice(COLORS) if random.random() < 0.7 else None,
            size=random.choice(SIZES) if category in ['Fashion', 'Sports'] else None,
            average_rating=avg_rating,
            review_count=review_count,
            tags=','.join(tags),
            image_url=f"https://placeholder.com/product{i+1}.jpg"
        )
        products.append(product)
    
    db.session.bulk_save_objects(products)
    db.session.commit()
    print(f"   ✅ Created {num_products} products")
    return products


def generate_users(num_users=50):
    """Generate sample users"""
    print(f"\n👥 Generating {num_users} users...")
    users = []
    
    FIRST_NAMES = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa', 
                   'Tom', 'Anna', 'James', 'Mary', 'Robert', 'Linda', 'Michael']
    LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson']
    GENDERS = ['Male', 'Female', 'Other', 'Prefer not to say']
    LOCATIONS = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
                 'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Seattle']
    
    for i in range(num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@example.com"
        
        # Generate preferences
        preferred_cats = random.sample(list(CATEGORIES.keys()), k=random.randint(1, 3))
        preferred_brands = random.sample(BRANDS, k=random.randint(1, 4))
        
        user = User(
            username=username,
            email=email,
            full_name=f"{first_name} {last_name}",
            age=random.randint(18, 70),
            gender=random.choice(GENDERS),
            location=random.choice(LOCATIONS),
            preferred_categories=','.join(preferred_cats),
            preferred_brands=','.join(preferred_brands),
            price_range_min=random.choice([10, 20, 50, 100]),
            price_range_max=random.choice([200, 500, 1000, 2000]),
            is_active=True,
            is_verified=random.random() < 0.8,  # 80% verified
            total_purchases=random.randint(0, 50),
            total_spent=round(random.uniform(0, 5000), 2),
            last_active=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        users.append(user)
    
    db.session.bulk_save_objects(users)
    db.session.commit()
    print(f"   ✅ Created {num_users} users")
    return users


def generate_interactions(num_interactions=500):
    """Generate sample user interactions"""
    print(f"\n🔄 Generating {num_interactions} interactions...")
    
    # Get all users and products
    users = User.query.all()
    products = Product.query.all()
    
    if not users or not products:
        print("   ⚠️  No users or products found. Run product and user generation first.")
        return
    
    interaction_types = UserInteraction.interaction_types()
    device_types = ['desktop', 'mobile', 'tablet']
    referrers = ['search', 'direct', 'social', 'email', 'ads']
    
    interactions = []
    
    for i in range(num_interactions):
        user = random.choice(users)
        product = random.choice(products)
        interaction_type = random.choice(interaction_types)
        
        # Create realistic interaction patterns
        rating = None
        review_text = None
        quantity = 1
        
        if interaction_type == 'rating':
            rating = random.randint(1, 5)
        elif interaction_type == 'review':
            rating = random.randint(1, 5)
            review_text = f"Great product! Would recommend. Rating: {rating}/5"
        elif interaction_type == 'purchase':
            quantity = random.randint(1, 3)
        elif interaction_type in ['cart_add', 'wishlist_add']:
            quantity = random.randint(1, 2)
        
        interaction = UserInteraction(
            user_id=user.id,
            product_id=product.id,
            interaction_type=interaction_type,
            rating=rating,
            review_text=review_text,
            quantity=quantity,
            price_at_interaction=product.price,
            session_id=f"session_{random.randint(1000, 9999)}",
            device_type=random.choice(device_types),
            referrer=random.choice(referrers),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
        )
        interactions.append(interaction)
    
    db.session.bulk_save_objects(interactions)
    db.session.commit()
    print(f"   ✅ Created {num_interactions} interactions")


def populate_database(num_products=100, num_users=50, num_interactions=500):
    """Main function to populate database with sample data"""
    print("🌱 Sample Data Population Script")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Check if data already exists
        existing_products = Product.query.count()
        existing_users = User.query.count()
        existing_interactions = UserInteraction.query.count()
        
        print(f"\n📊 Current database state:")
        print(f"   Products: {existing_products}")
        print(f"   Users: {existing_users}")
        print(f"   Interactions: {existing_interactions}")
        
        if existing_products > 0 or existing_users > 0:
            response = input("\n⚠️  Database already contains data. Clear and regenerate? (yes/no): ").lower()
            if response != 'yes':
                print("\n❌ Operation cancelled.")
                return
            
            print("\n🗑️  Clearing existing data...")
            UserInteraction.query.delete()
            Product.query.delete()
            User.query.delete()
            db.session.commit()
            print("   ✅ Data cleared")
        
        # Generate new data
        generate_products(num_products)
        generate_users(num_users)
        generate_interactions(num_interactions)
        
        # Show summary
        print("\n" + "=" * 60)
        print("✅ Database population complete!")
        print("\n📊 Final database state:")
        print(f"   Products: {Product.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Interactions: {UserInteraction.query.count()}")
        print("\n📈 Sample statistics:")
        print(f"   Average product price: ${Product.query.with_entities(db.func.avg(Product.price)).scalar():.2f}")
        print(f"   Products on sale: {Product.query.filter(Product.original_price.isnot(None)).count()}")
        print(f"   Active users: {User.query.filter_by(is_active=True).count()}")
        print(f"   Total purchases: {UserInteraction.query.filter_by(interaction_type='purchase').count()}")
        print("\n📝 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Test the API endpoints")
        print("   3. Move to Step 3: Recommendation Engine")
        print("=" * 60)


if __name__ == '__main__':
    populate_database(
        num_products=100,
        num_users=50,
        num_interactions=500
    )
