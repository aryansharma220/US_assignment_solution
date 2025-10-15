# ShopSmart AI - Intelligent E-commerce Recommendation System

🧠 **Production-Ready AI-Powered E-commerce Platform**

A complete Flask application featuring intelligent product recommendations using machine learning algorithms and Google's Gemini AI for natural language explanations.

## ✨ Key Features

- **🤖 Multiple Recommendation Strategies**: Collaborative filtering, content-based, and hybrid approaches
- **💬 AI-Powered Explanations**: Natural language insights powered by Google Gemini
- **🇮🇳 Indian E-commerce Focus**: 50+ realistic products, INR pricing, local brands
- **📱 Modern Responsive UI**: Clean, professional design that works on all devices
- **� Complete REST API**: 11 endpoints with comprehensive functionality
- **⚡ Production-Ready**: Multi-environment configuration, security, performance optimized
- **📊 Real-time Analytics**: Live statistics and user interaction tracking

## 🏗️ Technology Stack

**Backend:**
- **Python 3.8+** with Flask 3.0.0
- **SQLAlchemy 2.0+** for database management
- **NumPy & Pandas** for data processing
- **Scikit-learn** for ML algorithms
- **Google Generative AI** for Gemini integration

**Frontend:**
- **HTML5, CSS3, Vanilla JavaScript**
- **Responsive design** with modern UI/UX
- **Font Awesome** icons & **Google Fonts**

**Database:**
- **SQLite** (development) / **PostgreSQL** (production)
- 20 users, 50+ products, 150+ interactions

**Features:**
- Multi-environment configuration (dev/test/prod)
- Security best practices (CSRF, environment variables)
- RESTful API with comprehensive error handling
- Production-ready with Gunicorn support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ and pip
- Google Gemini API key (optional - system works without it)

### Installation

1. **Clone & Setup**
   ```bash
   git clone <repository-url>
   cd US
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux  
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and optionally add: GEMINI_API_KEY=your_key_here
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_database.py
   ```

5. **Start Application**
   ```bash
   python app.py
   ```

6. **Open Browser**
   
   Navigate to: http://localhost:5000

### Production Deployment

**Windows:**
```bash
.\start_production.bat
```

**Linux/macOS:**
```bash
./start_production.sh
```

## 🔑 Getting Gemini API Key (Optional)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in and create an API key
3. Add to your `.env` file:
   ```ini
   GEMINI_API_KEY=your_actual_api_key_here
   ```
4. Restart the application

**Note:** System works perfectly without the API key using intelligent fallback explanations.

## 📡 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /api/stats` - Database statistics  
- `GET /api/products` - List products (with pagination, filtering)
- `GET /api/users` - List users
- `GET /api/recommend/{user_id}` - Get recommendations
- `GET /api/similar/{product_id}` - Find similar products

### Example API Calls
```bash
# Health check
curl http://localhost:5000/health

# Get recommendations
curl "http://localhost:5000/api/recommend/1?strategy=auto&limit=5"

# Get statistics
curl http://localhost:5000/api/stats
```

### Response Format
```json
{
  "success": true,
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
  "strategy_used": "hybrid",
  "gemini_enabled": true
}

## 🎯 Usage Examples

### Web Interface
- **Home Page** (`/`) - System statistics and overview
- **Recommendations** (`/recommendations`) - AI-powered product suggestions  
- **Products** (`/products`) - Browse catalog with filters and search
- **About** (`/about`) - Learn about the technology

### Python API Usage
```python
import requests

# Get recommendations
response = requests.get(
    'http://localhost:5000/api/recommend/1',
    params={'strategy': 'auto', 'limit': 5}
)
recommendations = response.json()

# Get similar products  
response = requests.get(
    'http://localhost:5000/api/similar/5',
    params={'limit': 5}
)
similar = response.json()
```

## 🧪 Testing

Run the database initialization script to verify setup:
```bash
python scripts/init_database.py
```

Test the application:
1. Visit `http://localhost:5000`
2. Navigate through all pages
3. Select users and get recommendations
4. Test API endpoints with curl

## 📊 Project Statistics

- **7,500+ lines of code** (Python, HTML, CSS, JavaScript)
- **50+ products** across multiple categories
- **20 users** with realistic interaction data
- **11 REST API endpoints** with comprehensive functionality
- **Production-ready** with multi-environment configuration
- **Security hardened** with CSRF protection and environment variables

## 🚀 Production Deployment

Ready for production! The application includes:

- Multi-environment configuration (development/production/testing)
- Security best practices
- Production startup scripts
- Database migration support
- Gunicorn WSGI server integration

Use the provided scripts:
- `start_production.bat` (Windows)
- `start_production.sh` (Linux/macOS)

## 🤝 Contributing

This project demonstrates:
- Full-stack web development
- Machine learning integration
- REST API design
- Modern Python development
- Responsive frontend design

Feel free to fork, modify, or use as learning material.

## 📄 License

MIT License - Free to use for educational and commercial purposes.

---

<div align="center">

**🧠 ShopSmart AI - Production-Ready E-commerce Recommendations**

⭐ **Start with: `python app.py`** ⭐

Made with ❤️ using Python, Flask, and AI

</div>
