"""Global test fixtures and setup."""
import pytest
import tempfile
import sys
from pathlib import Path

@pytest.fixture
def temp_dir():
    if sys.version_info >= (3, 10):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            yield Path(tmpdir)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
