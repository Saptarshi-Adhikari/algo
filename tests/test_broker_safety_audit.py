"""Safety Audit Test Suite verifying ZERO real-money broker execution code exists."""
import pytest
from pathlib import Path
import re
from app.config.settings import settings
from app.config.safety import assert_paper_trading_only, RealMoneyExecutionForbiddenError

def test_paper_trading_setting_assertions():
    """Verify system configuration safety flags."""
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    assert_paper_trading_only()

def test_no_real_broker_order_functions():
    """Scan entire codebase to ensure no real broker order placement functions exist."""
    app_dir = Path(__file__).resolve().parent.parent / "app"
    forbidden_terms = [
        "place_order", "cancel_order", "modify_order", "send_order",
        "live_trading_execute", "broker_credentials", "real_money_execute"
    ]

    py_files = list(app_dir.rglob("*.py"))
    assert len(py_files) > 0, "No python files found in app directory"

    for file_path in py_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            for term in forbidden_terms:
                # Check for function definitions or execution methods matching forbidden terms
                pattern = rf"def\s+{term}\s*\("
                match = re.search(pattern, content, re.IGNORECASE)
                assert not match, f"FORBIDDEN BROKER FUNCTION FOUND in {file_path}: 'def {term}'"
