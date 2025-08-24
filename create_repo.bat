@echo off
echo ============================================
echo    Resume Adapter - GitHub Repository Setup
echo ============================================
echo.
echo Step 1: Creating GitHub repository manually...
echo.
echo Please follow these steps:
echo 1. Open: https://github.com/new
echo 2. Repository name: resume-adapter
echo 3. Description: AI-powered resume generation platform with intelligent parsing, role adaptation, and multiple template styles
echo 4. Make sure it's set to PRIVATE
echo 5. DO NOT initialize with README, .gitignore, or license (we have them)
echo 6. Click "Create repository"
echo.
pause
echo.
echo Step 2: After creating the repository, enter your GitHub username:
set /p USERNAME="GitHub username: "
echo.
echo Step 3: Setting up remote repository...
git remote add origin https://github.com/%USERNAME%/resume-adapter.git
git branch -M main
echo.
echo Step 4: Pushing to GitHub...
echo You'll be prompted for your GitHub credentials or token.
git push -u origin main
echo.
echo ============================================
echo    Repository setup complete!
echo    Your code is now on GitHub at:
echo    https://github.com/%USERNAME%/resume-adapter
echo ============================================
pause