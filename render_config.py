#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free Render Optimized Configuration for EmailScope
Designed specifically for Render's free tier limitations
"""

import os
import sys
import platform
from pathlib import Path

def create_wsgi_app():
    """Create WSGI application optimized for free Render deployment."""
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from emailscope.dashboard import EmailScopeDashboard
        
        # Get configuration optimized for FREE Render tier
        config = get_free_render_config()
        
        print("🚀 Starting EmailScope - FREE RENDER OPTIMIZED")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print("⚠️  FREE TIER LIMITATIONS:")
        print("   - 30 second process timeout")
        print("   - 512MB memory limit")
        print("   - Shared CPU resources")
        print("   - Limited network connections")
        print("-" * 60)
        print(f"Configuration: {config}")
        print("-" * 60)
        
        # Create dashboard with free-tier optimized settings
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

def get_free_render_config():
    """Get configuration optimized for FREE Render tier."""
    
    # Check if running on Render
    is_render = os.environ.get('RENDER', False) or os.environ.get('PORT', False)
    
    if is_render:
        print("🌐 FREE Render deployment detected")
        return {
            # ULTRA-CONSERVATIVE settings for free tier
            'delay': 5.0,           # Very slow requests (5s delay)
            'timeout': 15,          # Short timeout (15s vs 45s)
            'bypass_robots': False, # Always respect robots.txt
            'max_depth': 1,         # Only 1 level deep
            'max_pages': 3,         # Only 3 pages max (vs 8)
            'rate_limit': 5.0,      # Very slow rate (5s vs 3s)
            
            # Email verification settings
            'verification_timeout': 3,  # Short DNS timeout (3s vs 8s)
            'mock_dns': False,          # Real DNS checks
            
            # Process management
            'max_workers': 1,       # Single worker (vs 2)
            'request_retries': 2,   # Fewer retries (2 vs 5)
            
            # Free tier specific settings
            'max_emails_per_page': 5,    # Limit emails per page
            'max_total_emails': 10,     # Limit total emails
            'enable_timeout_protection': True,  # Enable timeout protection
        }
    else:
        print("💻 Local development mode")
        return {
            # Local settings (faster than free Render)
            'delay': 1.0,
            'timeout': 20,
            'bypass_robots': False,
            'max_depth': 2,
            'max_pages': 15,
            'rate_limit': 1.5,
            'verification_timeout': 3,
            'mock_dns': False,
            'max_workers': 3,
            'request_retries': 3,
            'max_emails_per_page': 50,
            'max_total_emails': 100,
            'enable_timeout_protection': False,
        }

# WSGI application entry point
application = create_wsgi_app()

if __name__ == '__main__':
    # This should not be called directly in production
    print("⚠️  This is a WSGI application optimized for FREE Render.")
    print("   Use Waitress (Windows) or Gunicorn (Unix) to run it.")
    print("   Windows: waitress-serve --host=0.0.0.0 --port=5000 render_config:application")
    print("   Unix: gunicorn -w 1 -b 0.0.0.0:5000 render_config:application")