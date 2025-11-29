# FinCA AI Application Launcher (PowerShell)
# This script activates the virtual environment and runs the Streamlit app

param(
    [int]$Port = 8506
)

Write-Host "🚀 Starting FinCA AI..." -ForegroundColor Green
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if venv exists
$VenvPath = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvPath)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Then: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
try {
    & $VenvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate virtual environment"
    }
} catch {
    Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Virtual environment activated successfully" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 Starting Streamlit app on port $Port..." -ForegroundColor Blue
Write-Host "URL: http://localhost:$Port" -ForegroundColor Blue
Write-Host ""
Write-Host "📝 Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

# Run the Streamlit app
try {
    & streamlit run src/ui/app_integrated.py --server.port $Port --server.headless true
} finally {
    # Deactivate venv when done
    Write-Host ""
    Write-Host "🔄 Deactivating virtual environment..." -ForegroundColor Cyan
    & (Join-Path $ScriptDir "venv\Scripts\deactivate.bat")
}