"""
Migration script to add display_name column to User table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def migrate():
    """Add display_name column and populate it from existing data"""
    app = create_app()
    
    with app.app_context():
        print("\n🔄 Starting migration: Add display_name to User table...")
        
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            
            if 'display_name' in columns:
                print("   ℹ️  Column 'display_name' already exists")
            else:
                # Add the display_name column
                print("   📝 Adding display_name column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN display_name VARCHAR(100)"))
                db.session.commit()
                print("   ✅ Column added successfully")
            
            # Populate display_name from full_name for existing users
            print("   📝 Populating display_name for existing users...")
            db.session.execute(text("""
                UPDATE user 
                SET display_name = full_name 
                WHERE display_name IS NULL AND full_name IS NOT NULL
            """))
            
            # For users without full_name, use username
            db.session.execute(text("""
                UPDATE user 
                SET display_name = username 
                WHERE display_name IS NULL
            """))
            
            db.session.commit()
            print("   ✅ Display names populated successfully")
            
            # Show some sample results
            result = db.session.execute(text("""
                SELECT username, full_name, display_name 
                FROM user 
                LIMIT 5
            """))
            
            print("\n   📊 Sample users:")
            for row in result:
                print(f"      Username: {row[0]}")
                print(f"      Full Name: {row[1]}")
                print(f"      Display Name: {row[2]}")
                print()
            
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate()
