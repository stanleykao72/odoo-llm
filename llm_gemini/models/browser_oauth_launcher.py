# -*- coding: utf-8 -*-

"""
Browser OAuth Launcher for Cross-Platform Authentication
Handles cross-platform browser launching for OAuth2 authentication
Enhanced for Odoo 18.0 with better error handling and platform detection
"""

import webbrowser
import subprocess
import platform
import logging
import time

_logger = logging.getLogger(__name__)


class BrowserOAuthLauncher:
    """Cross-platform browser launcher for OAuth2 authentication (18.0 Enhanced)"""
    
    def __init__(self, provider):
        """Initialize browser launcher with provider context"""
        self.provider = provider
        self.platform_info = {
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine(),
        }
        self.launch_attempts = 0
        self.max_attempts = 3
    
    def launch_browser_auth(self, auth_url):
        """
        Launch browser for OAuth2 authentication (18.0 enhanced implementation)
        
        Args:
            auth_url (str): OAuth2 authorization URL to open
            
        Returns:
            dict: Launch result with success status and details
        """
        self.launch_attempts = 0
        
        # 18.0 enhancement: Validate URL before launching
        if not self._validate_auth_url(auth_url):
            return self._create_launch_result(False, "Invalid authentication URL")
        
        # Try multiple launch strategies
        launch_strategies = [
            self._launch_default_browser,
            self._launch_platform_specific,
            self._launch_fallback_methods,
        ]
        
        for strategy in launch_strategies:
            self.launch_attempts += 1
            
            try:
                result = strategy(auth_url)
                if result['success']:
                    self._log_launch_success(auth_url, strategy.__name__)
                    return result
                    
            except Exception as e:
                self._log_launch_attempt_failed(strategy.__name__, str(e))
                continue
        
        # All strategies failed
        return self._create_fallback_result(auth_url)
    
    def _validate_auth_url(self, auth_url):
        """Validate OAuth2 URL for security (18.0 enhancement)"""
        if not auth_url or not isinstance(auth_url, str):
            return False
        
        # Check for valid Google OAuth URL
        valid_prefixes = [
            'https://accounts.google.com/o/oauth2/',
            'https://oauth2.googleapis.com/',
        ]
        
        if not any(auth_url.startswith(prefix) for prefix in valid_prefixes):
            _logger.warning(f"Suspicious OAuth URL detected: {auth_url[:50]}...")
            return False
        
        return True
    
    def _launch_default_browser(self, auth_url):
        """Launch using Python's webbrowser module (primary method)"""
        try:
            # 18.0 enhancement: Use specific browser if available
            browser_controller = webbrowser.get()
            
            # Open URL in new tab if possible
            success = webbrowser.open(auth_url, new=2, autoraise=True)
            
            if success:
                return self._create_launch_result(
                    True, 
                    f"Browser launched successfully using {browser_controller.name}",
                    method="webbrowser.open"
                )
            else:
                return self._create_launch_result(False, "webbrowser.open returned False")
                
        except Exception as e:
            return self._create_launch_result(False, f"webbrowser.open failed: {str(e)}")
    
    def _launch_platform_specific(self, auth_url):
        """Launch using platform-specific commands (18.0 enhanced)"""
        system = self.platform_info['system'].lower()
        
        try:
            if system == 'windows':
                return self._launch_windows_browser(auth_url)
            elif system == 'darwin':  # macOS
                return self._launch_macos_browser(auth_url)
            elif system == 'linux':
                return self._launch_linux_browser(auth_url)
            else:
                return self._create_launch_result(False, f"Unsupported platform: {system}")
                
        except Exception as e:
            return self._create_launch_result(False, f"Platform-specific launch failed: {str(e)}")
    
    def _launch_windows_browser(self, auth_url):
        """Launch browser on Windows (18.0 enhanced)"""
        try:
            # Try multiple Windows methods
            methods = [
                lambda: subprocess.run(['start', auth_url], shell=True, check=True),
                lambda: subprocess.run(['cmd', '/c', 'start', auth_url], check=True),
                lambda: subprocess.run(['rundll32', 'url.dll,FileProtocolHandler', auth_url], check=True),
            ]
            
            for method in methods:
                try:
                    method()
                    return self._create_launch_result(True, "Windows browser launched successfully", method="subprocess")
                except subprocess.CalledProcessError:
                    continue
            
            return self._create_launch_result(False, "All Windows launch methods failed")
            
        except Exception as e:
            return self._create_launch_result(False, f"Windows browser launch error: {str(e)}")
    
    def _launch_macos_browser(self, auth_url):
        """Launch browser on macOS (18.0 enhanced)"""
        try:
            # Try macOS 'open' command with different options
            methods = [
                ['open', auth_url],
                ['open', '-a', 'Safari', auth_url],
                ['open', '-a', 'Google Chrome', auth_url],
                ['open', '-a', 'Firefox', auth_url],
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, check=True, capture_output=True, text=True, timeout=10)
                    return self._create_launch_result(
                        True, 
                        f"macOS browser launched successfully with: {' '.join(method)}", 
                        method="subprocess"
                    )
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue
            
            return self._create_launch_result(False, "All macOS launch methods failed")
            
        except Exception as e:
            return self._create_launch_result(False, f"macOS browser launch error: {str(e)}")
    
    def _launch_linux_browser(self, auth_url):
        """Launch browser on Linux (18.0 enhanced)"""
        try:
            # Try Linux desktop environment methods
            methods = [
                ['xdg-open', auth_url],
                ['gnome-open', auth_url],
                ['kde-open', auth_url],
                ['firefox', auth_url],
                ['google-chrome', auth_url],
                ['chromium-browser', auth_url],
            ]
            
            for method in methods:
                try:
                    # Use Popen for non-blocking execution on Linux
                    process = subprocess.Popen(
                        method, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    
                    # Give it a moment to start
                    time.sleep(1)
                    
                    # Check if process is still running (indicates success)
                    if process.poll() is None or process.returncode == 0:
                        return self._create_launch_result(
                            True, 
                            f"Linux browser launched successfully with: {' '.join(method)}", 
                            method="subprocess"
                        )
                        
                except (OSError, subprocess.SubprocessError):
                    continue
            
            return self._create_launch_result(False, "All Linux launch methods failed")
            
        except Exception as e:
            return self._create_launch_result(False, f"Linux browser launch error: {str(e)}")
    
    def _launch_fallback_methods(self, auth_url):
        """Fallback launch methods (18.0 enhancement)"""
        try:
            # Try environment-specific methods
            fallback_methods = []
            
            # Check for WSL (Windows Subsystem for Linux)
            if self._is_wsl():
                fallback_methods.extend([
                    ['cmd.exe', '/c', 'start', auth_url],
                    ['powershell.exe', '-Command', f'Start-Process "{auth_url}"'],
                ])
            
            # Check for remote desktop / headless environments
            if self._is_headless_environment():
                return self._create_launch_result(
                    False, 
                    "Headless environment detected - manual browser access required",
                    fallback_url=auth_url
                )
            
            # Try fallback methods
            for method in fallback_methods:
                try:
                    subprocess.run(method, check=True, timeout=10)
                    return self._create_launch_result(
                        True, 
                        f"Fallback method successful: {' '.join(method)}", 
                        method="fallback"
                    )
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue
            
            return self._create_launch_result(False, "All fallback methods failed")
            
        except Exception as e:
            return self._create_launch_result(False, f"Fallback launch error: {str(e)}")
    
    def _is_wsl(self):
        """Check if running in Windows Subsystem for Linux (18.0 enhancement)"""
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info or 'wsl' in version_info
        except (OSError, IOError):
            return False
    
    def _is_headless_environment(self):
        """Check if running in headless environment (18.0 enhancement)"""
        # Check for common headless indicators
        headless_indicators = [
            # Environment variables
            not bool(os.environ.get('DISPLAY')),  # Linux X11
            not bool(os.environ.get('WAYLAND_DISPLAY')),  # Linux Wayland
            bool(os.environ.get('SSH_CONNECTION')),  # SSH session
            bool(os.environ.get('CI')),  # CI/CD environment
            
            # Platform checks
            platform.system() == 'Linux' and not self._has_gui_capability(),
        ]
        
        return any(headless_indicators)
    
    def _has_gui_capability(self):
        """Check if system has GUI capability (18.0 enhancement)"""
        try:
            # Try to detect GUI availability
            import os
            
            # Check for X11
            if os.environ.get('DISPLAY'):
                return True
            
            # Check for Wayland
            if os.environ.get('WAYLAND_DISPLAY'):
                return True
            
            # Check for running desktop environment
            desktop_procs = ['gnome-session', 'kde-session', 'xfce4-session']
            try:
                pgrep_result = subprocess.run(['pgrep', '-f', '|'.join(desktop_procs)], 
                                            capture_output=True, text=True)
                return pgrep_result.returncode == 0
            except OSError:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _create_launch_result(self, success, message, method=None, fallback_url=None):
        """Create standardized launch result (18.0 enhancement)"""
        result = {
            'success': success,
            'message': message,
            'platform': self.platform_info,
            'attempts': self.launch_attempts,
            'timestamp': time.time(),
        }
        
        if method:
            result['method'] = method
        
        if fallback_url:
            result['fallback_url'] = fallback_url
            result['manual_instructions'] = self._get_manual_instructions(fallback_url)
        
        return result
    
    def _create_fallback_result(self, auth_url):
        """Create fallback result when all methods fail (18.0 enhancement)"""
        return {
            'success': False,
            'message': 'All browser launch methods failed. Manual authentication required.',
            'fallback_url': auth_url,
            'manual_instructions': self._get_manual_instructions(auth_url),
            'platform': self.platform_info,
            'attempts': self.launch_attempts,
            'timestamp': time.time(),
            'troubleshooting': self._get_troubleshooting_tips(),
        }
    
    def _get_manual_instructions(self, auth_url):
        """Get manual authentication instructions (18.0 enhancement)"""
        return {
            'steps': [
                '1. Copy the following URL to your browser manually',
                '2. Complete the Google authentication process',
                '3. Grant the requested permissions',
                '4. Return to Odoo to continue',
            ],
            'url': auth_url,
            'note': 'This URL is valid for 10 minutes from generation time',
        }
    
    def _get_troubleshooting_tips(self):
        """Get troubleshooting tips based on platform (18.0 enhancement)"""
        system = self.platform_info['system'].lower()
        
        tips = {
            'general': [
                'Ensure you have a web browser installed',
                'Check if Odoo has permission to launch applications',
                'Try running Odoo as administrator/root if needed',
            ],
            'windows': [
                'Ensure your default browser is properly configured',
                'Try running "start https://google.com" in Command Prompt',
                'Check Windows Defender or antivirus blocking',
            ],
            'darwin': [
                'Check System Preferences → Security & Privacy → Privacy → Automation',
                'Try manually: open https://google.com in Terminal',
                'Ensure Odoo has permission to control other applications',
            ],
            'linux': [
                'Install xdg-utils: sudo apt-get install xdg-utils',
                'Check DISPLAY environment variable: echo $DISPLAY',
                'Try manually: xdg-open https://google.com',
            ],
        }
        
        return {
            'general': tips['general'],
            'platform_specific': tips.get(system, []),
        }
    
    def _log_launch_success(self, auth_url, method):
        """Log successful browser launch (18.0 enhancement)"""
        _logger.info(f"Browser launched successfully for OAuth2 authentication")
        _logger.debug(f"Method: {method}, Platform: {self.platform_info['system']}, Attempts: {self.launch_attempts}")
    
    def _log_launch_attempt_failed(self, method, error):
        """Log failed launch attempt (18.0 enhancement)"""
        _logger.warning(f"Browser launch attempt {self.launch_attempts} failed")
        _logger.debug(f"Method: {method}, Error: {error}, Platform: {self.platform_info['system']}")
    
    def get_platform_info(self):
        """Get detailed platform information for debugging (18.0 enhancement)"""
        return {
            **self.platform_info,
            'python_version': platform.python_version(),
            'browser_available': self._check_browser_availability(),
            'gui_capability': self._has_gui_capability(),
            'wsl_detected': self._is_wsl(),
            'headless_detected': self._is_headless_environment(),
        }
    
    def _check_browser_availability(self):
        """Check if browsers are available on the system (18.0 enhancement)"""
        browsers = {
            'webbrowser_module': True,  # Always available in Python
        }
        
        # Check for common browsers
        common_browsers = ['firefox', 'google-chrome', 'chromium-browser', 'safari']
        
        for browser in common_browsers:
            try:
                result = subprocess.run(['which', browser], capture_output=True, text=True)
                browsers[browser] = result.returncode == 0
            except OSError:
                browsers[browser] = False
        
        return browsers