"""
Database Initialization Script for ShopSmart AI
Populates database with Indian e-commerce product catalog
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Product, User, UserInteraction


def add_product(category, product_data):
    """Add a single product to the database"""
    product = Product(
        name=product_data['name'],
        brand=product_data['brand'],
        category=category,
        subcategory=product_data.get('subcategory', ''),
        price=product_data['price'],
        original_price=product_data.get('original_price'),
        currency='INR',
        description=product_data['description'],
        features=product_data.get('features', ''),
        tags=product_data.get('tags', ''),
        image_url=None,
        stock_quantity=product_data.get('stock', random.randint(5, 50)),
        is_available=True,
        average_rating=round(random.uniform(3.5, 5.0), 1),
        review_count=random.randint(5, 200),
        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
    )
    db.session.add(product)


def add_sample_users():
    """Add sample users with realistic data"""
    users_data = [
        {'username': 'rajesh_kumar', 'email': 'rajesh@example.com', 'full_name': 'Rajesh Kumar'},
        {'username': 'priya_sharma', 'email': 'priya@example.com', 'full_name': 'Priya Sharma'},
        {'username': 'amit_singh', 'email': 'amit@example.com', 'full_name': 'Amit Singh'},
        {'username': 'neha_gupta', 'email': 'neha@example.com', 'full_name': 'Neha Gupta'},
        {'username': 'vikram_rao', 'email': 'vikram@example.com', 'full_name': 'Vikram Rao'},
        {'username': 'anita_patel', 'email': 'anita@example.com', 'full_name': 'Anita Patel'},
        {'username': 'rohit_shah', 'email': 'rohit@example.com', 'full_name': 'Rohit Shah'},
        {'username': 'deepika_verma', 'email': 'deepika@example.com', 'full_name': 'Deepika Verma'},
        {'username': 'arjun_reddy', 'email': 'arjun@example.com', 'full_name': 'Arjun Reddy'},
        {'username': 'kavya_nair', 'email': 'kavya@example.com', 'full_name': 'Kavya Nair'},
        {'username': 'suresh_yadav', 'email': 'suresh@example.com', 'full_name': 'Suresh Yadav'},
        {'username': 'pooja_jain', 'email': 'pooja@example.com', 'full_name': 'Pooja Jain'},
        {'username': 'rahul_mehta', 'email': 'rahul@example.com', 'full_name': 'Rahul Mehta'},
        {'username': 'sita_agarwal', 'email': 'sita@example.com', 'full_name': 'Sita Agarwal'},
        {'username': 'kiran_das', 'email': 'kiran@example.com', 'full_name': 'Kiran Das'},
        {'username': 'manish_khanna', 'email': 'manish@example.com', 'full_name': 'Manish Khanna'},
        {'username': 'sunita_bhatt', 'email': 'sunita@example.com', 'full_name': 'Sunita Bhatt'},
        {'username': 'vishal_garg', 'email': 'vishal@example.com', 'full_name': 'Vishal Garg'},
        {'username': 'meera_saxena', 'email': 'meera@example.com', 'full_name': 'Meera Saxena'},
        {'username': 'ashish_tiwari', 'email': 'ashish@example.com', 'full_name': 'Ashish Tiwari'},
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            age=random.randint(18, 65),
            gender=random.choice(['Male', 'Female']),
            location=random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Ahmedabad']),
            is_active=True,
            is_verified=True,
            total_purchases=0,
            total_spent=0.0,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
        )
        db.session.add(user)


def add_sample_interactions():
    """Add sample user interactions and update user statistics"""
    users = User.query.all()
    products = Product.query.all()
    
    for _ in range(150):
        user = random.choice(users)
        product = random.choice(products)
        
        interaction_type = random.choices(
            ['view', 'cart_add', 'purchase', 'wishlist_add'],
            weights=[0.6, 0.2, 0.15, 0.05]
        )[0]
        
        interaction = UserInteraction(
            user_id=user.id,
            product_id=product.id,
            interaction_type=interaction_type,
            rating=random.randint(3, 5) if random.random() > 0.7 else None,
            quantity=random.randint(1, 3) if interaction_type == 'purchase' else 1,
            price_at_interaction=product.price,
            session_id=f"session_{random.randint(1000, 9999)}",
            device_type=random.choices(['mobile', 'desktop', 'tablet'], weights=[0.6, 0.3, 0.1])[0],
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
        )
        db.session.add(interaction)
    
    db.session.commit()
    
    for user in users:
        purchases = UserInteraction.query.filter_by(
            user_id=user.id, 
            interaction_type='purchase'
        ).all()
        
        total_purchases = len(purchases)
        total_spent = sum(p.price_at_interaction * p.quantity for p in purchases)
        
        user.total_purchases = total_purchases
        user.total_spent = total_spent
        user.last_active = datetime.utcnow() - timedelta(days=random.randint(0, 7))
        
        if purchases:
            categories = list(set(Product.query.get(p.product_id).category for p in purchases))
            user.preferred_categories = ','.join(categories[:3])


PRODUCTS = {
    'Electronics': [
        {
            'name': 'Samsung Galaxy A54 5G',
            'brand': 'Samsung',
            'price': 38999,
            'original_price': 42999,
            'description': 'Premium design meets flagship camera. Features 50MP main camera, 6.4" Super AMOLED display, 5000mAh battery with 25W fast charging.',
            'subcategory': 'Smartphones',
            'features': '50MP Camera, 6.4" AMOLED, 5000mAh Battery, 25W Charging',
            'tags': 'smartphone, samsung, 5g, camera, amoled'
        },
        {
            'name': 'OnePlus Nord CE 3 Lite 5G',
            'brand': 'OnePlus',
            'price': 19999,
            'original_price': 21999,
            'description': 'Smooth performance with 108MP camera. Snapdragon 695 processor, 120Hz display, 5000mAh battery.',
            'subcategory': 'Smartphones',
            'features': '108MP Camera, 120Hz Display, Snapdragon 695, 5000mAh',
            'tags': 'oneplus, smartphone, 5g, 108mp, snapdragon'
        },
        {
            'name': 'HP Pavilion Gaming Laptop',
            'brand': 'HP',
            'price': 54990,
            'original_price': 59990,
            'description': 'AMD Ryzen 5 5600H processor, NVIDIA GTX 1650 graphics, 8GB RAM, 512GB SSD, 15.6" FHD display.',
            'subcategory': 'Laptops',
            'features': 'Ryzen 5 5600H, GTX 1650, 8GB RAM, 512GB SSD',
            'tags': 'laptop, hp, gaming, ryzen, nvidia'
        },
        {
            'name': 'Dell Inspiron 3520',
            'brand': 'Dell',
            'price': 42990,
            'description': 'Intel Core i5-1235U processor, 8GB DDR4 RAM, 512GB SSD, 15.6" FHD display, Windows 11.',
            'subcategory': 'Laptops',
            'features': 'Intel i5-1235U, 8GB RAM, 512GB SSD, 15.6" FHD',
            'tags': 'laptop, dell, intel, core i5, windows'
        },
        {
            'name': 'boAt Airdopes 141 Bluetooth TWS',
            'brand': 'boAt',
            'price': 1499,
            'original_price': 2499,
            'description': 'True wireless earbuds with 42H playtime, ENx technology, ASAP charge, IPX4 water resistance.',
            'subcategory': 'Audio',
            'features': '42H Playtime, ENx Technology, IPX4, ASAP Charge',
            'tags': 'earbuds, boat, bluetooth, tws, wireless'
        }
    ],
    'Fashion': [
        {
            'name': "Levi's 511 Slim Jeans",
            'brand': "Levi's",
            'price': 3999,
            'original_price': 4999,
            'description': 'Classic slim fit jeans with comfort stretch. Made from premium denim, perfect for casual and semi-formal occasions.',
            'subcategory': 'Jeans',
            'features': 'Slim Fit, Comfort Stretch, Premium Denim',
            'tags': 'jeans, levis, slim fit, denim, casual'
        },
        {
            'name': 'Nike Air Max 270',
            'brand': 'Nike',
            'price': 12995,
            'description': 'Lifestyle sneakers with Max Air unit for all-day comfort. Engineered mesh upper for breathability.',
            'subcategory': 'Footwear',
            'features': 'Max Air Unit, Engineered Mesh, All-day Comfort',
            'tags': 'sneakers, nike, air max, comfort, lifestyle'
        }
    ],
    'Home & Kitchen': [
        {
            'name': 'Prestige Deluxe Alpha Stainless Steel Pressure Cooker',
            'brand': 'Prestige',
            'price': 2890,
            'original_price': 3200,
            'description': '5 Litre pressure cooker with controlled gasket-release system. Made from stainless steel with induction base.',
            'subcategory': 'Cookware',
            'features': '5L Capacity, Stainless Steel, Induction Compatible',
            'tags': 'pressure cooker, prestige, stainless steel, induction'
        },
        {
            'name': 'Bajaj Rex DLX 500-Watt Mixer Grinder',
            'brand': 'Bajaj',
            'price': 3299,
            'description': '500W powerful motor with 3 jars. Overload protection, sharp blades for efficient grinding.',
            'subcategory': 'Appliances',
            'features': '500W Motor, 3 Jars, Overload Protection',
            'tags': 'mixer grinder, bajaj, 500w, kitchen appliance'
        }
    ],
    'Books': [
        {
            'name': 'The Alchemist by Paulo Coelho',
            'brand': 'HarperCollins',
            'price': 175,
            'original_price': 199,
            'description': 'A magical story about following your dreams. International bestseller translated into 80 languages.',
            'subcategory': 'Fiction',
            'features': 'Paperback, 163 Pages, English',
            'tags': 'book, fiction, paulo coelho, bestseller, dreams'
        },
        {
            'name': 'Atomic Habits by James Clear',
            'brand': 'Random House',
            'price': 399,
            'original_price': 450,
            'description': 'Proven strategies to build good habits and break bad ones. #1 New York Times bestseller.',
            'subcategory': 'Self-Help',
            'features': 'Paperback, 320 Pages, Self-Help',
            'tags': 'book, self-help, habits, productivity, bestseller'
        }
    ],
    'Beauty': [
        {
            'name': 'Lakme Absolute Perfect Radiance Skin Lightening Facewash',
            'brand': 'Lakme',
            'price': 175,
            'original_price': 200,
            'description': 'Gentle facewash with micro-crystals for radiant skin. Suitable for all skin types.',
            'subcategory': 'Skincare',
            'features': 'Micro-crystals, All Skin Types, 100g',
            'tags': 'facewash, lakme, skincare, radiance, gentle'
        },
        {
            'name': 'Mamaearth Onion Hair Oil',
            'brand': 'Mamaearth',
            'price': 399,
            'description': 'Natural hair oil with onion extract and 14 essential oils. Reduces hairfall and promotes growth.',
            'subcategory': 'Haircare',
            'features': 'Onion Extract, 14 Essential Oils, Natural, 250ml',
            'tags': 'hair oil, mamaearth, onion, natural, hairfall'
        }
    ]
}


def main():
    """Initialize database with product catalog"""
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        for category, products in PRODUCTS.items():
            for product_data in products:
                add_product(category, product_data)
        
        add_sample_users()
        
        add_sample_interactions()
        
        db.session.commit()


if __name__ == '__main__':
    main()