from flask import jsonify
from typing import Any, Union

def success_response(data: Union[dict, list, str] = None, **kwargs) -> Any:
    """
    Standard success response: {ok: True, ...}
    Merges dictionary data into top-level for backwards compatibility where possible,
    or places it in 'data' key if explicitly requested or if data is not a dict.
    
    Usage:
        success_response(id=123) -> {"ok": True, "id": 123}
        success_response({"user": "foo"}) -> {"ok": True, "user": "foo"}
    """
    payload = {"ok": True}
    if data is not None:
        if isinstance(data, dict):
            payload.update(data)
        else:
            payload["data"] = data
    
    payload.update(kwargs)
    return jsonify(payload), 200

def error_response(message: str, code: int = 400, **kwargs) -> Any:
    """
    Standard error response: {ok: False, error: msg}
    """
    payload = {"ok": False, "error": message}
    payload.update(kwargs)
    return jsonify(payload), code
