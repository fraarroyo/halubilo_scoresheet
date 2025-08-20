# 🚀 Quick Start: Deploy to PythonAnywhere

## ⚡ Fast Deployment (5 minutes)

### 1. Sign Up
- Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
- Create free account

### 2. Upload Files
- Go to **Files** tab
- Create folder: `halubilo_scoresheet`
- Upload all your project files

### 3. Create Web App
- Go to **Web** tab
- Click **"Add a new web app"**
- Choose **Flask**
- Set source directory: `/home/yourusername/halubilo_scoresheet`

### 4. Configure WSGI
- Click on WSGI file link
- Replace content with:
```python
import sys
import os
path = '/home/yourusername/halubilo_scoresheet'
if path not in sys.path:
    sys.path.append(path)
from app import app as application
```

### 5. Set Static Files
- In **Web** tab → **Static files**
- Add: `/static/` → `/home/yourusername/halubilo_scoresheet/static`

### 6. Install Dependencies
- Go to **Consoles** tab
- Start **Bash** console
- Run:
```bash
cd halubilo_scoresheet
pip install -r requirements.txt
```

### 7. Reload & Test
- Go back to **Web** tab
- Click **Reload**
- Visit your URL: `https://yourusername.pythonanywhere.com`

## 🔑 Default Login
- **Username:** `admin`
- **Password:** `admin123`

## 📁 Project Structure
```
halubilo_scoresheet/
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI entry point
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, uploads)
└── DEPLOYMENT.md         # Detailed deployment guide
```

## 🆘 Need Help?
- Check **DEPLOYMENT.md** for detailed steps
- Run `python deploy_pythonanywhere.py` on PythonAnywhere
- Check error logs in **Web** tab

## 🌟 Features Ready
- ✅ Admin Dashboard
- ✅ User Management
- ✅ Team Management with Images
- ✅ CSV Bulk Upload
- ✅ Score Tracking
- ✅ Leaderboards
- ✅ Activity Management
- ✅ Reset Scores (Admin)

Your Team Building Scoresheet will be live in minutes! 🎉
