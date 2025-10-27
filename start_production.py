#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Production Startup Script
Automatically chooses the right WSGI server for the platform
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    """Start EmailScope with platform-appropriate WSGI server."""
    
    print("🚀 EmailScope Cross-Platform Production Startup")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("-" * 60)
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variables
    os.environ['RENDER'] = 'false'  # Use local production config
    
    # Get port from environment or use default
    port = os.environ.get('PORT', '5000')
    
    try:
        if platform.system() == "Windows":
            print("🪟 Windows detected - Using Waitress")
            return start_waitress(port)
        else:
            print("🐧 Unix/Linux detected - Using Gunicorn")
            return start_gunicorn(port)
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_waitress(port):
    """Start with Waitress (Windows-compatible)."""
    
    try:
        import waitress
        print(f"✅ Waitress {waitress.__version__} found")
    except ImportError:
        print("❌ Waitress not found! Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'waitress'])
        import waitress
        print(f"✅ Waitress {waitress.__version__} installed")
    
    print(f"Starting Waitress server on port {port}...")
    print("Dashboard will be available at: http://localhost:" + port)
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    # Run Waitress
    cmd = [
        'waitress-serve',
        '--host=0.0.0.0',
        f'--port={port}',
        '--threads=4',
        '--connection-limit=1000',
        'render_config:application'
    ]
    
    subprocess.run(cmd)
    return True

def start_gunicorn(port):
    """Start with Gunicorn (Unix-compatible)."""
    
    try:
        import gunicorn
        print(f"✅ Gunicorn {gunicorn.__version__} found")
    except ImportError:
        print("❌ Gunicorn not found! Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'])
        import gunicorn
        print(f"✅ Gunicorn {gunicorn.__version__} installed")
    
    print(f"Starting Gunicorn server on port {port}...")
    print("Dashboard will be available at: http://localhost:" + port)
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    # Run Gunicorn
    cmd = [
        'gunicorn',
        '-c', 'gunicorn.conf.py',
        f'--bind=0.0.0.0:{port}',
        '--workers=2',
        '--timeout=120',
        'render_config:application'
    ]
    
    subprocess.run(cmd)
    return True

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
