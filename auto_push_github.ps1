# Script tự động đưa lên GitHub
param(
    [string]$GitHubUsername = "",
    [string]$RepositoryName = "autoclick"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUTO PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
$hasGh = $false
try {
    $ghVersion = gh --version 2>$null
    if ($ghVersion) {
        $hasGh = $true
        Write-Host "GitHub CLI found!" -ForegroundColor Green
    }
} catch {
    Write-Host "GitHub CLI not found, will use manual method" -ForegroundColor Yellow
}

if ($hasGh) {
    Write-Host "Using GitHub CLI to create repository..." -ForegroundColor Cyan
    
    # Check if logged in
    try {
        gh auth status 2>$null
        Write-Host "GitHub CLI is authenticated" -ForegroundColor Green
        
        # Create repository
        Write-Host "Creating repository '$RepositoryName' on GitHub..." -ForegroundColor Cyan
        gh repo create $RepositoryName --public --description "Auto Click - Automatic Mouse and Keyboard with image recognition and if-else scripting" --source=. --remote=origin --push
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "SUCCESS!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repository created and pushed to:" -ForegroundColor White
        $repoUrl = gh repo view $RepositoryName --json url -q .url
        Write-Host $repoUrl -ForegroundColor Cyan
        Write-Host ""
        
    } catch {
        Write-Host "Error: Not logged in to GitHub CLI" -ForegroundColor Red
        Write-Host "Please run: gh auth login" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Or use manual method below" -ForegroundColor Yellow
        $hasGh = $false
    }
}

if (-not $hasGh) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "MANUAL METHOD" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Step 1: Create repository on GitHub" -ForegroundColor White
    Write-Host "   Go to: https://github.com/new" -ForegroundColor Cyan
    Write-Host "   Repository name: $RepositoryName" -ForegroundColor Cyan
    Write-Host "   Description: Auto Click - Automatic Mouse and Keyboard" -ForegroundColor Cyan
    Write-Host "   DO NOT initialize with README" -ForegroundColor Yellow
    Write-Host "   Click 'Create repository'" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $GitHubUsername) {
        $GitHubUsername = Read-Host "Enter your GitHub username"
    }
    
    Write-Host "Step 2: Adding remote and pushing..." -ForegroundColor Cyan
    
    # Remove existing remote if any
    git remote remove origin 2>$null
    
    # Add remote
    $remoteUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
    git remote add origin $remoteUrl
    
    Write-Host "Remote added: $remoteUrl" -ForegroundColor Green
    
    # Push
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push -u origin main
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository is now at:" -ForegroundColor White
    Write-Host "https://github.com/$GitHubUsername/$RepositoryName" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

