"""Standard error responses for D&D skill CLIs."""

from __future__ import annotations

from typing import Any, Dict, Optional


def error_response(message: str, *, code: str = "error", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "ok": False,
        "error": message,
        "code": code,
        "details": details or {},
    }


def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, **data}