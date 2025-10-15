"""
Realistic Indian E-commerce Product Data Generator
Creates sensible products with proper brands, pricing, and descriptions
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Product, User, UserInteraction


# Realistic Product Database
REALISTIC_PRODUCTS = {
    'Smartphones': [
        {
            'name': 'Samsung Galaxy A54 5G',
            'brand': 'Samsung',
            'price': 38999,
            'original_price': 42999,
            'description': 'Premium design meets flagship camera. Features 50MP main camera, 6.4" Super AMOLED display, 5000mAh battery with 25W fast charging. Available in Awesome Violet, Awesome White, Awesome Graphite.',
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/in/2302/gallery/in-galaxy-a54-5g-a546-sm-a546elvdins-534851043',
            'stock': 45
        },
        {
            'name': 'OnePlus Nord CE 3 Lite 5G',
            'brand': 'OnePlus',
            'price': 19999,
            'original_price': 21999,
            'description': 'Fast and smooth experience with Snapdragon 695 5G processor. 108MP triple camera system, 67W SUPERVOOC fast charging, and OxygenOS 13.1 based on Android 13.',
            'stock': 32
        },
        {
            'name': 'Realme 11 Pro+ 5G',
            'brand': 'Realme',
            'price': 27999,
            'original_price': 29999,
            'description': 'Curve vision design with 200MP OIS camera. MediaTek Dimensity 7050 5G chipset, 100W SuperVOOC charging, and premium curved display for immersive viewing.',
            'stock': 28
        },
        {
            'name': 'Xiaomi Redmi Note 12 Pro',
            'brand': 'Xiaomi',
            'price': 23999,
            'description': 'Pro-grade photography with 50MP triple camera setup. MediaTek Dimensity 1080 processor, 120Hz AMOLED display, and 67W turbo charging for all-day performance.',
            'stock': 56
        },
        {
            'name': 'iPhone 15',
            'brand': 'Apple',
            'price': 79900,
            'description': 'Dynamic Island and 48MP main camera with 2x telephoto. A16 Bionic chip, all-day battery life, and USB-C connectivity. Available in Pink, Yellow, Green, Blue, Black.',
            'stock': 12
        },
        {
            'name': 'Vivo V29 5G',
            'brand': 'Vivo',
            'price': 32999,
            'description': 'Aura Light portrait system with 50MP selfie camera. Snapdragon 778G 5G processor, 80W FlashCharge, and color-changing design for style enthusiasts.',
            'stock': 23
        }
    ],
    
    'Laptops': [
        {
            'name': 'HP Pavilion 15 (AMD Ryzen 5)',
            'brand': 'HP',
            'price': 54990,
            'original_price': 59990,
            'description': 'Perfect for students and professionals. AMD Ryzen 5 5500U processor, 8GB RAM, 512GB SSD, 15.6" FHD display. Pre-loaded with Windows 11 Home and MS Office.',
            'stock': 18
        },
        {
            'name': 'Dell Inspiron 3520',
            'brand': 'Dell',
            'price': 47999,
            'description': 'Reliable performance for everyday computing. Intel Core i5-1135G7, 8GB DDR4 RAM, 1TB HDD + 256GB SSD, 15.6" HD display with anti-glare technology.',
            'stock': 22
        },
        {
            'name': 'Lenovo IdeaPad Gaming 3',
            'brand': 'Lenovo',
            'price': 72999,
            'description': 'Gaming laptop with NVIDIA GTX 1650 graphics. AMD Ryzen 5 5600H processor, 16GB RAM, 512GB SSD, 15.6" FHD 120Hz display for smooth gaming experience.',
            'stock': 8
        },
        {
            'name': 'ASUS VivoBook 15',
            'brand': 'ASUS',
            'price': 42999,
            'original_price': 46999,
            'description': 'Thin and light laptop for productivity. Intel Core i3-1115G4, 8GB RAM, 512GB SSD, 15.6" FHD display, fingerprint sensor for secure login.',
            'stock': 35
        },
        {
            'name': 'MacBook Air M2',
            'brand': 'Apple',
            'price': 114900,
            'description': 'Revolutionary M2 chip delivers incredible performance. 8-core CPU, 8-core GPU, 16-core Neural Engine, 13.6" Liquid Retina display, all-day battery life.',
            'stock': 6
        }
    ],
    
    'Headphones': [
        {
            'name': 'boAt Airdopes 141',
            'brand': 'boAt',
            'price': 1499,
            'original_price': 2499,
            'description': 'True wireless earbuds with 42H total playback. ENx Technology for clear calls, IPX4 water resistance, and Bluetooth v5.1 for seamless connectivity.',
            'stock': 125
        },
        {
            'name': 'Sony WH-CH720N',
            'brand': 'Sony',
            'price': 9990,
            'original_price': 11990,
            'description': 'Noise canceling wireless headphones with up to 35 hours battery life. V1 processor, DSEE technology, and multipoint connection for superior audio experience.',
            'stock': 42
        },
        {
            'name': 'JBL Tune 760NC',
            'brand': 'JBL',
            'price': 6999,
            'description': 'Active noise cancelling over-ear headphones. JBL Pure Bass sound, 35H battery life with ANC on, hands-free calls with VoiceAware technology.',
            'stock': 28
        },
        {
            'name': 'Noise Air Buds Pro',
            'brand': 'Noise',
            'price': 3999,
            'original_price': 4999,
            'description': 'Premium TWS with Quad Mic ENC and 45dB ANC. 11mm drivers, 45H total playback, IPX5 rating, and touch controls for seamless music experience.',
            'stock': 67
        }
    ],
    
    'Fashion': [
        {
            'name': 'Levi\'s 511 Slim Jeans',
            'brand': 'Levi\'s',
            'price': 3999,
            'original_price': 4999,
            'description': 'Classic slim fit jeans in authentic indigo denim. Sits below waist, slim from hip to ankle. Made with cotton for comfort and durability.',
            'stock': 45
        },
        {
            'name': 'Nike Air Max SC',
            'brand': 'Nike',
            'price': 4995,
            'description': 'Casual lifestyle sneakers inspired by running heritage. Foam midsole, rubber outsole with waffle pattern, and classic Nike styling for everyday wear.',
            'stock': 32
        },
        {
            'name': 'Adidas Ultraboost 22',
            'brand': 'Adidas',
            'price': 16999,
            'description': 'Premium running shoes with responsive BOOST midsole. Primeknit upper, Continental rubber outsole, and energy return technology for ultimate performance.',
            'stock': 18
        },
        {
            'name': 'FabIndia Cotton Kurta',
            'brand': 'FabIndia',
            'price': 1299,
            'description': 'Handwoven cotton kurta in traditional Indian style. Comfortable straight fit, side slits, and authentic handloom fabric. Perfect for festivals and casual wear.',
            'stock': 78
        },
        {
            'name': 'W Printed Maxi Dress',
            'brand': 'W',
            'price': 2199,
            'original_price': 2999,
            'description': 'Flowy maxi dress with contemporary floral print. V-neckline, 3/4 sleeves, and comfortable viscose fabric. Ideal for casual outings and weekend wear.',
            'stock': 52
        }
    ],
    
    'Home & Kitchen': [
        {
            'name': 'Prestige Deluxe Alpha Pressure Cooker 5L',
            'brand': 'Prestige',
            'price': 1899,
            'original_price': 2299,
            'description': 'Stainless steel pressure cooker with alpha base technology. Controlled gasket release system, precision weight valve, and works on all cooktops including induction.',
            'stock': 89
        },
        {
            'name': 'Philips Daily Collection Mixer Grinder',
            'brand': 'Philips',
            'price': 3495,
            'description': '750W powerful motor with 3 leak-proof jars. Advanced ventilation system, overload protection, and 2-year warranty for reliable grinding performance.',
            'stock': 34
        },
        {
            'name': 'Kent Grand Plus Water Purifier',
            'brand': 'Kent',
            'price': 18500,
            'description': 'RO + UV + UF water purifier with 8L storage tank. TDS controller, UV LED, and zero water wastage technology for pure and healthy drinking water.',
            'stock': 12
        },
        {
            'name': 'Amazon Basics Cotton Bed Sheet Set',
            'brand': 'Amazon Basics',
            'price': 1299,
            'description': '100% cotton double bed sheet set with 2 pillow covers. 144 thread count, fade-resistant colors, and machine washable for easy care.',
            'stock': 95
        }
    ],
    
    'Books': [
        {
            'name': 'The Alchemist',
            'brand': 'HarperCollins',
            'price': 299,
            'description': 'Paulo Coelho\'s masterpiece about following your dreams. International bestseller translated into 80 languages, inspiring millions of readers worldwide.',
            'stock': 156
        },
        {
            'name': 'Rich Dad Poor Dad',
            'brand': 'Plata Publishing',
            'price': 399,
            'description': 'Robert Kiyosaki\'s #1 personal finance book. Learn what the rich teach their kids about money that the poor and middle class do not.',
            'stock': 89
        },
        {
            'name': 'Atomic Habits',
            'brand': 'Random House',
            'price': 599,
            'description': 'James Clear\'s guide to building good habits and breaking bad ones. Practical strategies for forming habits that stick and achieving remarkable results.',
            'stock': 67
        }
    ],
    
    'Beauty': [
        {
            'name': 'Lakme Absolute Perfect Radiance Foundation',
            'brand': 'Lakme',
            'price': 1100,
            'description': 'Lightweight foundation with buildable coverage. SPF 20 protection, vitamin E, and long-lasting formula for natural radiant finish.',
            'stock': 78
        },
        {
            'name': 'Himalaya Herbals Neem Face Wash',
            'brand': 'Himalaya',
            'price': 175,
            'description': 'Soap-free herbal formulation with neem and turmeric. Prevents pimples, removes excess oil, and gives you clear, problem-free skin.',
            'stock': 234
        },
        {
            'name': 'Forest Essentials Facial Cleanser',
            'brand': 'Forest Essentials',
            'price': 1875,
            'description': 'Ayurvedic facial cleanser with rose and saffron. Traditional recipe blended with modern techniques for gentle yet effective cleansing.',
            'stock': 45
        }
    ]
}


def create_realistic_products():
    """Create realistic products from the predefined database"""
    print("\n📦 Creating realistic Indian e-commerce products...")
    
    products = []
    product_id = 1
    
    for category, items in REALISTIC_PRODUCTS.items():
        print(f"   Creating {category} products...")
        
        for item in items:
            # Calculate ratings based on price tier and brand reputation
            brand_ratings = {
                'Apple': (4.3, 4.8), 'Samsung': (4.2, 4.7), 'OnePlus': (4.1, 4.6),
                'Sony': (4.0, 4.5), 'Nike': (4.2, 4.7), 'Adidas': (4.1, 4.6),
                'Levi\'s': (4.0, 4.5), 'HP': (3.8, 4.3), 'Dell': (3.7, 4.2),
                'boAt': (3.9, 4.4), 'Noise': (3.8, 4.3), 'Prestige': (4.1, 4.6),
                'Lakme': (3.9, 4.4), 'Himalaya': (4.0, 4.5)
            }
            
            brand = item['brand']
            rating_range = brand_ratings.get(brand, (3.5, 4.5))
            avg_rating = round(random.uniform(rating_range[0], rating_range[1]), 1)
            review_count = random.randint(50, 500) if avg_rating > 4.0 else random.randint(10, 200)
            
            # Determine main category
            main_category = 'Electronics' if category in ['Smartphones', 'Laptops', 'Headphones'] else category
            
            # Generate realistic tags
            tags = [
                main_category.lower(),
                category.lower(),
                brand.lower(),
                'bestseller' if avg_rating > 4.2 else 'popular',
                'trending' if item.get('original_price') else 'featured'
            ]
            
            product = Product(
                name=item['name'],
                description=item['description'],
                category=main_category,
                subcategory=category,
                price=item['price'],
                original_price=item.get('original_price'),
                stock_quantity=item['stock'],
                is_available=True,
                brand=brand,
                average_rating=avg_rating,
                review_count=review_count,
                tags=','.join(tags),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                updated_at=datetime.utcnow()
            )
            
            products.append(product)
            product_id += 1
    
    # Add products to database
    db.session.bulk_save_objects(products)
    db.session.commit()
    
    print(f"   ✅ Created {len(products)} realistic products")
    return products


def create_realistic_users(num_users=50):
    """Create realistic Indian users"""
    print(f"\n👥 Creating {num_users} realistic users...")
    
    # Indian names and locations
    INDIAN_NAMES = [
        ('Aryan', 'Sharma'), ('Priya', 'Patel'), ('Rahul', 'Kumar'), ('Ananya', 'Singh'),
        ('Rohan', 'Gupta'), ('Diya', 'Reddy'), ('Aditya', 'Verma'), ('Sneha', 'Joshi'),
        ('Arjun', 'Mehta'), ('Isha', 'Nair'), ('Karan', 'Iyer'), ('Riya', 'Das'),
        ('Vivek', 'Malhotra'), ('Kavya', 'Chopra'), ('Siddharth', 'Agarwal'), ('Nisha', 'Bansal'),
        ('Amit', 'Saxena'), ('Pooja', 'Mishra'), ('Vikram', 'Rao'), ('Anjali', 'Pandey'),
        ('Raj', 'Sinha'), ('Neha', 'Tiwari'), ('Akash', 'Chauhan'), ('Preeti', 'Jain'),
        ('Nikhil', 'Bhatt'), ('Deepika', 'Khanna'), ('Rohit', 'Bajaj'), ('Simran', 'Goel'),
        ('Varun', 'Sood'), ('Shreya', 'Kapoor'), ('Manish', 'Arora'), ('Divya', 'Sethi')
    ]
    
    INDIAN_CITIES = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
        'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Chandigarh', 'Kochi',
        'Indore', 'Nagpur', 'Gurgaon', 'Noida', 'Coimbatore', 'Vadodara'
    ]
    
    users = []
    
    for i in range(num_users):
        first_name, last_name = random.choice(INDIAN_NAMES)
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        
        # Generate realistic preferences based on Indian shopping patterns
        tech_users = random.random() < 0.4  # 40% are tech-savvy
        fashion_conscious = random.random() < 0.6  # 60% follow fashion
        
        preferred_categories = []
        if tech_users:
            preferred_categories.extend(['Electronics'])
        if fashion_conscious:
            preferred_categories.extend(['Fashion'])
        preferred_categories.extend(random.sample(['Home & Kitchen', 'Books', 'Beauty'], k=random.randint(1, 2)))
        
        # Realistic price ranges based on Indian demographics
        income_tier = random.choices(
            ['budget', 'middle', 'premium'],
            weights=[0.5, 0.4, 0.1]  # 50% budget, 40% middle class, 10% premium
        )[0]
        
        price_ranges = {
            'budget': (500, 15000),
            'middle': (1000, 50000),
            'premium': (5000, 200000)
        }
        
        min_price, max_price = price_ranges[income_tier]
        
        user = User(
            username=username,
            email=email,
            full_name=f"{first_name} {last_name}",
            display_name=f"{first_name} {last_name}",
            age=random.randint(18, 65),
            gender=random.choice(['Male', 'Female']),
            location=random.choice(INDIAN_CITIES),
            preferred_categories=','.join(preferred_categories),
            preferred_brands=','.join(random.sample(['Samsung', 'Xiaomi', 'OnePlus', 'Nike', 'Adidas', 'Levi\'s'], k=random.randint(2, 4))),
            price_range_min=min_price,
            price_range_max=max_price,
            is_active=True,
            is_verified=random.random() < 0.85,  # 85% verified
            total_purchases=random.randint(0, 25),
            total_spent=round(random.uniform(0, max_price * 2), 2),
            last_active=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        users.append(user)
    
    db.session.bulk_save_objects(users)
    db.session.commit()
    
    print(f"   ✅ Created {num_users} realistic users")
    return users


def main():
    """Main function to populate database with realistic data"""
    print("🇮🇳 Realistic Indian E-commerce Data Generator")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Create tables
        print("\n🔧 Setting up database...")
        db.create_all()
        
        # Check existing data
        existing_products = Product.query.count()
        existing_users = User.query.count()
        
        print(f"\n📊 Current database state:")
        print(f"   Products: {existing_products}")
        print(f"   Users: {existing_users}")
        
        if existing_products > 0:
            response = input("\n⚠️  Database has existing products. Replace with realistic data? (yes/no): ").lower()
            if response != 'yes':
                print("\n❌ Operation cancelled.")
                return
            
            print("\n🗑️  Clearing existing data...")
            UserInteraction.query.delete()
            Product.query.delete()
            User.query.delete()
            db.session.commit()
            print("   ✅ Data cleared")
        
        # Generate realistic data
        products = create_realistic_products()
        users = create_realistic_users(30)
        
        # Generate some realistic interactions
        print(f"\n🔄 Generating realistic user interactions...")
        users = User.query.all()
        products = Product.query.all()
        
        interactions = []
        for _ in range(200):
            user = random.choice(users)
            product = random.choice(products)
            
            # More realistic interaction patterns
            interaction_type = random.choices(
                ['view', 'cart_add', 'wishlist_add', 'purchase', 'rating', 'review'],
                weights=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05]
            )[0]
            
            rating = None
            review_text = None
            quantity = 1
            
            if interaction_type == 'rating':
                rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.2, 0.35, 0.3])[0]
            elif interaction_type == 'review':
                rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.2, 0.35, 0.3])[0]
                reviews = [
                    "Great product! Highly recommend.",
                    "Good value for money. Works as expected.",
                    "Excellent quality and fast delivery.",
                    "Perfect for my needs. Will buy again.",
                    "Amazing product! Exceeded expectations."
                ]
                review_text = random.choice(reviews)
            elif interaction_type == 'purchase':
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
                device_type=random.choices(['mobile', 'desktop', 'tablet'], weights=[0.6, 0.3, 0.1])[0],
                referrer=random.choices(['direct', 'search', 'social', 'ads'], weights=[0.4, 0.3, 0.2, 0.1])[0],
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
            )
            interactions.append(interaction)
        
        db.session.bulk_save_objects(interactions)
        db.session.commit()
        print(f"   ✅ Created {len(interactions)} realistic interactions")
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ Realistic data generation complete!")
        print("\n📊 Database Summary:")
        print(f"   📱 Products: {Product.query.count()}")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   🔄 Interactions: {UserInteraction.query.count()}")
        
        print("\n🏷️  Categories:")
        for category in ['Electronics', 'Fashion', 'Home & Kitchen', 'Books', 'Beauty']:
            count = Product.query.filter_by(category=category).count()
            print(f"   {category}: {count} products")
        
        print("\n💰 Price Range:")
        min_price = Product.query.with_entities(db.func.min(Product.price)).scalar()
        max_price = Product.query.with_entities(db.func.max(Product.price)).scalar()
        avg_price = Product.query.with_entities(db.func.avg(Product.price)).scalar()
        print(f"   Min: ₹{min_price:.0f}")
        print(f"   Max: ₹{max_price:.0f}")
        print(f"   Average: ₹{avg_price:.0f}")
        
        print("\n⭐ Top Rated Products:")
        top_products = Product.query.order_by(Product.average_rating.desc()).limit(5).all()
        for product in top_products:
            print(f"   {product.name} - ⭐{product.average_rating} ({product.review_count} reviews)")
        
        print("\n📈 Next Steps:")
        print("   1. Start the Flask application: python app.py")
        print("   2. Visit: http://localhost:5000")
        print("   3. Browse realistic Indian products!")
        print("=" * 60)


if __name__ == '__main__':
    main()