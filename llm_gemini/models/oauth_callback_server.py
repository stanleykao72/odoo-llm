# -*- coding: utf-8 -*-

"""
OAuth2 Callback Server for Browser Authentication
Handles OAuth2 redirect callbacks from Google during browser authentication
Enhanced for Odoo 18.0 with better error handling and security
"""

import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth2 callbacks (18.0 Enhanced)"""
    
    def do_GET(self):
        """Handle GET request from OAuth2 callback (18.0 enhanced implementation)"""
        try:
            # Parse the callback URL and extract parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Check for authorization code
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                state = query_params.get('state', [''])[0]
                
                # Store the authorization code for the waiting thread
                self.server.auth_code = auth_code
                self.server.state = state
                self.server.auth_received = True
                
                # 18.0 enhancement: Send success page with better UX
                self._send_success_page()
                
            elif 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]
                
                # Store error for the waiting thread
                self.server.auth_error = f"{error}: {error_description}"
                self.server.auth_received = True
                
                # 18.0 enhancement: Send error page with user guidance
                self._send_error_page(error, error_description)
                
            else:
                # Invalid callback - missing required parameters
                self.server.auth_error = "Invalid callback: missing code or error parameter"
                self.server.auth_received = True
                self._send_error_page("invalid_request", "Missing required parameters")
                
        except Exception as e:
            # Handle any unexpected errors
            self.server.auth_error = f"Callback handler error: {str(e)}"
            self.server.auth_received = True
            self._send_error_page("server_error", str(e))
    
    def _send_success_page(self):
        """Send success page to user (18.0 enhanced with better UX)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # 18.0 enhancement: More professional success page
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Authentication Successful - Odoo LLM</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; padding: 40px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; text-align: center; min-height: 100vh;
                    display: flex; align-items: center; justify-content: center;
                }
                .container { 
                    background: rgba(255,255,255,0.1); 
                    padding: 40px; border-radius: 15px;
                    backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    max-width: 500px; width: 100%;
                }
                .success-icon { font-size: 64px; margin-bottom: 20px; }
                h1 { margin: 0 0 20px 0; font-weight: 300; }
                p { opacity: 0.9; line-height: 1.6; margin-bottom: 30px; }
                .close-btn {
                    background: rgba(255,255,255,0.2); color: white;
                    border: 1px solid rgba(255,255,255,0.3); padding: 12px 24px;
                    border-radius: 8px; cursor: pointer; transition: all 0.3s;
                    font-size: 16px; text-decoration: none; display: inline-block;
                }
                .close-btn:hover { 
                    background: rgba(255,255,255,0.3); 
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Authentication Successful!</h1>
                <p>Your Google account has been successfully connected to Odoo LLM (18.0 Enhanced). 
                   You can now close this tab and return to Odoo to start using Gemini AI with your personal account.</p>
                <button class="close-btn" onclick="window.close()">Close This Tab</button>
            </div>
            <script>
                // Auto-close after 5 seconds (18.0 enhancement)
                setTimeout(() => {
                    try { window.close(); } catch(e) { 
                        document.querySelector('.close-btn').textContent = 'Please close this tab manually';
                    }
                }, 5000);
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
    
    def _send_error_page(self, error_type, error_description):
        """Send error page to user (18.0 enhanced with guidance)"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # 18.0 enhancement: User-friendly error messages with guidance
        error_guidance = {
            'access_denied': 'You declined the authorization request. To use Gemini AI, please try again and grant the necessary permissions.',
            'invalid_request': 'The authentication request was invalid. Please try the authentication process again from Odoo.',
            'server_error': 'A server error occurred during authentication. Please try again or contact support if the problem persists.',
        }
        
        guidance = error_guidance.get(error_type, 'An unexpected error occurred. Please try the authentication process again.')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Authentication Error - Odoo LLM</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; padding: 40px; 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                    color: white; text-align: center; min-height: 100vh;
                    display: flex; align-items: center; justify-content: center;
                }}
                .container {{ 
                    background: rgba(255,255,255,0.1); 
                    padding: 40px; border-radius: 15px;
                    backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    max-width: 500px; width: 100%;
                }}
                .error-icon {{ font-size: 64px; margin-bottom: 20px; }}
                h1 {{ margin: 0 0 20px 0; font-weight: 300; }}
                p {{ opacity: 0.9; line-height: 1.6; margin-bottom: 20px; }}
                .error-details {{ 
                    background: rgba(0,0,0,0.2); padding: 15px; 
                    border-radius: 8px; margin: 20px 0; font-family: monospace;
                    font-size: 14px; text-align: left;
                }}
                .retry-btn {{
                    background: rgba(255,255,255,0.2); color: white;
                    border: 1px solid rgba(255,255,255,0.3); padding: 12px 24px;
                    border-radius: 8px; cursor: pointer; transition: all 0.3s;
                    font-size: 16px; text-decoration: none; display: inline-block;
                    margin-right: 10px;
                }}
                .retry-btn:hover {{ 
                    background: rgba(255,255,255,0.3); 
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Authentication Failed</h1>
                <p>{guidance}</p>
                <div class="error-details">
                    Error: {error_type}<br>
                    Details: {error_description}
                </div>
                <button class="retry-btn" onclick="window.close()">Close Tab</button>
                <a href="#" class="retry-btn" onclick="history.back()">Try Again</a>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to suppress default HTTP server logging (18.0 enhancement)"""
        # Only log errors, not every request
        if args and len(args) > 1 and '4' in str(args[1]):
            super().log_message(format, *args)


class OAuthCallbackServer:
    """OAuth2 callback server manager (18.0 Enhanced)"""
    
    def __init__(self, callback_handler=None):
        """Initialize OAuth callback server with enhanced configuration"""
        self.callback_handler = callback_handler
        self.server = None
        self.server_thread = None
        self.port = None
        
    def start_server(self, host='localhost', port_range=(8000, 8100)):
        """
        Start callback server on available port (18.0 enhanced with port range)
        
        Args:
            host (str): Host to bind server to
            port_range (tuple): Range of ports to try
            
        Returns:
            str: Callback URL for OAuth redirect
        """
        # Find available port in range
        for port in range(port_range[0], port_range[1]):
            try:
                self.server = HTTPServer((host, port), OAuthCallbackHandler)
                self.port = port
                break
            except OSError:
                continue
        
        if not self.server:
            raise RuntimeError(f"No available ports in range {port_range}")
        
        # Initialize server state
        self.server.auth_code = None
        self.server.state = None
        self.server.auth_error = None
        self.server.auth_received = False
        
        # Start server in background thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Return callback URL
        return f"http://{host}:{self.port}/oauth2/callback"
    
    def wait_for_callback(self, timeout=300):
        """
        Wait for OAuth callback with enhanced timeout handling (18.0)
        
        Args:
            timeout (int): Timeout in seconds (default 5 minutes)
            
        Returns:
            tuple: (auth_code, state) if successful, (None, error) if failed
        """
        start_time = time.time()
        
        while not self.server.auth_received:
            if time.time() - start_time > timeout:
                self.stop_server()
                return None, "Authentication timeout: No response received within 5 minutes"
            
            time.sleep(0.5)  # Check every 500ms
        
        # Get results and clean up
        auth_code = getattr(self.server, 'auth_code', None)
        state = getattr(self.server, 'state', None)
        auth_error = getattr(self.server, 'auth_error', None)
        
        self.stop_server()
        
        if auth_error:
            return None, auth_error
        
        return auth_code, state
    
    def stop_server(self):
        """Stop the callback server (18.0 enhanced cleanup)"""
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass  # Ignore cleanup errors
            
            self.server = None
        
        if self.server_thread and self.server_thread.is_alive():
            try:
                self.server_thread.join(timeout=2.0)
            except Exception:
                pass  # Ignore thread cleanup errors
            
            self.server_thread = None
    
    def get_server_info(self):
        """Get server information for debugging (18.0 enhancement)"""
        if not self.server:
            return None
        
        return {
            'host': self.server.server_address[0],
            'port': self.server.server_address[1],
            'running': self.server_thread and self.server_thread.is_alive(),
            'callback_url': f"http://{self.server.server_address[0]}:{self.server.server_address[1]}/oauth2/callback"
        }