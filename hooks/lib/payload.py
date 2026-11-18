"""Extract the pieces of a Hermes hook payload the kit's hooks care about."""

from typing import Any, Optional


def message_text(payload: dict) -> str:
    """The current user message as plain text, whatever shape it arrived in."""
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    raw = extra.get("user_message")
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return raw.get("text") or ""
    if isinstance(raw, list):
        parts = []
        for item in raw:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return " ".join(parts)
    return ""


def tool_input(payload: dict) -> dict:
    """The tool_input / args object of a tool-call payload."""
    value = payload.get("tool_input")
    if not isinstance(value, dict):
        value = payload.get("args")
    return value if isinstance(value, dict) else {}
