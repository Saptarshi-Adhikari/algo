"""Absolute Safety Assertion Module.

This module guarantees that the application CANNOT engage in real live trading or call real broker endpoints.
"""
import functools
from app.config.settings import settings
from app.config.logging import logger

class RealMoneyExecutionForbiddenError(PermissionError):
    """Raised if any component attempts real-money execution or broker connection."""
    pass

def assert_paper_trading_only():
    """Verify system-wide paper trading constraint."""
    if not settings.PAPER_TRADING_ONLY or settings.ALLOW_REAL_BROKER:
        logger.critical("SAFETY VIOLATION DETECTED: System is configured to allow real broker execution!")
        raise RealMoneyExecutionForbiddenError(
            "CRITICAL SAFETY VIOLATION: Real-money broker execution is strictly prohibited. "
            "PAPER_TRADING_ONLY must be True and ALLOW_REAL_BROKER must be False."
        )

def paper_trading_guard(func):
    """Decorator ensuring a function runs strictly under paper-trading mode."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        assert_paper_trading_only()
        return func(*args, **kwargs)
    return wrapper
