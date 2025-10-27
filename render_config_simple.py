#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Render Configuration for EmailScope
Minimal setup to avoid deployment issues
"""

import os
import sys
from pathlib import Path

def create_wsgi_app():
    """Create WSGI application with minimal configuration."""
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from emailscope.dashboard import EmailScopeDashboard
        
        # Simple configuration
        config = {
            'delay': 2.0,
            'timeout': 20,
            'bypass_robots': True,
            'max_depth': 1,
            'max_pages': 5,
            'rate_limit': 2.5,
            'verification_timeout': 5,
            'mock_dns': False,
            'max_workers': 1,
            'request_retries': 3,
            'max_emails_per_page': 10,
            'max_total_emails': 20,
            'enable_timeout_protection': True,
        }
        
        print("🚀 Starting EmailScope - Simplified Configuration")
        print("=" * 50)
        print(f"Platform: {os.environ.get('RENDER', 'Local')}")
        print("✅ Using simplified configuration")
        print("-" * 50)
        
        # Create dashboard
        dashboard = EmailScopeDashboard(config)
        
        # Return the Flask app
        return dashboard.app
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        # Fallback to simple Flask app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error():
            return f'''
            <html>
            <head><title>EmailScope - Import Error</title></head>
            <body>
                <h1>❌ Import Error</h1>
                <p>Error: {e}</p>
                <p>Please check your dependencies.</p>
            </body>
            </html>
            '''
        
        return app
    except Exception as e:
        print(f"❌ Error: {e}")
        # Fallback to simple Flask app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error():
            return f'''
            <html>
            <head><title>EmailScope - Error</title></head>
            <body>
                <h1>❌ Error</h1>
                <p>Error: {e}</p>
            </body>
            </html>
            '''
        
        return app

# WSGI application entry point
application = create_wsgi_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting EmailScope on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)
