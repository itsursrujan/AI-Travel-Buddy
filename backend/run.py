#!/usr/bin/env python
"""
Startup script for AI Travel Buddy Backend
Uses gunicorn on Windows (via waitress as fallback)
"""
import os
import sys

# Try gunicorn first, fall back to Flask dev server
try:
    from gunicorn.app.wsgiapp import run as gunicorn_run
    from main import create_app
    
    # Create the app
    app = create_app("development")
    
    # Run with gunicorn
    sys.argv = [
        'gunicorn',
        '--bind', '0.0.0.0:8000',
        '--workers', '1',
        '--timeout', '60',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'main:app'
    ]
    gunicorn_run()
except ImportError:
    # Fall back to Flask
    print("Gunicorn not available, using Flask development server...")
    from main import create_app
    app = create_app("development")
    app.run(debug=False, host="0.0.0.0", port=8000, use_reloader=False)
