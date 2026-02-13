# Local Development Setup

This guide helps you set up the project for local development after the deployment-ready changes.

## Quick Start

### 1. Clone or Extract Project

```bash
# If from zip
unzip 2moreFitness.zip
cd 2moreFitness

# Or if from git
git clone https://github.com/yourusername/2moreFitness.git
cd 2moreFitness
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create .env File (Optional for Local)

For local development, you can skip this step as settings.py has sensible defaults.

If you want to customize, create a `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env with your preferences
# For local development, you can use:
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 7. Load Sample Data (Optional)

```bash
python manage.py shell < setup_sample_data.py
```

### 8. Run Development Server

```bash
python manage.py runserver
```

### 9. Access the Application

- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Login:** http://127.0.0.1:8000/login/

## Development vs Production

The application now automatically detects the environment:

### Local Development (Default)
- Uses SQLite database
- DEBUG = True
- Uses default SECRET_KEY
- ALLOWED_HOSTS = localhost, 127.0.0.1

### Production (Render)
- Uses PostgreSQL (via DATABASE_URL)
- DEBUG = False (set via environment variable)
- Uses secure SECRET_KEY (from environment)
- ALLOWED_HOSTS set via environment variable

## Working with the New Setup

### Environment Variables

The project now uses `python-decouple` for environment variables.

**Priority order:**
1. Environment variables (`.env` file or system)
2. Default values in `settings.py`

**Key variables:**
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - PostgreSQL connection string (optional for local)
- `STATIC_ADMIN_USERNAME` - Admin username
- `STATIC_ADMIN_PASSWORD` - Admin password
- `TIME_ZONE` - Timezone (default: Asia/Manila)

### Database

**Local Development:**
- SQLite database (`db.sqlite3`)
- No additional setup required
- File-based, easy to reset

**Production (Render):**
- PostgreSQL database
- Automatically configured via `DATABASE_URL`
- Requires PostgreSQL service on Render

### Static Files

**Local Development:**
- Django's built-in static file serving
- Run `python manage.py collectstatic` before deploying

**Production:**
- WhiteNoise serves static files
- Automatically collects during build process

### Media Files

**Local Development:**
- Files stored in `media/` directory
- Served by Django in DEBUG mode

**Production:**
- Files stored in `media/` directory (temporary on free tier)
- Consider using AWS S3 or Cloudinary for persistence

## Common Development Tasks

### Reset Database

```bash
# Delete database
rm db.sqlite3

# Delete migrations (optional)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser again
python manage.py createsuperuser
```

### Update Dependencies

```bash
# After adding new packages
pip freeze > requirements.txt

# Or manually edit requirements.txt
# Then install
pip install -r requirements.txt
```

### Run Tests

```bash
python manage.py test
```

### Collect Static Files

```bash
python manage.py collectstatic --no-input
```

### Create New App

```bash
python manage.py startapp app_name

# Then add to INSTALLED_APPS in settings.py
```

## Troubleshooting

### Issue: "No module named 'decouple'"

**Solution:**
```bash
pip install python-decouple
```

### Issue: "No module named 'psycopg2'"

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --no-input
```

### Issue: Database errors

**Solution:**
```bash
python manage.py migrate
```

### Issue: "SECRET_KEY" errors

**Solution:**
Create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
```

Or the app will use the default (fine for local development).

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Django
- Pylance

Settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true
    }
}
```

### PyCharm

1. Open project
2. Set Python interpreter to `venv`
3. Enable Django support in Settings
4. Set Django project root
5. Set Settings module: `gym_project.settings`

## Git Workflow

### Initial Setup

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### Regular Workflow

```bash
# Make changes
git add .
git commit -m "Description of changes"
git push
```

### Branches

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature

# Merge to main (after review)
git checkout main
git merge feature/new-feature
git push
```

## Testing Before Deployment

Before deploying to production:

1. **Set DEBUG=False locally** and test
2. **Run with production settings:**
   ```bash
   python manage.py check --deploy
   ```
3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```
4. **Run tests:**
   ```bash
   python manage.py test
   ```
5. **Check security:**
   ```bash
   python manage.py check --deploy
   ```

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Python Decouple: https://github.com/HBNetwork/python-decouple
- WhiteNoise: http://whitenoise.evans.io/

## Getting Help

- Check `DEPLOYMENT.md` for deployment issues
- Check `ISSUES_FIXED.md` for known issues and solutions
- Django Debug Toolbar: Install for detailed debugging
  ```bash
  pip install django-debug-toolbar
  ```
