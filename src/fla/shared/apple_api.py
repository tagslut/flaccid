"""
Apple Music API client with iTunes fallback.
"""

class AppleAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str):
        """Search for a track on Apple Music."""
        pass

    def get_metadata(self, track_id: str):
        """Retrieve metadata for a given track ID."""
        pass
