"""Provider factory — resolves the correct data provider for any symbol/asset class.

This centralizes provider selection and ensures all asset classes are routed
through their correct normalized provider.
"""
from typing import Optional
from app.data.base_provider import BaseDataProvider
from app.config.logging import logger


def get_provider(asset_class: str, symbol: Optional[str] = None) -> BaseDataProvider:
    """Return the appropriate data provider for the given asset class.

    Args:
        asset_class: One of INDIAN_EQUITY, INDIAN_INDEX, FOREX, CRYPTO, GOLD
        symbol: Optional symbol for additional routing hints

    Returns:
        A BaseDataProvider instance for the requested asset class
    """
    from app.data.indian_provider import IndianMarketDataProvider
    from app.data.forex_provider import ForexDataProvider
    from app.data.crypto_provider import CryptoDataProvider
    from app.data.gold_provider import GoldDataProvider

    if asset_class in ("INDIAN_EQUITY", "INDIAN_INDEX"):
        return IndianMarketDataProvider()
    elif asset_class == "FOREX":
        return ForexDataProvider()
    elif asset_class == "CRYPTO":
        return CryptoDataProvider()
    elif asset_class == "GOLD":
        return GoldDataProvider()
    else:
        logger.warning(f"Unknown asset class '{asset_class}'. Falling back to IndianMarketDataProvider.")
        return IndianMarketDataProvider()


def get_provider_for_symbol(symbol: str) -> BaseDataProvider:
    """Infer and return the appropriate data provider for a given symbol."""
    from app.data.universe import ALL_INSTRUMENTS

    inst = ALL_INSTRUMENTS.get(symbol)
    if inst:
        return get_provider(inst.asset_class, symbol)

    # Heuristic fallback based on symbol format
    if symbol.endswith("=X"):
        return get_provider("FOREX")
    elif symbol.startswith("^"):
        return get_provider("INDIAN_INDEX")
    elif "/" in symbol and ("USDT" in symbol or "BTC" in symbol or "ETH" in symbol):
        return get_provider("CRYPTO")
    elif symbol in ("XAUUSD", "GC=F") or "GOLD" in symbol.upper():
        return get_provider("GOLD")
    else:
        return get_provider("INDIAN_EQUITY")
