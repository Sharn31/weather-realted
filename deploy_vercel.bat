@echo off
echo ========================================
echo Vercel Deployment Script
echo ========================================
echo.

REM Check if Vercel CLI is installed
where vercel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Vercel CLI is not installed!
    echo.
    echo Installing Vercel CLI...
    call npm install -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install Vercel CLI
        echo Please install Node.js first from https://nodejs.org/
        pause
        exit /b 1
    )
    echo.
    echo Vercel CLI installed successfully!
    echo.
)

echo Checking Vercel login status...
vercel whoami >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo You are not logged in to Vercel.
    echo Please login...
    vercel login
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Login failed
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting Deployment...
echo ========================================
echo.

REM Deploy to production
echo Deploying to Vercel (Production)...
vercel --prod

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Deployment Successful!
    echo ========================================
    echo.
    echo Your app is now live on Vercel!
    echo.
) else (
    echo.
    echo ========================================
    echo Deployment Failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause

