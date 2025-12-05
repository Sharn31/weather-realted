# Vercel Deployment Script for PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vercel Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue

if (-not $vercelInstalled) {
    Write-Host "Vercel CLI is not installed!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    
    try {
        npm install -g vercel
        if ($LASTEXITCODE -ne 0) {
            throw "Installation failed"
        }
        Write-Host ""
        Write-Host "Vercel CLI installed successfully!" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host ""
        Write-Host "ERROR: Failed to install Vercel CLI" -ForegroundColor Red
        Write-Host "Please install Node.js first from https://nodejs.org/" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check login status
Write-Host "Checking Vercel login status..." -ForegroundColor Yellow
$whoami = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "You are not logged in to Vercel." -ForegroundColor Yellow
    Write-Host "Please login..." -ForegroundColor Yellow
    vercel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Login failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Deployment..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Deploy to production
Write-Host "Deploying to Vercel (Production)..." -ForegroundColor Yellow
vercel --prod

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your app is now live on Vercel!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Deployment Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"

