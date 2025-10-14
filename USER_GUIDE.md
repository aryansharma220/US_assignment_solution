# 📖 User Guide - AI-Powered Product Recommender

Welcome to the comprehensive user guide for the AI-Powered E-commerce Product Recommender system!

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Web Interface Guide](#web-interface-guide)
3. [Understanding Recommendations](#understanding-recommendations)
4. [API Usage Guide](#api-usage-guide)
5. [Troubleshooting](#troubleshooting)
6. [FAQs](#faqs)

## 🚀 Getting Started

### First Time Setup

1. **Installation** (5 minutes)
   ```bash
   # Clone and navigate to project
   cd US
   
   # Create virtual environment
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configuration** (2 minutes)
   ```bash
   # Copy environment file
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/Mac
   
   # Optional: Add Gemini API key to .env
   # GEMINI_API_KEY=your_key_here
   ```

3. **Load Sample Data** (1 minute)
   ```bash
   python scripts/populate_data.py
   ```

4. **Start the Application**
   ```bash
   python app.py
   ```

5. **Open Your Browser**
   - Navigate to: `http://localhost:5000`
   - You should see the home page!

### Quick Start Checklist

- ✅ Python 3.8+ installed
- ✅ Virtual environment activated
- ✅ Dependencies installed
- ✅ Database populated with sample data
- ✅ Flask server running
- ✅ Browser open to localhost:5000

## 🌐 Web Interface Guide

### 1️⃣ Home Page

**URL**: `http://localhost:5000/`

#### What You'll See:
- **Hero Section**: Welcome message with system status badge
- **Features Grid**: Four main features of the system
- **Statistics Section**: Live database statistics
- **Call-to-Action**: Quick links to get started

#### How to Use:
1. Check the **System Status** badge (green = fully operational)
2. Review the **Statistics** to see available products and users
3. Click **"Explore Products"** to browse the catalog
4. Click **"Get Recommendations"** to see personalized suggestions

#### Understanding Statistics:
- **Total Products**: Number of products in catalog
- **Active Users**: Number of users in the system
- **Interactions**: Total user interactions (views, purchases, ratings)
- **Recommendations**: Total recommendations generated

---

### 2️⃣ Recommendations Page

**URL**: `http://localhost:5000/recommendations`

#### Step-by-Step Guide:

**Step 1: Select a User**
- Click the "Select User" dropdown
- Choose any user from the list (e.g., "Alice Johnson")
- The system will load this user's profile

**Step 2: Choose a Strategy**
- **Auto (Recommended)**: System chooses the best strategy
- **Hybrid**: Combines collaborative + content-based
- **Collaborative**: Based on similar users' preferences
- **Content-Based**: Based on product attributes

**Step 3: Set Number of Recommendations**
- Choose between 3, 5, 10, or 15 recommendations
- Recommended: Start with 5

**Step 4: Get Recommendations**
- Click the **"Get Recommendations"** button
- Wait for results (typically < 1 second)

#### Understanding the Results:

**User Info Card** (appears after clicking Get Recommendations):
```
👤 Alice Johnson
📦 12 Purchases
🎯 Strategy: Hybrid Recommendation
```

**Recommendation Cards**:
Each recommendation shows:
1. **Rank Badge**: Position in recommendations (#1, #2, etc.)
2. **Product Image**: Visual representation
3. **Product Name**: Full product title
4. **Category & Brand**: Product classification
5. **Price**: Current price (with discounts if applicable)
6. **Rating**: Star rating and review count
7. **Match Score**: How well it matches (0-100%)
8. **AI Explanation**: Why this product is recommended
9. **Reason Tags**: Quick indicators (👥 Similar users, 📁 Matched categories)
10. **Action Buttons**: View details or find similar products

#### Pro Tips:
- 💡 Try different strategies to see varying results
- 💡 "Auto" strategy is intelligent and adapts to user history
- 💡 AI explanations help understand WHY products are recommended
- 💡 Higher match scores = better fit for the user

---

### 3️⃣ Products Page

**URL**: `http://localhost:5000/products`

#### Navigation Features:

**Filters Panel** (left side):
1. **Category Filter**
   - "All Categories" shows everything
   - Select specific category (Electronics, Clothing, etc.)
   
2. **Sort Options**
   - Name (A-Z)
   - Price (Low to High)
   - Price (High to Low)
   - Rating (High to Low)
   
3. **Search Bar**
   - Type product name or brand
   - Results update as you type
   - Example: "laptop" or "nike"

#### Product Grid:

**Product Cards Show**:
- Product image with category icon
- Product name and brand
- Category badge
- Price (with sale indicator if discounted)
- Rating with star display
- Stock status (In Stock / Low Stock / Out of Stock)
- "View Details" button

**Click Any Product**:
- Opens a modal with full details
- Shows all specifications
- Displays features list
- Shows complete description
- View customer ratings

#### Pagination:
- 12 products per page
- Navigate using numbered buttons
- First/Last page quick links
- Current page highlighted

#### Pro Tips:
- 💡 Use search for quick finding
- 💡 Combine filters for precise results
- 💡 Check "On Sale" badges for discounts
- 💡 Yellow warning = low stock (act fast!)
- 💡 Modal scrolls for long descriptions

---

### 4️⃣ About Page

**URL**: `http://localhost:5000/about`

#### Sections:

**1. Project Overview**
- Learn what the system does
- Understand the vision

**2. Technology Stack**
- See what powers the system
- Python/Flask backend
- Gemini AI integration
- Modern web technologies

**3. How It Works**
- **Collaborative Filtering**: How we use similar users
- **Content-Based Filtering**: How we match product attributes
- **Hybrid Approach**: Combining the best of both
- **AI Explanations**: How Gemini generates insights

**4. Live Statistics**
- Current system metrics
- Real-time data

**5. Key Features**
- All system capabilities listed
- What makes it special

---

## 🎓 Understanding Recommendations

### Recommendation Strategies Explained

#### 1. Auto Strategy (Recommended) 🎯
**What it does**: Intelligently chooses the best approach

**When to use**: Default choice, works for all users

**How it works**:
```
IF user has many interactions:
    → Use Hybrid (best of both worlds)
ELSE IF user has few interactions:
    → Use Content-Based (based on what they liked)
ELSE:
    → Use Collaborative (based on similar users)
```

#### 2. Hybrid Strategy 🔀
**What it does**: Combines collaborative + content-based

**When to use**: Users with moderate interaction history

**How it works**:
- 70% weight to collaborative filtering
- 30% weight to content-based filtering
- Scores normalized and combined
- Best overall accuracy

#### 3. Collaborative Filtering 👥
**What it does**: "Users who liked X also liked Y"

**When to use**: Users with many interactions

**How it works**:
1. Find users similar to you
2. See what they liked
3. Recommend products you haven't tried
4. Weight by similarity score

**Example**: If you and User B both love laptops, and User B also bought a mouse, we'll recommend that mouse to you.

#### 4. Content-Based Filtering 📊
**What it does**: Recommends based on product attributes

**When to use**: New users or users with specific preferences

**How it works**:
1. Analyze products you liked
2. Extract key features (category, brand, price range)
3. Find similar products
4. Rank by similarity

**Example**: If you bought a Nike running shoe, we'll recommend other Nike athletic footwear.

### Understanding Match Scores

**95-100%**: Excellent match, highly recommended
**85-94%**: Very good match, strong recommendation
**75-84%**: Good match, worth considering
**65-74%**: Decent match, might interest you
**50-64%**: Moderate match, explore if curious

### AI Explanation Insights

The Gemini AI generates explanations by analyzing:
- User's purchase history
- Product attributes
- Similar user behaviors
- Category preferences
- Price sensitivity
- Brand loyalty

**Example Explanation**:
> "Based on your previous purchases of Apple MacBook Pro and other premium electronics, this iPad Pro is an excellent match. Users with similar preferences often upgrade to tablets for enhanced mobility. The high rating (4.5★) and premium build quality align perfectly with your preference for quality electronics."

---

## 🔧 API Usage Guide

### For Developers

#### Authentication
Currently, no authentication is required (development mode).

#### Base URL
```
http://localhost:5000/api
```

#### Common Headers
```http
Content-Type: application/json
Accept: application/json
```

### Example API Calls

#### 1. Get Recommendations

**cURL**:
```bash
curl "http://localhost:5000/api/recommend/1?strategy=auto&limit=5"
```

**Python**:
```python
import requests

response = requests.get(
    'http://localhost:5000/api/recommend/1',
    params={'strategy': 'auto', 'limit': 5}
)
data = response.json()
```

**JavaScript**:
```javascript
fetch('/api/recommend/1?strategy=auto&limit=5')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "alice_j",
    "email": "alice@example.com"
  },
  "recommendations": [
    {
      "product": {
        "id": 5,
        "name": "Apple iPad Pro",
        "price": 799.99,
        "rating": 4.5
      },
      "score": 0.89,
      "explanation": "AI-generated explanation...",
      "reasons": ["similar_users", "matched_categories"]
    }
  ],
  "count": 5,
  "strategy_used": "hybrid",
  "gemini_enabled": true
}
```

#### 2. Get Similar Products

**cURL**:
```bash
curl "http://localhost:5000/api/similar/5?limit=5"
```

**Response**:
```json
{
  "success": true,
  "product": {
    "id": 5,
    "name": "Apple iPad Pro"
  },
  "similar_products": [
    {
      "id": 12,
      "name": "Samsung Galaxy Tab",
      "similarity": 0.85
    }
  ]
}
```

#### 3. Get Products

**cURL**:
```bash
curl "http://localhost:5000/api/products?category=Electronics&page=1"
```

#### 4. Get System Stats

**cURL**:
```bash
curl "http://localhost:5000/api/stats"
```

**Response**:
```json
{
  "products": 50,
  "users": 20,
  "interactions": 500,
  "recommendations_generated": 1234
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: "Module not found" Error

**Problem**: Missing Python packages

**Solution**:
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### Issue 2: Database Not Found

**Problem**: Database file missing

**Solution**:
```bash
# Populate database
python scripts/populate_data.py
```

#### Issue 3: Port 5000 Already in Use

**Problem**: Another application using port 5000

**Solution**:
```bash
# Option 1: Stop other application
# Option 2: Use different port
# Edit app.py, change:
# app.run(debug=True, host='0.0.0.0', port=5001)
```

#### Issue 4: Gemini API Not Working

**Problem**: Invalid or missing API key

**Solution**:
1. Check `.env` file has correct key
2. Verify key at https://makersuite.google.com/app/apikey
3. System works without key (uses fallback explanations)

**Check Gemini Status**:
```bash
curl http://localhost:5000/api/gemini/test
```

#### Issue 5: No Recommendations Generated

**Problem**: Insufficient data

**Solution**:
```bash
# Re-populate database with more data
python scripts/populate_data.py
```

#### Issue 6: Static Files Not Loading

**Problem**: CSS/JS not loading

**Solution**:
1. Check `app/static/` folder exists
2. Clear browser cache (Ctrl+Shift+Del)
3. Hard refresh page (Ctrl+F5)

#### Issue 7: Slow Performance

**Problem**: Recommendations taking too long

**Solution**:
1. Reduce `limit` parameter (use 5 instead of 15)
2. Check database size
3. Restart Flask server

### Debug Mode

Enable detailed error messages:

```python
# In app.py
app.run(debug=True)
```

**View Logs**:
- Check terminal where Flask is running
- Look for error stack traces

### Getting Help

1. **Check Logs**: Terminal output has detailed errors
2. **Test API**: Use `/health` endpoint to verify system
3. **Integration Tests**: Run `python scripts/test_integration.py`
4. **GitHub Issues**: Report bugs on repository
5. **Documentation**: Re-read relevant sections

---

## ❓ FAQs

### General Questions

**Q: Do I need a Gemini API key?**
A: No, the system works without it using fallback explanations. However, Gemini provides better, more personalized explanations.

**Q: How do I get a Gemini API key?**
A: Visit https://makersuite.google.com/app/apikey, sign in, and create a free API key.

**Q: Is this system production-ready?**
A: It's a demonstration system. For production, add authentication, use PostgreSQL, implement caching, and add monitoring.

**Q: Can I add my own products?**
A: Yes! Edit `scripts/populate_data.py` or use the API to add products programmatically.

**Q: How accurate are the recommendations?**
A: With the sample data, accuracy is good. Real-world accuracy depends on:
- Amount of user interaction data
- Quality of product metadata
- Diversity of user preferences

### Technical Questions

**Q: What database does it use?**
A: SQLite for development. Can be switched to PostgreSQL, MySQL, etc.

**Q: Can I use this with my e-commerce site?**
A: Yes! Integrate via the REST API. See API Documentation section.

**Q: How are recommendations calculated?**
A: See "Understanding Recommendations" section above for detailed explanations.

**Q: What's the response time for recommendations?**
A: Typically < 500ms for 5 recommendations, including AI explanations.

**Q: Can it handle concurrent users?**
A: Yes, Flask can handle multiple users. For high traffic, use production WSGI server (Gunicorn, uWSGI).

**Q: Is the AI explanation real or template?**
A: If Gemini is enabled, explanations are AI-generated and unique. Otherwise, intelligent fallback templates are used.

### Development Questions

**Q: How do I add a new recommendation strategy?**
A: Create a new service class inheriting from base recommendation service, implement `recommend_products()` method.

**Q: Can I customize the UI?**
A: Yes! Edit templates in `app/templates/` and stylesheets in `app/static/css/`.

**Q: How do I add a new API endpoint?**
A: Add a new route in `app.py`:
```python
@app.route('/api/new-endpoint')
def new_endpoint():
    return jsonify({'message': 'New endpoint'})
```

**Q: Can I use a different AI model?**
A: Yes! Create a new service similar to `GeminiService` and implement the same interface.

---

## 📞 Support & Resources

### Documentation
- **README.md**: Installation and setup
- **USER_GUIDE.md**: This guide
- **API Docs**: See README.md API section
- **Code Comments**: Inline documentation

### Community
- **GitHub Issues**: Report bugs
- **GitHub Discussions**: Ask questions
- **Pull Requests**: Contribute improvements

### Learning Resources
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Gemini API**: https://ai.google.dev/
- **Recommendation Systems**: Research papers on collaborative filtering

---

## 🎉 Tips for Success

1. **Start Simple**: Begin with the web interface before using the API
2. **Try Different Strategies**: Compare results from different recommendation approaches
3. **Read AI Explanations**: Understand WHY products are recommended
4. **Explore Products**: Use filters and search to understand the catalog
5. **Check Statistics**: Monitor system performance on the About page
6. **Experiment**: Try different users, strategies, and limits
7. **Read the Code**: Well-commented code is great for learning
8. **Run Tests**: Integration tests show what's working

---

## 🚀 Next Steps

After mastering the basics:

1. **Add Your Own Data**: Customize products and users
2. **Integrate with Real Site**: Use the API
3. **Enhance UI**: Customize templates and styles
4. **Add Features**: User profiles, wishlists, etc.
5. **Deploy**: Put it in production
6. **Monitor**: Track performance and accuracy
7. **Iterate**: Improve based on user feedback

---

**Happy Recommending! 🎯**

Need help? Check the Troubleshooting section or open an issue on GitHub.
