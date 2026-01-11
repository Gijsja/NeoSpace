"""
HTML Sanitization Utility.
Server-side defense against XSS for user-generated content.
"""

import bleach

# Allowed HTML tags for user content (e.g., bios, messages)
ALLOWED_TAGS = [
    'b', 'i', 'u', 's', 'strong', 'em', 
    'a', 'code', 'pre', 'br',
    'ul', 'ol', 'li',
    'blockquote', 'p',
    'img', 'div', 'span'
]

# Allowed attributes per tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'style'],
    '*': ['class', 'style', 'id']  # Allow class/style/id on any tag for customization
}

# Allowed URL schemes for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def clean_html(content: str) -> str:
    """
    Sanitize HTML content, stripping dangerous tags and attributes.
    
    Args:
        content: Raw HTML string from user input
    
    Returns:
        Sanitized HTML string
    """
    if not content:
        return ""
    
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )


def escape_text(content: str) -> str:
    """
    Escape all HTML in content (no tags allowed).
    Use for plain text fields like usernames, titles.
    
    Args:
        content: Raw text string
    
    Returns:
        HTML-escaped string
    """
    if not content:
        return ""
    
    return bleach.clean(content, tags=[], strip=True)


def linkify_text(content: str) -> str:
    """
    Auto-link URLs in plain text content.
    
    Args:
        content: Text that may contain URLs
    
    Returns:
        Text with URLs wrapped in anchor tags
    """
    if not content:
        return ""
    
    return bleach.linkify(content, callbacks=[_add_noopener])


def _add_noopener(attrs, new=False):
    """Callback to add rel=noopener to links for security."""
    attrs[(None, 'rel')] = 'noopener noreferrer'
    attrs[(None, 'target')] = '_blank'
    return attrs
