
import os
import json
import pytest
from core import __version__

def test_version_consistency():
    """
    Ensure the version is consistent across all sources of truth:
    1. core.__version__ (Python runtime)
    2. VERSION file (Deployment)
    3. package.json (Frontend/Assets)
    """
    
    # 1. Read VERSION file
    with open('VERSION', 'r') as f:
        version_file = f.read().strip()
    
    # 2. Read package.json
    with open('package.json', 'r') as f:
        package_json = json.load(f)
        package_version = package_json['version']
    
    # Assert consistency
    assert __version__ == version_file, "core.__version__ differs from VERSION file"
    assert __version__ == package_version, "core.__version__ differs from package.json"
    assert version_file == package_version, "VERSION file differs from package.json"

def test_version_format():
    """Ensure version mimics SemVer (e.g. X.Y.Z)."""
    parts = __version__.split('.')
    assert len(parts) >= 3, "Version should be at least X.Y.Z"
    assert all(p.isdigit() for p in parts[:3]), "Major, Minor, Patch should be integers"
