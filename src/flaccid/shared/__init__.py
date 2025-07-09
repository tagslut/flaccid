import typer
from .qobuz_api import QobuzAPI
from .apple_api import AppleAPI
from .metadata_utils import (
    extract_isrc_from_flac,
    get_existing_metadata,
    build_search_query,
    validate_flac_file,
    apply_metadata_to_flac
)

app = typer.Typer(name="shared", help="Shared utilities and API clients.")

@app.command("test-qobuz")
def test_qobuz():
    """Test Qobuz API connection."""
    import asyncio

    async def test():
        qobuz = QobuzAPI()
        try:
            await qobuz.authenticate()
            print("✅ Qobuz authentication successful")
        except Exception as e:
            print(f"❌ Qobuz authentication failed: {e}")
        finally:
            await qobuz.close()

    asyncio.run(test())

@app.command("test-apple")
def test_apple():
    """Test Apple Music API connection."""
    print("⚠️  Apple Music API requires developer tokens - check credentials configuration")

# Export main classes for easy importing
__all__ = [
    "QobuzAPI",
    "AppleAPI",
    "extract_isrc_from_flac",
    "get_existing_metadata",
    "build_search_query",
    "validate_flac_file",
    "apply_metadata_to_flac"
]