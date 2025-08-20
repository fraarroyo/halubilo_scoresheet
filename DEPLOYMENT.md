# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (free or paid)
- Your Flask application code

## Step 1: Upload Your Code

### Option A: Upload via Files Tab
1. Go to PythonAnywhere dashboard
2. Click on "Files" tab
3. Navigate to your home directory
4. Create a new folder: `halubilo_scoresheet`
5. Upload all your project files to this folder

### Option B: Clone from GitHub (if you upload there first)
```bash
git clone https://github.com/fraarroyo/halubilo_scoresheet.git
```

## Step 2: Set Up Virtual Environment
1. Go to "Consoles" tab
2. Start a new Bash console
3. Navigate to your project directory:
```bash
cd halubilo_scoresheet
```

4. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. Install requirements:
```bash
pip install -r requirements.txt
```

## Step 3: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask"
4. Select Python version (3.9 or higher)
5. Set source code directory: `/home/yourusername/halubilo_scoresheet`
6. Set working directory: `/home/yourusername/halubilo_scoresheet`

## Step 4: Configure WSGI File
1. Click on the WSGI configuration file link
2. Replace the content with:
```python
import sys
import os

# Add your project directory to the Python path
path = '/home/yourusername/halubilo_scoresheet'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import app as application

# For debugging
if __name__ == "__main__":
    application.run()
```

**Important:** Replace `yourusername` with your actual PythonAnywhere username!

## Step 5: Set Environment Variables
1. Go to "Web" tab
2. Click on your web app
3. Go to "Environment variables" section
4. Add:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a new secret key

## Step 6: Configure Static Files
1. In "Web" tab, go to "Static files" section
2. Add:
   - URL: `/static/`
   - Directory: `/home/yourusername/halubilo_scoresheet/static`

## Step 7: Database Setup
1. Go to "Databases" tab
2. Create a new SQLite database or use MySQL/PostgreSQL
3. Update your `app.py` database URI if needed

## Step 8: File Uploads
1. Create upload directories:
```bash
mkdir -p static/uploads/teams
```

2. Set proper permissions:
```bash
chmod 755 static/uploads
chmod 755 static/uploads/teams
```

## Step 9: Reload Web App
1. Go back to "Web" tab
2. Click "Reload" button
3. Check for any error messages in the error log

## Step 10: Test Your Application
1. Visit your web app URL: `https://yourusername.pythonanywhere.com`
2. Test all functionality
3. Check error logs if issues occur

## Troubleshooting

### Common Issues:
1. **Import Errors**: Check Python path in WSGI file
2. **Database Errors**: Ensure database file permissions
3. **Static File Issues**: Verify static file configuration
4. **Upload Errors**: Check upload directory permissions

### Error Logs:
- Check "Web" tab → "Log files" → "Error log"
- Check "Consoles" tab for any error messages

### Performance Tips:
1. Use production WSGI server (Gunicorn)
2. Enable static file caching
3. Use CDN for static assets
4. Optimize database queries

## Security Notes:
1. Change default secret key
2. Use HTTPS in production
3. Set proper file permissions
4. Regular security updates

## Support:
- PythonAnywhere help: https://help.pythonanywhere.com/
- Flask documentation: https://flask.palletsprojects.com/
