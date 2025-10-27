#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render-optimized configuration for EmailScope
"""

import os
import sys
from pathlib import Path

def get_render_config():
    """Get configuration optimized for Render deployment."""
    
    # Check if running on Render
    is_render = os.environ.get('RENDER', False) or os.environ.get('PORT', False)
    
    if is_render:
        print("🚀 Running on Render - Using optimized settings")
        return {
            # More conservative crawling for cloud deployment
            'delay': 2.0,           # Slower requests (2s vs 0.5s)
            'timeout': 30,          # Longer timeout (30s vs 10s)
            'bypass_robots': False, # Respect robots.txt on cloud
            'max_depth': 1,         # Shallow crawling (1 vs 2 levels)
            'max_pages': 10,        # Fewer pages (10 vs 30)
            'rate_limit': 2.0,      # Slower rate (2s vs 0.8s)
            
            # Email verification settings
            'verification_timeout': 5,  # Longer DNS timeout
            'mock_dns': False,          # Real DNS checks
            
            # Process management
            'max_workers': 3,       # Fewer concurrent workers
            'request_retries': 3,   # More retries for failed requests
        }
    else:
        print("💻 Running locally - Using standard settings")
        return {
            # Standard local settings
            'delay': 0.5,
            'timeout': 10,
            'bypass_robots': True,
            'max_depth': 2,
            'max_pages': 30,
            'rate_limit': 0.8,
            'verification_timeout': 1,
            'mock_dns': False,
            'max_workers': 5,
            'request_retries': 2,
        }

def create_render_launcher():
    """Create a Render-optimized launcher."""
    
    config = get_render_config()
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from emailscope.dashboard import EmailScopeDashboard
        
        print("=" * 60)
        print("EmailScope - Render Optimized Deployment")
        print("=" * 60)
        print(f"Configuration: {config}")
        print("-" * 40)
        
        # Create dashboard with Render-optimized settings
        dashboard = EmailScopeDashboard(config)
        
        # Get port from environment (Render requirement)
        port = int(os.environ.get('PORT', 5000))
        
        print(f"Starting on port {port}")
        print("Press Ctrl+C to stop")
        print("-" * 40)
        
        dashboard.run(host='0.0.0.0', port=port, debug=False)
        return True
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    try:
        success = create_render_launcher()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nDashboard stopped. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
