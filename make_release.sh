#!/bin/bash

# Check if version part (major, minor, patch) is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [major|minor|patch]"
    exit 1
fi

# Bump version
bump2version --allow-dirty $1

# Extract the current version from pyproject.toml (assuming it's there)
# It uses Python to parse the TOML file and extract the version
new_version=$(python -c "import toml; print(toml.load('pyproject.toml')['tool']['poetry']['version'])")

# Build docs
cd docs
make clean
make html
make latexpdf
cd ..

# Build and publish package
poetry build
poetry publish

# Update changelog
# Replace 'v1.0.0' with the tag of the previous version or a commit hash
# to generate changelog from that point.
git log --pretty=format:"- %s" v1.0.0..HEAD >> CHANGELOG.md

# Commit, tag and push
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to $new_version"
git tag -a "$new_version" -m "Version $new_version"
git push origin main
git push origin --tags
