from flaccid.plugins import PLUGINS


def test_builtin_plugins_present():
    # Ensure built-in plugins are discovered without ImportError
    names = {"apple", "beatport", "discogs", "qobuz", "tidal"}
    assert names.issubset(PLUGINS.keys())
