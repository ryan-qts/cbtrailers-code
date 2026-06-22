# C&B Trailers GitHub Setup Script
# Run this once from the "set up github" folder in PowerShell:
#   cd "C:\Users\jerem\Claude\Projects\set up github"
#   .\setup-git.ps1

$repoPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoPath

Write-Host "Setting up git repo..." -ForegroundColor Cyan

# Remove broken .git if present
if (Test-Path ".git") {
    Remove-Item -Recurse -Force ".git"
    Write-Host "Removed old .git folder" -ForegroundColor Yellow
}

# Init with main branch
git init -b main
git config user.email "ryang@qtsidaho.com"
git config user.name "Ryan Gonzales"

# Set remote
git remote add origin https://github.com/ryan-qts/cbtrailers-code.git

# Stage everything
git add .

# Initial commit
git commit -m "Initial commit: add scraping projects and repo setup"

Write-Host ""
Write-Host "Ready to push! Run:" -ForegroundColor Green
Write-Host "  git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "You'll be prompted for your GitHub username + a Personal Access Token." -ForegroundColor Gray
Write-Host "Create a token at: https://github.com/settings/tokens (needs 'repo' scope)" -ForegroundColor Gray
