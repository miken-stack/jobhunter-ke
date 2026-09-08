import os

def create_jobhunter_structure():
    """
    Create the jobhunter-ke project directory structure
    """
    directories = [
        'app',
        'app/templates',
        'app/static',
        'app/static/css',
        'app/static/js',
        'tests',
    ]
    
    files = {
        'app/__init__.py': '',
        'app/models.py': '',
        'app/routes.py': '',
        'app/templates/base.html': '',
        'app/templates/index.html': '',
        'app/templates/login.html': '',
        'app/templates/register.html': '',
        'app/templates/dashboard.html': '',
        'app/static/css/style.css': '',
        'app/static/js/app.js': '',
        'tests/test_app.py': '',
        '.env': '',
        '.env.example': '',
        '.gitignore': '',
        'config.py': '',
        'run.py': '',
        'requirements.txt': '',
        'README.md': '',
    }
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create files
    for file_path in files:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(files[file_path])
        print(f"Created file: {file_path}")

if __name__ == "__main__":
    create_jobhunter_structure()
