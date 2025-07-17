"""Custom exception hierarchy for the FLACCID project."""


class FLACCIDError(Exception):
    """Base exception for all FLACCID errors."""


class PluginError(FLACCIDError):
    """Base class for plugin-related failures."""


class AuthenticationError(PluginError):
    """Raised when authentication with an external service fails."""


class APIError(PluginError):
    """Raised when an API request returns an error response."""
