"""Helpers for normalizing attachment objects."""

from __future__ import annotations

from typing import Any, Dict, Optional


def normalize_attachment(attachment: object) -> Optional[Dict[str, Any]]:
    """Convert diverse attachment representations into dictionaries."""

    if attachment is None:
        return None

    if isinstance(attachment, dict):
        return attachment

    for attr in ("model_dump", "dict"):
        method = getattr(attachment, attr, None)
        if callable(method):
            try:
                data = method()
            except TypeError:
                try:
                    data = method(exclude_none=False)
                except TypeError:
                    continue
            if isinstance(data, dict):
                return data

    result: Dict[str, Any] = {}
    for key in ("content_type", "name", "filename", "path", "data"):
        if hasattr(attachment, key):
            result[key] = getattr(attachment, key)

    return result or None
