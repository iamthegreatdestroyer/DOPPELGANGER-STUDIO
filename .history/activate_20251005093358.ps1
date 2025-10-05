# DOPPELGANGER STUDIO™ - Virtual Environment Activation Script
# Quick activation script for PowerShell

Write-Host ""
Write-Host "🎬 DOPPELGANGER STUDIO™" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""

# Check if Python is using venv (more reliable than $VIRTUAL_ENV)
$pythonPath = python -c "import sys; print(sys.prefix)"
if ($pythonPath -like "*\.venv*") {
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    Write-Host "📍 Location: $pythonPath" -ForegroundColor DarkGray
    Write-Host ""
    
    # Show Python version
    Write-Host "🐍 Python:" -ForegroundColor Cyan
    python --version
    Write-Host ""
    
    # Show key packages
    Write-Host "📦 Key packages:" -ForegroundColor Cyan
    pip list --format=columns | Select-String -Pattern "anthropic|openai|pymongo|fastapi|pytest|aiohttp|beautifulsoup|Wikipedia" -Context 0,0
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🚀 Ready to create magic!" -ForegroundColor Magenta
    Write-Host ""
} else {
    Write-Host "❌ Virtual environment not detected" -ForegroundColor Red
    Write-Host "Python is using: $pythonPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try manual activation: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
}
