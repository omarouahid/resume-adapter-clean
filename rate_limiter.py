#!/usr/bin/env python3
"""
Rate Limiter - IP-based request limiting for OpenRouter API calls.
"""

import os
import time
import json
import hashlib
import streamlit as st
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IPRateLimiter:
    """IP-based rate limiter with configurable limits and time windows."""
    
    def __init__(self, 
                 max_requests: int = None,
                 time_window: int = None,
                 enabled: bool = None,
                 storage_key: str = "rate_limiter_data"):
        """
        Initialize rate limiter with configuration.
        
        Args:
            max_requests: Maximum requests per time window (default from env)
            time_window: Time window in minutes (default from env)
            enabled: Whether rate limiting is enabled (default from env)
            storage_key: Session state key for storing rate limit data
        """
        
        # Load configuration from environment variables
        self.max_requests = max_requests or int(os.environ.get('RATE_LIMIT_MAX_REQUESTS', 30))
        self.time_window = time_window or int(os.environ.get('RATE_LIMIT_TIME_WINDOW', 60))  # minutes
        self.enabled = enabled if enabled is not None else os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        self.storage_key = storage_key
        
        # Admin override
        self.admin_ips = set(os.environ.get('RATE_LIMIT_ADMIN_IPS', '').split(','))
        self.admin_ips.discard('')  # Remove empty strings
        
        logger.info(f"Rate limiter initialized: enabled={self.enabled}, max_requests={self.max_requests}, time_window={self.time_window}min")
    
    def get_client_ip(self) -> str:
        """Get client IP address from Streamlit request headers."""
        try:
            # Try to get real IP from headers (for deployments behind proxies)
            headers = st.context.headers if hasattr(st, 'context') and hasattr(st.context, 'headers') else {}
            
            # Common headers for real IP
            for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']:
                if header in headers:
                    ip = headers[header].split(',')[0].strip()
                    if ip:
                        return ip
            
            # Fallback to remote address
            if 'Remote-Addr' in headers:
                return headers['Remote-Addr']
                
            # Last resort - use a hash of session info
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'session_id'):
                return hashlib.md5(str(st.session_state.session_id).encode()).hexdigest()[:15]
            
            # Ultimate fallback
            return "unknown"
            
        except Exception as e:
            logger.warning(f"Could not determine client IP: {e}")
            return "unknown"
    
    def get_rate_limit_data(self) -> Dict:
        """Get rate limit data from session state."""
        if self.storage_key not in st.session_state:
            st.session_state[self.storage_key] = {}
        return st.session_state[self.storage_key]
    
    def cleanup_old_requests(self, ip_data: Dict) -> Dict:
        """Remove old requests outside the time window."""
        if not ip_data:
            return {}
        
        current_time = time.time()
        window_start = current_time - (self.time_window * 60)  # Convert minutes to seconds
        
        # Keep only requests within the time window
        cleaned_data = {}
        for ip, requests in ip_data.items():
            recent_requests = [req_time for req_time in requests if req_time > window_start]
            if recent_requests:
                cleaned_data[ip] = recent_requests
        
        return cleaned_data
    
    def is_admin_ip(self, ip: str) -> bool:
        """Check if IP is in admin list (no rate limiting)."""
        return ip in self.admin_ips and len(self.admin_ips) > 0
    
    def check_rate_limit(self, ip: str = None) -> Tuple[bool, Dict]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            ip: IP address to check (auto-detected if None)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        
        # If rate limiting is disabled, allow all requests
        if not self.enabled:
            return True, {"status": "disabled", "remaining": float('inf')}
        
        # Get client IP
        if ip is None:
            ip = self.get_client_ip()
        
        # Admin IPs bypass rate limiting
        if self.is_admin_ip(ip):
            return True, {"status": "admin", "remaining": float('inf')}
        
        # Get and cleanup rate limit data
        rate_data = self.get_rate_limit_data()
        rate_data = self.cleanup_old_requests(rate_data)
        
        # Get current requests for this IP
        current_requests = rate_data.get(ip, [])
        
        # Check if limit exceeded
        if len(current_requests) >= self.max_requests:
            oldest_request = min(current_requests) if current_requests else 0
            reset_time = oldest_request + (self.time_window * 60)
            
            return False, {
                "status": "limited",
                "remaining": 0,
                "reset_time": datetime.fromtimestamp(reset_time),
                "retry_after": int(reset_time - time.time())
            }
        
        # Calculate remaining requests
        remaining = self.max_requests - len(current_requests)
        
        return True, {
            "status": "allowed",
            "remaining": remaining,
            "used": len(current_requests),
            "window_minutes": self.time_window
        }
    
    def record_request(self, ip: str = None) -> bool:
        """
        Record a request for the given IP.
        
        Args:
            ip: IP address (auto-detected if None)
            
        Returns:
            True if request was recorded, False if rate limited
        """
        
        # If rate limiting is disabled, don't record
        if not self.enabled:
            return True
        
        # Get client IP
        if ip is None:
            ip = self.get_client_ip()
        
        # Admin IPs bypass rate limiting
        if self.is_admin_ip(ip):
            return True
        
        # Check rate limit first
        allowed, info = self.check_rate_limit(ip)
        if not allowed:
            return False
        
        # Record the request
        rate_data = self.get_rate_limit_data()
        current_time = time.time()
        
        if ip not in rate_data:
            rate_data[ip] = []
        
        rate_data[ip].append(current_time)
        
        # Update session state
        st.session_state[self.storage_key] = rate_data
        
        logger.info(f"Request recorded for IP {ip[:10]}... ({info.get('remaining', 0)} remaining)")
        return True
    
    def get_rate_limit_status(self, ip: str = None) -> Dict:
        """Get current rate limit status for an IP."""
        if ip is None:
            ip = self.get_client_ip()
        
        allowed, info = self.check_rate_limit(ip)
        
        # Add additional info
        info.update({
            "ip": ip[:10] + "..." if len(ip) > 10 else ip,
            "enabled": self.enabled,
            "max_requests": self.max_requests,
            "time_window": self.time_window,
            "is_admin": self.is_admin_ip(ip)
        })
        
        return info
    
    def reset_ip_limits(self, ip: str) -> bool:
        """Reset rate limits for a specific IP (admin function)."""
        try:
            rate_data = self.get_rate_limit_data()
            if ip in rate_data:
                del rate_data[ip]
                st.session_state[self.storage_key] = rate_data
                logger.info(f"Rate limits reset for IP {ip}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting limits for IP {ip}: {e}")
            return False
    
    def get_all_ips_status(self) -> Dict:
        """Get rate limit status for all IPs (admin function)."""
        try:
            rate_data = self.get_rate_limit_data()
            rate_data = self.cleanup_old_requests(rate_data)
            
            all_status = {}
            for ip in rate_data.keys():
                all_status[ip] = self.get_rate_limit_status(ip)
            
            return all_status
        except Exception as e:
            logger.error(f"Error getting all IPs status: {e}")
            return {}

def rate_limited_request(func):
    """Decorator to add rate limiting to functions."""
    def wrapper(*args, **kwargs):
        limiter = IPRateLimiter()
        
        if not limiter.record_request():
            status = limiter.get_rate_limit_status()
            raise RateLimitExceeded(
                f"Rate limit exceeded. Try again in {status.get('retry_after', 60)} seconds.",
                status
            )
        
        return func(*args, **kwargs)
    return wrapper

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, rate_limit_info: Dict):
        super().__init__(message)
        self.rate_limit_info = rate_limit_info