@echo off
chcp 65001 >nul
title Push OpenWrt NC-1812 to GitHub

echo ============================================
echo  Push OpenWrt NC-1812 to GitHub
echo ============================================
echo.

set /p GITHUB_USER="GitHub username: "
if "%GITHUB_USER%"=="" exit /b

set REPO_NAME=zona404-openwrt

echo.
echo 1. Creating repo "%REPO_NAME%" on GitHub...
echo    (enter your GitHub PAT or password when prompted)
echo.

git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
git branch -M main
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Push failed. Possible reasons:
    echo   - Repo doesn't exist yet: create at https://github.com/new
    echo   - Not authenticated: use a Personal Access Token instead of password
    echo     Generate at: https://github.com/settings/tokens
    echo.
    pause
    exit /b
)

echo.
echo [OK] Pushed successfully!
echo URL: https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo Next: go to Actions tab and run the workflow.
echo.
pause
