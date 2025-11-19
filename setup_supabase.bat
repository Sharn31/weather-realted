@echo off
REM Supabase Setup Script for Windows Command Prompt
REM This script helps you set up Supabase environment variables

echo === Supabase Environment Setup ===
echo.

set /p SUPABASE_URL="https://nwweilelmzickmmmmhmb.supabase.co"
set /p SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VpbGVsbXppY2ttbW1taG1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MjY3MjksImV4cCI6MjA3OTEwMjcyOX0.Vq99eRVvSYwj-sehc193U1nnL2EvlvE1MaCMjEeqq3s"

echo.
echo Environment variables set for current session:
echo SUPABASE_URL = %SUPABASE_URL%
echo SUPABASE_KEY = %SUPABASE_KEY%
echo.

set /p SET_PERMANENT="Do you want to set these permanently? (y/n): "
if /i "%SET_PERMANENT%"=="y" (
    setx SUPABASE_URL "%SUPABASE_URL%"
    setx SUPABASE_KEY "%SUPABASE_KEY%"
    echo Environment variables set permanently!
) else (
    echo Environment variables are set for this session only.
    echo To set permanently, run this script again and choose 'y', or set them manually in System Properties.
)

echo.
echo Setup complete! You can now run your Flask application.
echo Note: If you set them for this session only, restart your terminal/IDE to use them.
pause

