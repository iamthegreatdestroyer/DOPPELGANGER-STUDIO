# DOPPELGANGER STUDIO™ - Virtual Environment Activation Script
# Quick activation script for PowerShell

Write-Host "🎬 Activating DOPPELGANGER STUDIO virtual environment..." -ForegroundColor Cyan

# Activate the virtual environment
& ".\\.venv\Scripts\Activate.ps1"

# Verify activation
if ($VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
    Write-Host "📍 Location: $VIRTUAL_ENV" -ForegroundColor Yellow
    Write-Host ""
    
    # Show Python version
    Write-Host "🐍 Python version:" -ForegroundColor Cyan
    python --version
    Write-Host ""
    
    # Show key packages
    Write-Host "📦 Key packages installed:" -ForegroundColor Cyan
    pip list --format=columns | Select-String -Pattern "anthropic|openai|pymongo|fastapi|pytest|aiohttp|beautifulsoup|Wikipedia" -Context 0,0
    Write-Host ""
    
    Write-Host "🚀 Ready to create magic!" -ForegroundColor Magenta
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Try running manually: .\\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}
