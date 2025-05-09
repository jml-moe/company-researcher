#!/bin/bash

# Company Researcher Git Push Script

echo "🔍 Checking changes..."
git status

echo ""
echo "📋 Adding changes..."
git add .

echo ""
echo "💬 Enter commit message:"
read commit_message

echo ""
echo "🚀 Committing changes with message: '$commit_message'"
git commit -m "$commit_message"

echo ""
echo "⬆️ Pushing to remote repository..."
git push

echo ""
echo "✅ Done!" 