"""
CoWriter — DictTranslator
=========================
A QTranslator subclass that loads translations from JSON files.

This allows per-module translation files to be added without needing
Qt's lrelease tool to compile .ts → .qm files.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QTranslator

if TYPE_CHECKING:
    from PyQt6.QtCore import QAbstractEventDispatcher

logger = logging.getLogger(__name__)


class DictTranslator(QTranslator):
    """QTranslator that reads translations from a JSON dictionary.

    JSON format:
        {
            "ContextName": {
                "source text": "translated text",
                ...
            },
            ...
        }

    Multiple JSON files can be loaded; later files override earlier ones.
    """

    def __init__(self, parent: object = None) -> None:
        super().__init__(parent)
        self._dict: dict[tuple[str, str], str] = {}

    def load_json(self, path: str | Path) -> bool:
        """Load translations from a JSON file.

        Returns True if the file was loaded successfully.
        """
        try:
            path = Path(path)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            logger.warning("Cannot load translations from %s: %s", path, exc)
            return False

        count = 0
        toplevel = data if isinstance(data, dict) else {}
        for context, messages in toplevel.items():
            if context.startswith("_"):
                continue  # skip metadata keys like _comment
            if isinstance(messages, dict):
                for src, trans in messages.items():
                    if trans and trans != src:
                        self._dict[(context, src)] = trans
                        count += 1

        logger.info("Loaded %d translations from %s", count, path.name)
        return True

    def translate(
        self, context: str | None, sourceText: str | None,
        disambiguation: str | None = None, n: int = -1
    ) -> str | None:
        """Override: look up translation in the JSON dictionary."""
        key = (context or "", sourceText or "")
        result = self._dict.get(key)
        if result is not None:
            return result
        # Return None so Qt falls through to the next translator in the chain
        return None

    @property
    def count(self) -> int:
        """Number of translations loaded."""
        return len(self._dict)
