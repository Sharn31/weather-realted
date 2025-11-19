# Supabase Setup Script for Windows PowerShell
# This script helps you set up Supabase environment variables

Write-Host "=== Supabase Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Get Supabase URL
$supabaseUrl = Read-Host "https://nwweilelmzickmmmmhmb.supabase.co"

# Validate URL format
if ($supabaseUrl -notmatch "^https://.*\.supabase\.co$") {
    Write-Host "Warning: URL doesn't match expected Supabase format" -ForegroundColor Yellow
}

# Get Supabase Key
$supabaseKey = Read-Host "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VpbGVsbXppY2ttbW1taG1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MjY3MjksImV4cCI6MjA3OTEwMjcyOX0.Vq99eRVvSYwj-sehc193U1nnL2EvlvE1MaCMjEeqq3s"

# Validate key format (should start with eyJ)
if ($supabaseKey -notmatch "^eyJ") {
    Write-Host "Warning: Key doesn't match expected format (should start with 'eyJ')" -ForegroundColor Yellow
}

# Set environment variables for current session
$env:SUPABASE_URL = $supabaseUrl
$env:SUPABASE_KEY = $supabaseKey

Write-Host ""
Write-Host "Environment variables set for current session:" -ForegroundColor Green
Write-Host "SUPABASE_URL = $supabaseUrl" -ForegroundColor Gray
Write-Host "SUPABASE_KEY = $supabaseKey" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to set permanently
$setPermanent = Read-Host "Do you want to set these permanently? (y/n)"
if ($setPermanent -eq "y" -or $setPermanent -eq "Y") {
    [System.Environment]::SetEnvironmentVariable("SUPABASE_URL", $supabaseUrl, "User")
    [System.Environment]::SetEnvironmentVariable("SUPABASE_KEY", $supabaseKey, "User")
    Write-Host "Environment variables set permanently!" -ForegroundColor Green
} else {
    Write-Host "Environment variables are set for this session only." -ForegroundColor Yellow
    Write-Host "To set permanently, run this script again and choose 'y', or set them manually in System Properties." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! You can now run your Flask application." -ForegroundColor Green
Write-Host "Note: If you set them for this session only, restart your terminal/IDE to use them." -ForegroundColor Yellow

