"""Unit tests for dashboard imports and compilation."""
import pytest

def test_dashboard_compilation():
    # Ensure dashboard app module imports and compiles cleanly
    import dashboard.app
    assert dashboard.app is not None
