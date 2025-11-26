# Install RAG Dependencies for FinCA AI
# Run this script to install all required packages for the Knowledge Base feature

Write-Host "=" -NoNewline
Write-Host ("=" * 60)
Write-Host "Installing RAG Dependencies for FinCA AI Knowledge Base"
Write-Host "=" -NoNewline
Write-Host ("=" * 60)
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
}

Write-Host "✅ Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing RAG packages..." -ForegroundColor Cyan
Write-Host ""

$packages = @(
    "chromadb==0.4.22",
    "sentence-transformers==2.3.1",
    "pypdf==4.0.1",
    "unstructured==0.11.8"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Yellow
    & python -m pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install $package" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline
Write-Host ("=" * 60)
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 60)
Write-Host ""

Write-Host "🧪 Running test script..." -ForegroundColor Cyan
Write-Host ""

& python test_rag.py

Write-Host ""
Write-Host "=" -NoNewline
Write-Host ("=" * 60)
Write-Host "🚀 To start the app, run:" -ForegroundColor Cyan
Write-Host "   streamlit run src/ui/app_integrated.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Then navigate to 'Knowledge Base' in the sidebar!" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 60)
