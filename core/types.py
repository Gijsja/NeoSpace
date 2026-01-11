
"""
Core Type Definitions.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ServiceResult:
    """Standard result object for service operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: int = 200
