#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Render Deployment Configuration
Minimal setup to troubleshoot deployment issues
"""

import os
import sys
from pathlib import Path

def create_simple_app():
    """Create a simple Flask app for testing deployment."""
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from flask import Flask
        
        # Create a simple Flask app first
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return '''
            <html>
            <head><title>EmailScope - Deployment Test</title></head>
            <body>
                <h1>🚀 EmailScope Deployment Test</h1>
                <p>✅ Flask app is working!</p>
                <p>✅ Deployment successful!</p>
                <p>Platform: ''' + str(os.environ.get('RENDER', 'Local')) + '''</p>
                <p>Port: ''' + str(os.environ.get('PORT', '5000')) + '''</p>
            </body>
            </html>
            '''
        
        @app.route('/health')
        def health():
            return {'status': 'ok', 'message': 'EmailScope is running'}
        
        print("✅ Simple Flask app created successfully")
        return app
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        # Create a minimal error app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error():
            return f"<h1>Import Error</h1><p>{e}</p>"
        
        return app
    except Exception as e:
        print(f"❌ Error: {e}")
        # Create a minimal error app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error():
            return f"<h1>Error</h1><p>{e}</p>"
        
        return app

# WSGI application entry point
application = create_simple_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting simple app on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)
