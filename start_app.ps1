# Start Flask App with Supabase Environment Variables
# This script sets the environment variables and starts your Flask application

Write-Host "Setting Supabase environment variables..." -ForegroundColor Cyan

# Set Supabase credentials
$env:SUPABASE_URL = "https://nwweilelmzickmmmmhmb.supabase.co"
$env:SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VpbGVsbXppY2ttbW1taG1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MjY3MjksImV4cCI6MjA3OTEwMjcyOX0.Vq99eRVvSYwj-sehc193U1nnL2EvlvE1MaCMjEeqq3s"

Write-Host "SUPABASE_URL: $env:SUPABASE_URL" -ForegroundColor Green
Write-Host "SUPABASE_KEY: $($env:SUPABASE_KEY.Substring(0,20))..." -ForegroundColor Green
Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host ""

# Start Flask app
python app.py

