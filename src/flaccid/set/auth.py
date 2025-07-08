import typer
import keyring
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from pathlib import Path
import getpass

console = Console()
app = typer.Typer(help="Store service credentials in system keychain.")

# Service definitions
SERVICES = {
    "qobuz": {
        "name": "Qobuz",
        "username_field": "username",
        "password_field": "password",
        "keyring_service": "flaccid-qobuz",
        "description": "Qobuz music streaming service credentials"
    },
    "apple": {
        "name": "Apple Music",
        "username_field": "developer_token",
        "password_field": "user_token",
        "keyring_service": "flaccid-apple",
        "description": "Apple Music API tokens (Developer Token and optional User Token)"
    },
    "tidal": {
        "name": "Tidal",
        "username_field": "username",
        "password_field": "password",
        "keyring_service": "flaccid-tidal",
        "description": "Tidal music streaming service credentials"
    },
    "spotify": {
        "name": "Spotify",
        "username_field": "client_id",
        "password_field": "client_secret",
        "keyring_service": "flaccid-spotify",
        "description": "Spotify API credentials (Client ID and Secret)"
    }
}

def store_credentials(service_name: str, username: str, password: str = None):
    """Store credentials in system keychain."""
    service_info = SERVICES.get(service_name)
    if not service_info:
        console.print(f"❌ Unknown service: {service_name}", style="red")
        return False

    keyring_service = service_info["keyring_service"]

    try:
        # Store username/token
        keyring.set_password(keyring_service, service_info["username_field"], username)

        # Store password if required
        if service_info["password_field"] and password:
            keyring.set_password(keyring_service, service_info["password_field"], password)

        return True
    except Exception as e:
        console.print(f"❌ Error storing credentials: {e}", style="red")
        return False

@app.command("qobuz")
def qobuz_auth(
    username: str = typer.Option(None, "--username", "-u", help="Qobuz username"),
    password: str = typer.Option(None, "--password", "-p", help="Qobuz password")
):
    """
    Store Qobuz authentication credentials.

    Args:
        username: Qobuz username (will prompt if not provided)
        password: Qobuz password (will prompt if not provided)
    """
    if not username:
        username = Prompt.ask("Qobuz username")

    if not password:
        password = getpass.getpass("Qobuz password: ")

    if store_credentials("qobuz", username, password):
        console.print("🔐 Qobuz credentials stored securely.", style="green")
    else:
        console.print("❌ Failed to store Qobuz credentials.", style="red")
        raise typer.Exit(1)

@app.command("apple")
def apple_auth(
    developer_token: str = typer.Option(None, "--developer-token", "-d", help="Apple Music Developer Token"),
    user_token: str = typer.Option(None, "--user-token", "-u", help="Apple Music User Token (optional)")
):
    """
    Store Apple Music API tokens.

    Args:
        developer_token: Apple Music Developer Token (will prompt if not provided)
        user_token: Apple Music User Token (optional, for user-specific features)
    """
    if not developer_token:
        developer_token = Prompt.ask("Apple Music Developer Token")

    if not user_token:
        user_token = Prompt.ask("Apple Music User Token (optional, press Enter to skip)", default="")

    if store_credentials("apple", developer_token, user_token if user_token else None):
        console.print("🔐 Apple Music tokens stored securely.", style="green")
        if user_token:
            console.print("   Both Developer and User tokens stored.", style="dim")
        else:
            console.print("   Only Developer token stored (User token can be added later).", style="dim")
    else:
        console.print("❌ Failed to store Apple Music tokens.", style="red")
        raise typer.Exit(1)

@app.command("list")
def list_credentials():
    """List all stored service credentials."""
    table = Table(title="Stored Credentials")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description", style="dim")

    for service_name, service_info in SERVICES.items():
        keyring_service = service_info["keyring_service"]
        username_field = service_info["username_field"]

        try:
            username = keyring.get_password(keyring_service, username_field)
            status = "✅ Configured" if username else "❌ Not set"
        except Exception:
            status = "❌ Error"

        table.add_row(
            service_info["name"],
            status,
            service_info["description"]
        )

    console.print(table)
