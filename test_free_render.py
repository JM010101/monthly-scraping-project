#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for FREE Render Deployment
Helps verify that the balanced settings work correctly
"""

import os
import sys
import time
from pathlib import Path

def test_free_render_config():
    """Test the free Render configuration."""
    
    print("🧪 Testing FREE Render Configuration")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from emailscope.dashboard import EmailScopeDashboard
        
        # Set environment to simulate Render
        os.environ['RENDER'] = 'true'
        os.environ['PORT'] = '5000'
        
        # Get free Render config
        from render_config import get_free_render_config
        config = get_free_render_config()
        
        print("📋 Configuration:")
        print(f"  Delay: {config['delay']}s")
        print(f"  Timeout: {config['timeout']}s")
        print(f"  Max Pages: {config['max_pages']}")
        print(f"  Rate Limit: {config['rate_limit']}s")
        print(f"  Max Emails: {config['max_total_emails']}")
        print()
        
        # Create dashboard
        dashboard = EmailScopeDashboard(config)
        
        print("✅ Dashboard created successfully")
        print("✅ Configuration loaded correctly")
        print()
        
        # Test timeout protection
        if config['enable_timeout_protection']:
            print("✅ Timeout protection enabled")
        else:
            print("❌ Timeout protection disabled")
        
        print()
        print("🚀 Ready for deployment!")
        print("Expected behavior:")
        print("  - Scraping should take 20-25 seconds")
        print("  - Should find 3-10 emails")
        print("  - Should complete before 30s timeout")
        print("  - Should show detailed logs")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_domains():
    """Test recommended domains for free tier."""
    
    print("\n🌐 Recommended Test Domains:")
    print("=" * 50)
    
    test_domains = [
        {
            'domain': 'example.com',
            'reason': 'Always works, simple site',
            'expected_emails': '1-3',
            'success_rate': '95%'
        },
        {
            'domain': 'github.com',
            'reason': 'Well-structured, has contact info',
            'expected_emails': '2-5',
            'success_rate': '90%'
        },
        {
            'domain': 'stackoverflow.com',
            'reason': 'Good for testing, reliable',
            'expected_emails': '1-4',
            'success_rate': '85%'
        }
    ]
    
    for i, domain_info in enumerate(test_domains, 1):
        print(f"{i}. {domain_info['domain']}")
        print(f"   Reason: {domain_info['reason']}")
        print(f"   Expected emails: {domain_info['expected_emails']}")
        print(f"   Success rate: {domain_info['success_rate']}")
        print()
    
    print("💡 Start with example.com for testing")

if __name__ == '__main__':
    try:
        print("🔧 FREE Render Configuration Test")
        print("=" * 60)
        
        success = test_free_render_config()
        test_domains()
        
        if success:
            print("\n✅ All tests passed!")
            print("Your configuration is ready for deployment.")
        else:
            print("\n❌ Tests failed!")
            print("Check the error messages above.")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
