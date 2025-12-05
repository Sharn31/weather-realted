@echo off
echo ========================================
echo Railway Deployment Script
echo ========================================
echo.

REM Check if Railway CLI is installed
where railway >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Railway CLI is not installed!
    echo.
    echo Installing Railway CLI...
    call npm install -g @railway/cli
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install Railway CLI
        echo Please install Node.js first from https://nodejs.org/
        pause
        exit /b 1
    )
    echo.
    echo Railway CLI installed successfully!
    echo.
)

echo Checking Railway login status...
railway whoami >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo You are not logged in to Railway.
    echo Please login...
    railway login
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

REM Check if already initialized
if not exist "railway.json" (
    echo Initializing Railway project...
    railway init
)

echo.
echo Deploying to Railway...
railway up

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Deployment Successful!
    echo ========================================
    echo.
    echo Your app is now live on Railway!
    echo.
    echo To view logs: railway logs
    echo To open in browser: railway open
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



