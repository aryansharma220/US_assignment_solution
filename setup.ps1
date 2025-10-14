# Installation script for E-commerce Product Recommender
# Run this script in PowerShell

Write-Host "🛍️  E-commerce Product Recommender - Setup Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📌 Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📌 Step 2: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  Virtual environment already exists. Skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "📌 Step 3: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "📌 Step 4: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✅ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📌 Step 5: Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
pip install -r requirements.txt --quiet
Write-Host "   ✅ All dependencies installed" -ForegroundColor Green

# Create .env file
Write-Host ""
Write-Host "📌 Step 6: Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ⚠️  .env file already exists. Skipping..." -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host "   ✅ .env file created from template" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Edit .env file and add your Gemini API key:" -ForegroundColor White
Write-Host "      notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Get your Gemini API key from:" -ForegroundColor White
Write-Host "      https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. Run the application:" -ForegroundColor White
Write-Host "      python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Access the API at:" -ForegroundColor White
Write-Host "      http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
