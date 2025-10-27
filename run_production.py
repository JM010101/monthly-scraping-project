#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Production Server for EmailScope
Uses Waitress on Windows, Gunicorn on Unix
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    """Run EmailScope with appropriate production server."""
    
    print("🚀 EmailScope Cross-Platform Production Server")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print("Using production WSGI server")
    print("-" * 60)
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variables for local production
    os.environ['RENDER'] = 'false'  # Use local production config
    
    # Get the current directory
    project_dir = str(current_dir)
    
    # Determine which server to use based on platform
    if platform.system() == "Windows":
        print("🪟 Windows detected - Using Waitress WSGI server")
        return run_waitress(project_dir)
    else:
        print("🐧 Unix/Linux detected - Using Gunicorn WSGI server")
        return run_gunicorn(project_dir)

def run_waitress(project_dir):
    """Run with Waitress (Windows-compatible)."""
    
    try:
        # Check if Waitress is installed
        import waitress
        print(f"✅ Waitress {waitress.__version__} found")
    except ImportError:
        print("❌ Waitress not found!")
        print("Install with: pip install waitress")
        return False
    
    try:
        print("Starting Waitress server...")
        print("Dashboard will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        # Run Waitress with production settings
        cmd = [
            'waitress-serve',
            '--host=0.0.0.0',
            '--port=5000',
            '--threads=4',
            '--connection-limit=1000',
            'render_config:application'
        ]
        
        subprocess.run(cmd, cwd=project_dir)
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting Waitress server: {e}")
        return False

def run_gunicorn(project_dir):
    """Run with Gunicorn (Unix-compatible)."""
    
    try:
        # Check if Gunicorn is installed
        import gunicorn
        print(f"✅ Gunicorn {gunicorn.__version__} found")
    except ImportError:
        print("❌ Gunicorn not found!")
        print("Install with: pip install gunicorn")
        return False
    
    try:
        print("Starting Gunicorn server...")
        print("Dashboard will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        # Run Gunicorn with production settings
        cmd = [
            'gunicorn',
            '-c', 'gunicorn.conf.py',
            '--bind', '0.0.0.0:5000',
            '--workers', '2',
            '--timeout', '120',
            'render_config:application'
        ]
        
        subprocess.run(cmd, cwd=project_dir)
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting Gunicorn server: {e}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)