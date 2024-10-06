#!/bin/bash

# Step 1: Run vite build
echo "Running vite build..."
if vite build; then
  echo "Vite build successful."
else
  echo "Vite build failed. Exiting."
  exit 1
fi
echo "Checking for changes to commit..."
if git diff-index --quiet HEAD --; then
  echo "No changes to commit. Skipping commit."
else
  if git commit -a; then
    echo "Git commit successful."
  else
    echo "Git commit failed. Exiting."
    exit 1
  fi
fi

# Step 3: Push changes to remote
echo "Pushing changes to remote..."
if git push; then
  echo "Git push successful."
else
  echo "Git push failed. Exiting."
  exit 1
fi
