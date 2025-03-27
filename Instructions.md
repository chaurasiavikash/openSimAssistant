# GitHub Repository Setup Instructions

Follow these steps to create and upload your OpenSim RAG Assistant to GitHub.

## 1. Prepare Your Local Project

First, organize your project files:

```bash
# Create directory structure for GitHub
mkdir -p data static/images templates

# Create .gitkeep files to preserve empty directories
touch data/.gitkeep static/.gitkeep static/images/.gitkeep templates/.gitkeep

# Create .gitignore file
cat > .gitignore << 'EOL'
# Virtual environment
venv/
opensim-rag-env/
env/
.env

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Database files
opensim_chroma_db/
chroma_db/

# Downloaded files
data/opensim_docs.json

# Generated templates
templates/index.html

# Generated images
static/images/opensim_logo.png
static/favicon.ico

# Logs
*.log

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
EOL

# If you don't already have a LICENSE file, create one (MIT example)
cat > LICENSE << 'EOL'
MIT License

Copyright (c) 2023 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOL
```

## 2. Create a New GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., "opensim-rag")
4. Add a short description: "A Retrieval Augmented Generation (RAG) system for OpenSim biomechanics software"
5. Choose "Public" visibility (or Private if you prefer)
6. Do NOT initialize with README, .gitignore, or license (we'll add these ourselves)
7. Click "Create repository"

## 3. Initialize Git and Push to GitHub

Once your repository is created, GitHub will show instructions. Follow these commands:

```bash
# Initialize Git repository (if not already done)
git init

# Add all your files
git add .

# Commit your files
git commit -m "Initial commit: OpenSim RAG Assistant"

# Add the GitHub repository as remote
git remote add origin https://github.com/yourusername/opensim-rag.git

# Push your code to GitHub
git push -u origin main
```

**Note**: If you get an error about `main` branch, try using `master` instead:
```bash
git push -u origin master
```

Or create the main branch first:
```bash
git branch -M main
git push -u origin main
```

## 4. Verify Your Repository

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md will be displayed on the main page
4. Make sure the directory structure is preserved

## 5. Update Repository Settings (Optional)

1. Go to "Settings" in your repository
2. Under "General":
   - Enable "Discussions" if you want to allow users to ask questions
   - Enable "Issues" for bug reports and feature requests
3. Under "Pages":
   - You can set up GitHub Pages to host documentation if needed

## 6. Create a Release (Optional)

1. Go to "Releases" in your repository
2. Click "Create a new release"
3. Tag version: "v1.0.0"
4. Release title: "Initial Release: OpenSim RAG Assistant"
5. Add release notes describing the features
6. Click "Publish release"

Your OpenSim RAG Assistant is now available on GitHub for others to use and contribute to!
