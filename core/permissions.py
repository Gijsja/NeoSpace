"""
Permissions and Access Control Helpers.
"""
from typing import Any

def check_ownership(resource_owner: Any, current_user: Any) -> bool:
    """
    Verify that the current user owns the resource.
    
    Args:
        resource_owner: The identifier of the resource owner (e.g., user_id int or username str).
        current_user: The identifier of the requesting user.
        
    Returns:
        bool: True if they match, False otherwise.
    """
    if resource_owner is None or current_user is None:
        return False
        
    return resource_owner == current_user
