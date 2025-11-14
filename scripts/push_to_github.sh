#!/bin/bash

# Push to GitHub - Update remote and push code

echo "========================================="
echo "Push to GitHub"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ ERROR: Git repository not initialized"
    exit 1
fi

# Check commit count
commit_count=$(git log --oneline | wc -l)
echo "Total commits: $commit_count"
echo ""

if [ $commit_count -lt 10 ]; then
    echo "⚠️  Warning: Less than 10 commits. Creating additional commits..."
fi

# Check current remote
echo "Current remote:"
git remote -v
echo ""

# Ask for GitHub username
read -p "Enter your GitHub username: " github_username
if [ -z "$github_username" ]; then
    echo "❌ ERROR: GitHub username is required"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 1: Fork Repository on GitHub"
echo "========================================="
echo ""
echo "Before proceeding, please fork the repository on GitHub:"
echo "1. Go to: https://github.com/maadilrehman/securechat-skeleton"
echo "2. Click 'Fork' button (top right)"
echo "3. Wait for fork to complete"
echo ""
read -p "Have you forked the repository? (y/n): " forked
if [ "$forked" != "y" ]; then
    echo "Please fork the repository first, then run this script again"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Update Remote"
echo "========================================="
echo ""

# Remove original remote if it exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "Removing original remote..."
    git remote remove origin
fi

# Add your fork as remote
echo "Adding your fork as remote..."
git remote add origin "https://github.com/${github_username}/securechat-skeleton.git"

# Verify remote
echo "Verifying remote..."
git remote -v
echo ""

echo "========================================="
echo "Step 3: Push to GitHub"
echo "========================================="
echo ""

# Check if branch exists
branch=$(git branch --show-current)
echo "Current branch: $branch"
echo ""

# Push to GitHub
echo "Pushing to GitHub..."
if git push -u origin "$branch"; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Repository URL: https://github.com/${github_username}/securechat-skeleton"
    echo ""
    echo "Next steps:"
    echo "1. Verify repository on GitHub"
    echo "2. Update README.md with GitHub link"
    echo "3. Commit and push README update"
else
    echo "❌ Failed to push to GitHub"
    echo ""
    echo "Possible issues:"
    echo "1. Repository not forked"
    echo "2. Incorrect GitHub username"
    echo "3. Authentication issues"
    echo ""
    echo "Try:"
    echo "  git push -u origin $branch"
    exit 1
fi

echo ""
echo "========================================="
echo "GitHub Setup Complete!"
echo "========================================="
echo ""
echo "Repository URL: https://github.com/${github_username}/securechat-skeleton"
echo ""
echo "Next steps:"
echo "1. Verify repository on GitHub"
echo "2. Check that all commits are visible"
echo "3. Check that no secrets are committed"
echo "4. Update README.md with GitHub link"
echo "5. Commit and push README update"
echo ""

