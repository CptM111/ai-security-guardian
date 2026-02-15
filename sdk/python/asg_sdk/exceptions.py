"""
SDK Exceptions
"""


class ASGException(Exception):
    """Base exception for ASG SDK"""
    pass


class AuthenticationError(ASGException):
    """Authentication failed"""
    pass


class APIError(ASGException):
    """API request failed"""
    pass


class SecurityException(ASGException):
    """Security threat detected"""
    pass
