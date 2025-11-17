# PowerShell script to set Gemini API Key
# Run this script before starting your Flask app

$apiKey = "AIzaSyD-kyo84xEDpyV08VJGrHHJ6Kn99lQlfS8"
$env:GEMINI_API_KEY = $apiKey

Write-Host "✅ Gemini API Key has been set!" -ForegroundColor Green
Write-Host "You can now start your Flask app." -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the app, run: python app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Note: This API key is only set for this PowerShell session." -ForegroundColor Yellow
Write-Host "   If you open a new terminal, you'll need to run this script again." -ForegroundColor Yellow

