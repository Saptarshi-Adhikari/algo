"""Unit tests for safety enforcement."""
import pytest
from app.config.settings import settings
from app.config.safety import assert_paper_trading_only, paper_trading_guard, RealMoneyExecutionForbiddenError

def test_paper_trading_default_settings():
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    # Calling assert should pass without exception
    assert_paper_trading_only()

def test_safety_guard_decorator():
    @paper_trading_guard
    def dummy_simulated_trade():
        return "SIMULATED_FILL"

    assert dummy_simulated_trade() == "SIMULATED_FILL"

def test_safety_violation_raises():
    original_paper_mode = settings.PAPER_TRADING_ONLY
    try:
        settings.PAPER_TRADING_ONLY = False
        with pytest.raises(RealMoneyExecutionForbiddenError):
            assert_paper_trading_only()
    finally:
        settings.PAPER_TRADING_ONLY = original_paper_mode
