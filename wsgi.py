#!/usr/bin/env python3
"""
WSGI entry point for PythonAnywhere deployment
"""
import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

from app import app

if __name__ == "__main__":
    app.run()
