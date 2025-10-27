"""
Web dashboard for EmailScope.
Flask-based web interface for email discovery.
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any

from .crawler import WebCrawler
from .extractor import EmailExtractor
from .verifier import EmailVerifier
from .database import EmailScopeDB

class EmailScopeDashboard:
    """Web dashboard for EmailScope."""
    
    def __init__(self):
        """Initialize the dashboard."""
        # Set template folder to the correct path
        import os
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.config['SECRET_KEY'] = 'emailscope-dashboard-2024'
        
        # Initialize EmailScope components
        # Initialize advanced crawler with optimized settings
        self.crawler = WebCrawler(
            delay=0.5,           # Faster requests
            timeout=10,          # 10 second timeout
            bypass_robots=True,   # Bypass robots.txt
            max_depth=2,         # Crawl 2 levels deep
            max_pages=30,        # Max 30 pages per domain
            rate_limit=0.8       # 0.8 seconds between requests
        )
        self.extractor = EmailExtractor()
        self.verifier = EmailVerifier()
        self.db = EmailScopeDB()  # Database for persistence
        
        # Store results in memory (for real-time display)
        self.results = []
        self.scraping_status = "idle"  # idle, scraping, completed, error
        self.scraping_log = []  # Store real-time log messages
        self.stop_scraping = False  # Flag to stop scraping
        self.current_domain_id = None  # Current domain being scraped
        self.current_session_id = None  # Current scraping session
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/scrape', methods=['POST'])
        def scrape_domain():
            """API endpoint to scrape a domain."""
            data = request.get_json()
            domain = data.get('domain', '').strip()
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            # Start scraping (asynchronous)
            if self.scraping_status == "idle":
                self.scraping_status = "scraping"
                # Start scraping in background thread
                import threading
                thread = threading.Thread(target=self._scrape_domain, args=(domain,))
                thread.daemon = True
                thread.start()
                return jsonify({'status': 'started', 'message': 'Scraping started'})
            else:
                return jsonify({'error': 'Scraping already in progress'}), 400
        
        @self.app.route('/api/status')
        def get_status():
            """Get scraping status."""
            return jsonify({
                'status': self.scraping_status,
                'results_count': len(self.results)
            })
        
        @self.app.route('/api/results')
        def get_results():
            """Get all results from database."""
            try:
                # Always get all emails from database
                all_emails = []
                domains = self.db.get_all_domains()
                
                for domain_info in domains:
                    domain_name = domain_info['domain']
                    emails = self.db.get_emails_by_domain(domain_name)
                    
                    # Convert database emails to result format
                    for email_data in emails:
                        result = {
                            'id': email_data['id'],
                            'domain': domain_name,
                            'email': email_data['email'],
                            'confidence': email_data['confidence'],
                            'is_valid': email_data['is_valid'],
                            'reason': email_data['reason'],
                            'timestamp': email_data['created_at'],
                            'status': 'verified' if email_data['is_valid'] else 'unverified'
                        }
                        all_emails.append(result)
                
                # Sort by timestamp (newest first)
                all_emails.sort(key=lambda x: x['timestamp'], reverse=True)
                return jsonify(all_emails)
                
            except Exception as e:
                print(f"Error loading results from database: {e}")
                return jsonify([])
        
        @self.app.route('/api/logs')
        def get_logs():
            """Get scraping logs."""
            # If we have current logs in memory, return those
            if self.scraping_log:
                return jsonify(self.scraping_log)
            
            # Otherwise, get recent logs from database
            try:
                # Get recent logs from all domains
                all_logs = []
                domains = self.db.get_all_domains()
                
                for domain_info in domains:
                    domain_id = domain_info['id']
                    logs = self.db.get_logs_by_domain(domain_id)
                    
                    for log_data in logs:
                        log_entry = {
                            'timestamp': log_data['timestamp'],
                            'message': log_data['message']
                        }
                        all_logs.append(log_entry)
                
                # Sort by timestamp (newest first) and limit to recent logs
                all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
                return jsonify(all_logs[:50])  # Limit to 50 most recent logs
                
            except Exception as e:
                print(f"Error loading logs from database: {e}")
                return jsonify([])
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_results():
            """Clear all results from memory and database."""
            try:
                # Clear memory
                self.results = []
                self.scraping_log = []
                self.scraping_status = "idle"
                
                # Clear database
                import sqlite3
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM emails")
                    cursor.execute("DELETE FROM domains")
                    cursor.execute("DELETE FROM scraping_sessions")
                    cursor.execute("DELETE FROM scraping_logs")
                    conn.commit()
                
                return jsonify({'message': 'All results cleared from memory and database'})
            except Exception as e:
                print(f"Error clearing results: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/clean-low-confidence', methods=['POST'])
        def clean_low_confidence_data():
            """Remove emails with confidence less than 30%."""
            try:
                import sqlite3
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Count emails with low confidence
                    cursor.execute("SELECT COUNT(*) FROM emails WHERE confidence < 30")
                    count_before = cursor.fetchone()[0]
                    
                    if count_before == 0:
                        return jsonify({'message': 'No emails with confidence less than 30% found', 'removed_count': 0})
                    
                    # Delete emails with low confidence
                    cursor.execute("DELETE FROM emails WHERE confidence < 30")
                    removed_count = cursor.rowcount
                    
                    # Also clean up domains that have no emails left
                    cursor.execute("""
                        DELETE FROM domains 
                        WHERE id NOT IN (
                            SELECT DISTINCT domain_id FROM emails
                        )
                    """)
                    
                    # Clean up sessions for deleted domains
                    cursor.execute("""
                        DELETE FROM scraping_sessions 
                        WHERE domain_id NOT IN (
                            SELECT id FROM domains
                        )
                    """)
                    
                    # Clean up logs for deleted domains
                    cursor.execute("""
                        DELETE FROM scraping_logs 
                        WHERE domain_id NOT IN (
                            SELECT id FROM domains
                        )
                    """)
                    
                    conn.commit()
                
                return jsonify({
                    'message': f'Successfully cleaned {removed_count} emails with low confidence',
                    'removed_count': removed_count
                })
                
            except Exception as e:
                print(f"Error cleaning low confidence data: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_scraping():
            """Stop current scraping process."""
            if self.scraping_status == "scraping":
                self.stop_scraping = True
                self.scraping_status = "stopped"
                self._add_log("[STOP] Scraping stopped by user")
                
                # Update database
                if self.current_domain_id:
                    self.db.update_domain_status(self.current_domain_id, "stopped")
                    self.db.update_scraping_session(
                        self.current_session_id,
                        status="stopped",
                        completed_at=datetime.now().isoformat()
                    )
                
                return jsonify({'message': 'Scraping stopped'})
            else:
                return jsonify({'error': 'No scraping in progress'}), 400
        
        @self.app.route('/api/domains')
        def get_domains():
            """Get all domains with statistics."""
            domains = self.db.get_all_domains()
            return jsonify(domains)
        
        @self.app.route('/api/domains/<domain>')
        def get_domain_data(domain):
            """Get all data for a specific domain."""
            data = self.db.export_domain_data(domain)
            if not data:
                return jsonify({'error': 'Domain not found'}), 404
            return jsonify(data)
        
        @self.app.route('/api/sessions')
        def get_sessions():
            """Get recent scraping sessions."""
            sessions = self.db.get_recent_sessions(limit=20)
            return jsonify(sessions)
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall statistics."""
            try:
                domains = self.db.get_all_domains()
                total_domains = len(domains)
                total_emails = 0
                verified_emails = 0
                
                for domain_info in domains:
                    emails = self.db.get_emails_by_domain(domain_info['domain'])
                    total_emails += len(emails)
                    verified_emails += len([e for e in emails if e['is_valid']])
                
                return jsonify({
                    'total_domains': total_domains,
                    'total_emails': total_emails,
                    'verified_emails': verified_emails,
                    'verification_rate': (verified_emails / total_emails * 100) if total_emails > 0 else 0
                })
            except Exception as e:
                print(f"Error loading stats: {e}")
                return jsonify({
                    'total_domains': 0,
                    'total_emails': 0,
                    'verified_emails': 0,
                    'verification_rate': 0
                })
        
    
    def _scrape_domain(self, domain: str):
        """Scrape a domain in background thread."""
        try:
            print(f"Starting scraping for domain: {domain}")
            self.scraping_log = []  # Clear previous logs
            self.stop_scraping = False  # Reset stop flag
            
            # Add domain to database
            self.current_domain_id = self.db.add_domain(domain, "scraping")
            self.current_session_id = self.db.start_scraping_session(self.current_domain_id)
            
            self._add_log(f"Starting scraping for {domain}")
            self._add_log(f"WARNING: Bypassing robots.txt restrictions")
            
            # Store original domain for email generation
            original_domain = domain
            
            # Clean domain for crawling
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"
            
            # Crawl website
            print(f"Crawling website: {domain}")
            self._add_log(f"Crawling website: {domain}")
            urls = self.crawler.crawl_company_website(domain)
            
            if not urls:
                print(f"No URLs found for {domain}")
                self._add_log(f"ERROR: No URLs found for {domain}")
                self.scraping_status = "error"
                return
            
            print(f"Found {len(urls)} URLs to process")
            self._add_log(f"SUCCESS: Found {len(urls)} URLs to process")
            
            # Extract emails from all pages concurrently
            all_emails = set()
            self._add_log(f"Extracting emails from {len(urls)} pages concurrently...")
            
            # Use ThreadPoolExecutor for concurrent page processing
            max_page_workers = min(5, len(urls))  # Limit concurrent page workers
            
            with ThreadPoolExecutor(max_workers=max_page_workers) as executor:
                # Submit all page processing tasks
                future_to_url = {
                    executor.submit(self._process_page_concurrent, url, original_domain): url 
                    for url in urls
                }
                
                # Process completed pages as they finish
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    
                    try:
                        found_emails, generated_emails = future.result()
                        all_emails.update(found_emails)
                        all_emails.update(generated_emails)
                        
                    except Exception as e:
                        print(f"Error processing {url}: {e}")
                        self._add_log(f"[ERROR] Error processing {url}: {str(e)}")
            
            # Remove duplicates and sort
            all_emails = sorted(list(all_emails))
            print(f"Total unique emails: {len(all_emails)}")
            self._add_log(f"[STATS] Total unique emails: {len(all_emails)}")
            
            if not all_emails:
                print(f"No emails found for {domain}")
                self._add_log(f"[ERROR] No emails found for {domain}")
                self.scraping_status = "error"
                return
            
            # Verify emails concurrently using ThreadPoolExecutor
            print(f"Verifying {len(all_emails)} emails concurrently...")
            self._add_log(f"[SEARCH] Verifying {len(all_emails)} emails concurrently...")
            
            # Use ThreadPoolExecutor for concurrent email verification
            max_workers = min(10, len(all_emails))  # Limit concurrent workers
            completed_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all email verification tasks
                future_to_email = {
                    executor.submit(self._verify_email_concurrent, email, original_domain): email 
                    for email in all_emails
                }
                
                # Process completed verifications as they finish
                for future in as_completed(future_to_email):
                    # Check if scraping should stop
                    if self.stop_scraping:
                        self._add_log("[STOP] Scraping stopped by user")
                        self.scraping_status = "stopped"
                        # Cancel remaining futures
                        for f in future_to_email:
                            f.cancel()
                        return
                    
                    email = future_to_email[future]
                    completed_count += 1
                    
                    try:
                        result = future.result()
                        self.results.append(result)
                        
                        print(f"Completed {completed_count}/{len(all_emails)}: {result['email']} (confidence: {result['confidence']}%)")
                        self._add_log(f"[SUCCESS] Completed {completed_count}/{len(all_emails)}: {result['email']} (confidence: {result['confidence']}%)")
                        
                    except Exception as e:
                        print(f"Error processing email {email}: {e}")
                        self._add_log(f"[ERROR] Error processing {email}: {str(e)}")
            
            print(f"Scraping completed for {domain}. Found {len(all_emails)} emails.")
            self._add_log(f"[COMPLETE] Scraping completed! Found {len(all_emails)} emails.")
            
            # Update database with completion
            verified_count = len([r for r in self.results if r.get('is_valid')])
            self.db.update_domain_status(
                domain, 
                "completed", 
                total_emails=len(all_emails),
                verified_emails=verified_count,
                last_scraped_at=datetime.now().isoformat()
            )
            self.db.update_scraping_session(
                self.current_session_id,
                status="completed",
                total_emails_found=len(all_emails),
                total_emails_verified=verified_count,
                completed_at=datetime.now().isoformat()
            )
            
            self.scraping_status = "completed"
            
            # Reset to idle after a longer delay to allow frontend to detect completion
            import threading
            def reset_status():
                import time
                time.sleep(5)  # Wait 5 seconds to ensure frontend detects completion
                self.scraping_status = "idle"
                print("Status reset to idle")
            
            reset_thread = threading.Thread(target=reset_status)
            reset_thread.daemon = True
            reset_thread.start()
            
        except Exception as e:
            print(f"Error scraping {domain}: {str(e)}")
            self._add_log(f"[ERROR] Error: {str(e)}")
            self.scraping_status = "error"
    
    def _add_log(self, message: str):
        """Add a log message with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'message': message
        }
        self.scraping_log.append(log_entry)
        
        # Save to database if we have a current domain
        if self.current_domain_id:
            self.db.add_log(self.current_domain_id, timestamp, message)
        
        print(f"[{timestamp}] {message}")
    
    def _verify_email_concurrent(self, email: str, original_domain: str) -> Dict[str, Any]:
        """Verify a single email concurrently."""
        try:
            # Verify single email
            is_valid, confidence, reason = self.verifier.verify_email(email)
            
            # Add to database
            email_id = self.db.add_email(
                domain_id=self.current_domain_id,
                email=email,
                confidence=confidence,
                is_valid=is_valid,
                reason=reason,
                source="generated" if email.startswith(('info@', 'contact@', 'hello@', 'support@', 'sales@', 'admin@', 'team@', 'office@')) else "found"
            )
            
            # Create result
            result = {
                'id': email_id,
                'domain': original_domain,
                'email': email,
                'confidence': confidence,
                'is_valid': is_valid,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'status': 'verified' if is_valid else 'unverified'
            }
            
            return result
            
        except Exception as e:
            print(f"Error verifying email {email}: {e}")
            return {
                'id': None,
                'domain': original_domain,
                'email': email,
                'confidence': 0,
                'is_valid': False,
                'reason': f"Error: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def _process_page_concurrent(self, url: str, original_domain: str) -> tuple:
        """Process a single page concurrently."""
        try:
            print(f"Processing URL: {url}")
            self._add_log(f"[PAGE] Processing: {url}")
            
            # Get page content
            content = self.crawler.get_page_content(url)
            if not content:
                print(f"No content found for {url}")
                self._add_log(f"[WARNING] No content found for {url}")
                return set(), set()
            
            # Extract emails (use original domain for email generation)
            found_emails, generated_emails, email_sources = self.extractor.extract_all_emails(
                content, domain=original_domain
            )
            
            print(f"Found {len(found_emails)} emails, generated {len(generated_emails)} emails from {url}")
            self._add_log(f"[EMAIL] Found {len(found_emails)} emails, generated {len(generated_emails)} emails from {url}")
            
            return found_emails, generated_emails
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            self._add_log(f"[ERROR] Error processing {url}: {str(e)}")
            return set(), set()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard server."""
        print(f"Starting EmailScope Dashboard at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Create dashboard instance
dashboard = EmailScopeDashboard()

if __name__ == '__main__':
    dashboard.run(debug=True)
