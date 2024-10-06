#!/bin/bash
echo "Running vite build..."
if vite build; then
  echo "Vite build successful."
else
  echo "Vite build failed. Exiting."
  exit 1
fi
echo "Checking for changes to commit..."
if git diff-index --quiet HEAD --; then
  
  if git commit -a; then
      echo "Git commit successful."
    else
      echo "Git commit failed. Exiting."
      exit 1
    fi
else
  echo "No changes to commit. Skipping commit."
fi
echo "Pushing changes to remote..."
if git push; then
  echo "Git push successful."
else
  echo "Git push failed. Exiting."
  exit 1
fi
