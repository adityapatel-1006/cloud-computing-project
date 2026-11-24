# Automated GitHub Push Script for Cloud-Based Student Management System
# Student: Aditya Patel (3CSE23) - IILM University

param(
    [string]$Username = ""
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   PUSHING PROJECT TO PUBLIC GITHUB REPOSITORY                  " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check if Git is installed
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    # Check standard install path
    if (Test-Path "C:\Program Files\Git\cmd\git.exe") {
        $env:Path += ";C:\Program Files\Git\cmd"
        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    }
}

if (-not $gitCmd) {
    Write-Host "[!] Git is not yet installed on this computer." -ForegroundColor Yellow
    Write-Host "    Installing Git via winget now..." -ForegroundColor Green
    winget install --id Git.Git -e --source winget
    Write-Host ""
    Write-Host "[*] Git has been installed! Please close and reopen this PowerShell window," -ForegroundColor Cyan
    Write-Host "    then run .\push_to_github.ps1 again to push." -ForegroundColor Cyan
    pause
    exit
}

# 2. Get GitHub Username
if (-not $Username) {
    $Username = Read-Host "Enter your GitHub Username"
}

if (-not $Username) {
    Write-Host "[!] Username cannot be empty." -ForegroundColor Red
    exit
}

$repoName = "Cloud-Based-Student-Management-System"
$remoteUrl = "https://github.com/$Username/$repoName.git"

Write-Host ""
Write-Host "[1/5] Target Repository: $remoteUrl" -ForegroundColor Green
Write-Host "      Ensure you created this PUBLIC repository at https://github.com/new" -ForegroundColor Yellow

# 3. Configure local Git identity if needed
$currentEmail = git config user.email
if (-not $currentEmail) {
    git config --global user.name "Aditya Patel"
    git config --global user.email "$Username@users.noreply.github.com"
}

# 4. Initialize and Commit
Write-Host "[2/5] Initializing Git repository..." -ForegroundColor Green
if (-not (Test-Path ".git")) {
    git init
}

Write-Host "[3/5] Staging all files..." -ForegroundColor Green
git add .

Write-Host "[4/5] Committing project files..." -ForegroundColor Green
git commit -m "Submit Cloud-Based Student Management System - Aditya Patel (3CSE23) - IILM University" -q

# 5. Push to GitHub
Write-Host "[5/5] Pushing to main branch on GitHub..." -ForegroundColor Green
git branch -M main

$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

git push -u origin main

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  SUCCESSFULLY PUSHED TO GITHUB!" -ForegroundColor Green
Write-Host "  View your public repository at:" -ForegroundColor Cyan
Write-Host "  https://github.com/$Username/$repoName" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
