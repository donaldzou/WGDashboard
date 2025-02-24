#!/bin/bash

set -e  # Exit script on any command failure

# Check if Vite is installed
if ! command -v vite &>/dev/null; then
  echo "[ERROR] Vite is not installed. Please install it before running this script."
  exit 1
fi

# Check if Git is installed
if ! command -v git &>/dev/null; then
  echo "[ERROR] Git is not installed. Please install it before running this script."
  exit 1
fi

# Run Vite build
echo "Running Vite build..."
vite build
echo "[SUCCESS] Vite build completed."

# Check if there are uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Changes detected. Committing..."
  
  git add .
  git commit -m "Automated build commit at $(date '+%Y-%m-%d %H:%M:%S')"
  echo "[SUCCESS] Git commit successful."
else
  echo "[INFO] No changes to commit. Skipping commit."
fi

# Push changes to remote repository
echo "Pushing changes..."
git push origin "$(git rev-parse --abbrev-ref HEAD)"
echo "[SUCCESS] Changes pushed successfully."
