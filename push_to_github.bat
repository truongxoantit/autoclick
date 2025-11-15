@echo off
echo ========================================
echo PUSH TO GITHUB
echo ========================================
echo.

echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Please create a repository named 'autoclick' on GitHub first!
echo.
echo Go to: https://github.com/new
echo Repository name: autoclick
echo Description: Auto Click - Automatic Mouse and Keyboard with image recognition
echo Visibility: Public or Private (your choice)
echo.
echo DO NOT initialize with README, .gitignore, or license
echo.
pause

echo.
echo Step 3: Enter your GitHub username:
set /p GITHUB_USER=

echo.
echo Step 4: Adding remote origin...
git remote add origin https://github.com/%GITHUB_USER%/autoclick.git

echo.
echo Step 5: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Your repository is now at:
echo https://github.com/%GITHUB_USER%/autoclick
echo.
pause

