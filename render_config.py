#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Production WSGI Application for EmailScope
Works on both Windows and Unix systems
"""

import os
import sys
import platform
from pathlib import Path

def create_wsgi_app():
    """Create WSGI application for production deployment."""
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from emailscope.dashboard import EmailScopeDashboard
        
        # Get configuration optimized for production
        config = get_production_config()
        
        print("🚀 Starting EmailScope Production Server")
        print("=" * 50)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Configuration: {config}")
        print("-" * 50)
        
        # Create dashboard with production settings
        dashboard = EmailScopeDashboard(config)
        
        # Return the Flask app for WSGI
        return dashboard.app
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        raise
    except Exception as e:
        print(f"Error creating WSGI app: {e}")
        raise

def get_production_config():
    """Get production-optimized configuration."""
    
    # Check if running on Render
    is_render = os.environ.get('RENDER', False) or os.environ.get('PORT', False)
    
    if is_render:
        print("🌐 Production deployment on Render")
        return {
            # Conservative settings for production stability
            'delay': 3.0,           # Slower requests for stability
            'timeout': 45,          # Longer timeout for production
            'bypass_robots': False, # Always respect robots.txt in production
            'max_depth': 1,         # Shallow crawling for reliability
            'max_pages': 8,         # Fewer pages for stability
            'rate_limit': 3.0,      # Conservative rate limiting
            
            # Email verification settings
            'verification_timeout': 8,  # Longer DNS timeout
            'mock_dns': False,          # Real DNS checks
            
            # Process management
            'max_workers': 2,       # Conservative worker count
            'request_retries': 5,  # More retries for production
        }
    else:
        print("💻 Local production mode")
        return {
            # Local production settings (faster than Render)
            'delay': 1.0,
            'timeout': 20,
            'bypass_robots': False,  # Still respect robots.txt
            'max_depth': 2,
            'max_pages': 15,
            'rate_limit': 1.5,
            'verification_timeout': 3,
            'mock_dns': False,
            'max_workers': 3,
            'request_retries': 3,
        }

# WSGI application entry point
application = create_wsgi_app()

if __name__ == '__main__':
    # This should not be called directly in production
    print("⚠️  This is a WSGI application.")
    print("   Use Waitress (Windows) or Gunicorn (Unix) to run it.")
    print("   Windows: waitress-serve --host=0.0.0.0 --port=5000 render_config:application")
    print("   Unix: gunicorn -w 4 -b 0.0.0.0:5000 render_config:application")