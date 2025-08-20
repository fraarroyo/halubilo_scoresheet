#!/usr/bin/env python3
"""
PythonAnywhere Deployment Helper Script
Run this on PythonAnywhere to set up your environment
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 PythonAnywhere Deployment Helper")
    print("=" * 50)
    
    # Check if we're on PythonAnywhere
    if not os.environ.get('PYTHONANYWHERE_SITE'):
        print("⚠️  This script is designed to run on PythonAnywhere")
        print("   Please run it in your PythonAnywhere console")
        return
    
    print(f"📍 Running on PythonAnywhere: {os.environ.get('PYTHONANYWHERE_SITE')}")
    
    # Create necessary directories
    directories = [
        'static/uploads',
        'static/uploads/teams',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Set proper permissions
    try:
        os.chmod('static/uploads', 0o755)
        os.chmod('static/uploads/teams', 0o755)
        print("🔐 Set proper permissions for upload directories")
    except Exception as e:
        print(f"⚠️  Could not set permissions: {e}")
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        print("\n📦 Installing Python requirements...")
        if run_command('pip install -r requirements.txt', 'Installing requirements'):
            print("✅ All requirements installed")
        else:
            print("❌ Failed to install some requirements")
    else:
        print("⚠️  requirements.txt not found")
    
    # Test the application
    print("\n🧪 Testing application...")
    try:
        from app import app
        print("✅ Application imports successfully")
        
        # Test database connection
        with app.app_context():
            from app import db
            db.create_all()
            print("✅ Database setup successful")
            
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return
    
    print("\n🎉 Deployment setup completed!")
    print("\n📋 Next steps:")
    print("1. Go to Web tab in PythonAnywhere")
    print("2. Configure your WSGI file")
    print("3. Set up static files")
    print("4. Reload your web app")
    print("5. Test your application")
    
    print(f"\n🌐 Your app will be available at:")
    print(f"   https://{os.environ.get('PYTHONANYWHERE_SITE')}")

if __name__ == '__main__':
    main()
