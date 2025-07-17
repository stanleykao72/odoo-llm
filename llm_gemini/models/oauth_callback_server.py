# -*- coding: utf-8 -*-

"""
OAuth Callback Server for Browser Authentication
Implements temporary HTTP server for OAuth2 callback handling
"""

import http.server
import socketserver
import threading
import urllib.parse
from odoo.exceptions import UserError


class OAuthCallbackServer:
    """HTTP Server for OAuth Callback Handling"""
    
    def __init__(self, callback_handler):
        """
        Initialize OAuth callback server
        
        Args:
            callback_handler: Function to handle OAuth callback
        """
        self.callback_handler = callback_handler
        self.server = None
        self.port = None
        self.auth_code = None
        self.state = None
        self.error = None
        
    def start_server(self, port_range=(8080, 8090)):
        """
        Start local HTTP server for OAuth callback
        
        Args:
            port_range (tuple): Range of ports to try (start, end)
            
        Returns:
            str: Callback URL for OAuth flow
            
        Raises:
            Exception: If no available ports found
        """
        # Create custom handler class with access to parent instance
        parent_instance = self
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle GET requests to callback endpoint"""
                # Parse URL and query parameters
                parsed_url = urllib.parse.urlparse(self.path)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                if parsed_url.path == '/callback':
                    # Extract authorization code and state
                    auth_code = query_params.get('code', [None])[0]
                    state = query_params.get('state', [None])[0]
                    error = query_params.get('error', [None])[0]
                    
                    if error:
                        parent_instance.error = error
                        self.send_error_response(f"OAuth Error: {error}")
                    elif auth_code and state:
                        parent_instance.auth_code = auth_code
                        parent_instance.state = state
                        self.send_success_response()
                        
                        # Process callback in background
                        threading.Thread(
                            target=parent_instance.process_callback,
                            daemon=True
                        ).start()
                    else:
                        self.send_error_response("Missing authorization code or state")
                else:
                    self.send_error_response("Invalid callback path")
            
            def send_success_response(self):
                """Send success response to browser"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
                        .success { color: green; }
                        .container { max-width: 500px; margin: 0 auto; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="success">✓ Authentication Successful</h1>
                        <p>Your Google account has been connected successfully.</p>
                        <p>You can now close this browser window and return to Odoo.</p>
                    </div>
                    <script>
                        // Auto-close window after 3 seconds
                        setTimeout(function() {
                            window.close();
                        }, 3000);
                    </script>
                </body>
                </html>
                """.strip()
                
                self.wfile.write(html_content.encode())
            
            def send_error_response(self, error_message):
                """Send error response to browser"""
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Failed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; margin: 50px; }}
                        .error {{ color: red; }}
                        .container {{ max-width: 500px; margin: 0 auto; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">✗ Authentication Failed</h1>
                        <p>{error_message}</p>
                        <p>Please close this window and try again.</p>
                    </div>
                </body>
                </html>
                """.strip()
                
                self.wfile.write(html_content.encode())
            
            def log_message(self, format, *args):
                """Suppress server logs"""
                pass
        
        # Try to find an available port
        for port in range(*port_range):
            try:
                self.server = socketserver.TCPServer(("", port), CallbackHandler)
                self.port = port
                
                # Start server in background thread
                server_thread = threading.Thread(
                    target=self.server.serve_forever,
                    daemon=True
                )
                server_thread.start()
                
                return f"http://localhost:{port}/callback"
                
            except OSError:
                # Port is in use, try next one
                continue
        
        raise Exception("No available ports for OAuth callback server")
    
    def process_callback(self):
        """Process OAuth callback in background"""
        try:
            if self.auth_code and self.state:
                self.callback_handler(self.auth_code, self.state)
        except Exception as e:
            self.error = str(e)
        finally:
            # Shutdown server after processing
            if self.server:
                self.server.shutdown()
    
    def stop_server(self):
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server = None