"""
Session timeout middleware for automatic user logout after inactivity.
"""
import time
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log out users after a period of inactivity.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check if the session has expired and logout the user if necessary.
        """
        # Only process authenticated users
        if not request.user.is_authenticated:
            return None

        # Status polling must observe inactivity without becoming activity
        # itself. Explicit extension is handled by the endpoint.
        is_timeout_check = request.path == reverse("session_timeout_check")
        
        # Get the last activity time from session
        last_activity = request.session.get('last_activity')
        current_time = time.time()
        
        # Set initial last activity if not set
        if last_activity is None:
            request.session['last_activity'] = current_time
            return None
        
        # Calculate time difference
        time_diff = current_time - last_activity
        
        # Get session timeout from settings (default to 10 minutes)
        session_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 600)
        
        # If time difference exceeds timeout, logout user
        if time_diff > session_timeout:
            # Store the reason for logout
            request.session['logout_reason'] = 'session_timeout'
            logout(request)
            messages.warning(
                request, 
                'Your session has expired due to inactivity. Please log in again.'
            )
            if is_timeout_check:
                return None
            return redirect('login')

        if not is_timeout_check:
            request.session['last_activity'] = current_time
        return None
    
    def process_response(self, request, response):
        """
        Update the session's last activity time for authenticated users.
        """
        if (
            request.user.is_authenticated
            and request.path != reverse("session_timeout_check")
        ):
            request.session['last_activity'] = time.time()
        return response
