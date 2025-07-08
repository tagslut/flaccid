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

def get_credentials(service_name: str):
    """Get credentials from system keychain."""
    service_info = SERVICES.get(service_name)
    if not service_info:
        return None

    keyring_service = service_info["keyring_service"]

    try:
        username = keyring.get_password(keyring_service, service_info["username_field"])
        password = None

        if service_info["password_field"]:
            password = keyring.get_password(keyring_service, service_info["password_field"])

        return {
            "username": username,
            "password": password,
            "service": service_name
        }
    except Exception as e:
        console.print(f"❌ Error retrieving credentials: {e}", style="red")
        return None

def delete_credentials(service_name: str):
    """Delete credentials from system keychain."""
    service_info = SERVICES.get(service_name)
    if not service_info:
        return False

    keyring_service = service_info["keyring_service"]

    try:
        keyring.delete_password(keyring_service, service_info["username_field"])

        if service_info["password_field"]:
            keyring.delete_password(keyring_service, service_info["password_field"])

        return True
    except Exception as e:
        console.print(f"❌ Error deleting credentials: {e}", style="red")
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

@app.command("tidal")
def tidal_auth(
    username: str = typer.Option(None, "--username", "-u", help="Tidal username"),
    password: str = typer.Option(None, "--password", "-p", help="Tidal password")
):
    """
    Store Tidal authentication credentials.

    Args:
        username: Tidal username (will prompt if not provided)
        password: Tidal password (will prompt if not provided)
    """
    if not username:
        username = Prompt.ask("Tidal username")

    if not password:
        password = getpass.getpass("Tidal password: ")

    if store_credentials("tidal", username, password):
        console.print("🔐 Tidal credentials stored securely.", style="green")
    else:
        console.print("❌ Failed to store Tidal credentials.", style="red")
        raise typer.Exit(1)

@app.command("spotify")
def spotify_auth(
    client_id: str = typer.Option(None, "--client-id", "-c", help="Spotify Client ID"),
    client_secret: str = typer.Option(None, "--client-secret", "-s", help="Spotify Client Secret")
):
    """
    Store Spotify API credentials.

    Args:
        client_id: Spotify Client ID (will prompt if not provided)
        client_secret: Spotify Client Secret (will prompt if not provided)
    """
    if not client_id:
        client_id = Prompt.ask("Spotify Client ID")

    if not client_secret:
        client_secret = getpass.getpass("Spotify Client Secret: ")

    if store_credentials("spotify", client_id, client_secret):
        console.print("🔐 Spotify credentials stored securely.", style="green")
    else:
        console.print("❌ Failed to store Spotify credentials.", style="red")
        raise typer.Exit(1)

@app.command("list")
def list_credentials():
    """List all stored service credentials."""
    console.print("[bold]Stored Service Credentials:[/bold]")

    table = Table()
    table.add_column("Service", style="cyan")
    table.add_column("Username/Token", style="green")
    table.add_column("Password", style="yellow")
    table.add_column("Status", style="white")

    for service_name, service_info in SERVICES.items():
        credentials = get_credentials(service_name)

        if credentials and credentials["username"]:
            username = credentials["username"]
            password_status = "✅ Stored" if credentials["password"] else "N/A"

            # Mask username/token for security
            if len(username) > 6:
                masked_username = username[:3] + "***" + username[-3:]
            else:
                masked_username = "***"

            status = "🔐 Configured"
            table.add_row(service_info["name"], masked_username, password_status, status)
        else:
            table.add_row(service_info["name"], "Not set", "Not set", "❌ Not configured")

    console.print(table)

@app.command("test")
def test_credentials(service: str = typer.Argument(..., help="Service to test (qobuz, apple, tidal, spotify)")):
    """
    Test stored credentials for a service.

    Args:
        service: Service name to test
    """
    if service not in SERVICES:
        console.print(f"❌ Unknown service: {service}", style="red")
        console.print(f"Available services: {', '.join(SERVICES.keys())}")
        raise typer.Exit(1)

    credentials = get_credentials(service)

    if not credentials or not credentials["username"]:
        console.print(f"❌ No credentials found for {service}", style="red")
        console.print(f"Run 'fla set auth {service}' to set up credentials.")
        raise typer.Exit(1)

    console.print(f"🔍 Testing {SERVICES[service]['name']} credentials...")

    # Basic credential validation
    service_info = SERVICES[service]

    if service == "qobuz":
        if credentials["username"] and credentials["password"]:
            console.print("✅ Qobuz credentials are present", style="green")
            console.print("⚠️  To fully test, try using 'fla tag qobuz' command", style="yellow")
        else:
            console.print("❌ Qobuz credentials incomplete", style="red")

    elif service == "apple":
        if credentials["username"]:  # Token stored as username
            console.print("✅ Apple Music token is present", style="green")
            console.print("⚠️  To fully test, try using 'fla tag apple' command", style="yellow")
        else:
            console.print("❌ Apple Music token missing", style="red")

    elif service == "tidal":
        if credentials["username"] and credentials["password"]:
            console.print("✅ Tidal credentials are present", style="green")
            console.print("⚠️  To fully test, try using 'fla get tidal' command", style="yellow")
        else:
            console.print("❌ Tidal credentials incomplete", style="red")

    elif service == "spotify":
        if credentials["username"] and credentials["password"]:  # Client ID/Secret
            console.print("✅ Spotify API credentials are present", style="green")
            console.print("⚠️  To fully test, try using 'fla tag spotify' command", style="yellow")
        else:
            console.print("❌ Spotify API credentials incomplete", style="red")

@app.command("remove")
def remove_credentials(service: str = typer.Argument(..., help="Service to remove credentials for")):
    """
    Remove stored credentials for a service.

    Args:
        service: Service name to remove credentials for
    """
    if service not in SERVICES:
        console.print(f"❌ Unknown service: {service}", style="red")
        console.print(f"Available services: {', '.join(SERVICES.keys())}")
        raise typer.Exit(1)

    service_info = SERVICES[service]

    if not typer.confirm(f"Remove {service_info['name']} credentials?"):
        console.print("Cancelled.", style="yellow")
        return

    if delete_credentials(service):
        console.print(f"✅ {service_info['name']} credentials removed.", style="green")
    else:
        console.print(f"❌ Failed to remove {service_info['name']} credentials.", style="red")
        raise typer.Exit(1)

@app.command("clear")
def clear_all():
    """Remove all stored credentials."""
    console.print("[bold red]⚠️  This will remove ALL stored service credentials![/bold red]")

    if not typer.confirm("Are you sure you want to remove all credentials?"):
        console.print("Cancelled.", style="yellow")
        return

    if not typer.confirm("This action cannot be undone. Proceed?"):
        console.print("Cancelled.", style="yellow")
        return

    removed_count = 0
    error_count = 0

    for service_name in SERVICES.keys():
        if delete_credentials(service_name):
            removed_count += 1
        else:
            error_count += 1

    if removed_count > 0:
        console.print(f"✅ Removed credentials for {removed_count} services.", style="green")

    if error_count > 0:
        console.print(f"❌ Failed to remove credentials for {error_count} services.", style="red")

    if removed_count == 0 and error_count == 0:
        console.print("ℹ️  No credentials were found to remove.", style="blue")

@app.command("export")
def export_config(output: str = typer.Option("flaccid-config.json", help="Output file path")):
    """
    Export configuration (non-sensitive data only).

    Args:
        output: Output file path
    """
    import json
    from datetime import datetime

    config_data = {
        "exported_at": datetime.now().isoformat(),
        "services": {}
    }

    for service_name, service_info in SERVICES.items():
        credentials = get_credentials(service_name)

        config_data["services"][service_name] = {
            "name": service_info["name"],
            "configured": bool(credentials and credentials["username"]),
            "description": service_info["description"]
        }

    output_path = Path(output)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    console.print(f"✅ Configuration exported to: {output_path}", style="green")
    console.print("ℹ️  Note: Only configuration status exported, not actual credentials.", style="blue")
