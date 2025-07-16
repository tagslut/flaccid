"""Dynamic plugin discovery utilities."""

from __future__ import annotations

from importlib import util as import_util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, Type

from .base import MetadataProviderPlugin, LyricsProviderPlugin


class PluginLoader:
    """Discover provider plugins in the given directories."""

    def __init__(self, *paths: str | Path) -> None:
        self.paths = [Path(p) for p in paths]

    def _load_module(self, path: Path) -> ModuleType | None:
        """Load a module from ``path`` using a package name."""
        name = f"flaccid.plugins.{path.stem}"
        loader = SourceFileLoader(name, str(path))
        spec = import_util.spec_from_loader(name, loader)
        if not spec:
            return None
        module = import_util.module_from_spec(spec)
        sys.modules[name] = module
        loader.exec_module(module)
        return module

    def discover(self) -> Dict[str, Type[MetadataProviderPlugin]]:
        """Return mapping of provider name to plugin class."""
        found: Dict[str, Type[MetadataProviderPlugin]] = {}
        for base in self.paths:
            if not base.exists():
                continue
            skip = {"loader", "registry", "__init__", "base"}
            for file in base.glob("*.py"):
                if file.name.startswith("_") or file.stem in skip:
                    continue
                module = self._load_module(file)
                if not module:
                    continue
                for attr in vars(module).values():
                    if not isinstance(attr, type):
                        continue
                    if (
                        issubclass(attr, MetadataProviderPlugin)
                        and attr is not MetadataProviderPlugin
                    ) or (
                        issubclass(attr, LyricsProviderPlugin)
                        and attr is not LyricsProviderPlugin
                    ):
                        name = getattr(attr, "NAME", file.stem).lower()
                        found[name] = attr
        return found
