# PowerShell script to setup and push to GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP GITHUB REPOSITORY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if already initialized
if (Test-Path ".git") {
    Write-Host "Git repository already initialized" -ForegroundColor Yellow
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Cyan
    git init
}

# Add all files
Write-Host "Adding files..." -ForegroundColor Cyan
git add .

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host "Committing changes..." -ForegroundColor Cyan
    git commit -m "Initial commit: Auto Click application with image recognition, if-else scripting, and advanced features"
} else {
    Write-Host "No changes to commit" -ForegroundColor Yellow
}

# Set branch to main
Write-Host "Setting branch to main..." -ForegroundColor Cyan
git branch -M main

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create a repository on GitHub:" -ForegroundColor White
Write-Host "   Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "   Repository name: autoclick" -ForegroundColor Cyan
Write-Host "   Description: Auto Click - Automatic Mouse and Keyboard" -ForegroundColor Cyan
Write-Host "   DO NOT initialize with README" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. After creating repository, run:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/autoclick.git" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use the push_to_github.bat script" -ForegroundColor Green
Write-Host ""

