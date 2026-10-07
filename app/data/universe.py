"""Market Universe Registry — Phase 10 multi-asset market catalog.

Defines all supported instruments by asset class with:
- Symbol canonical names
- Provider mapping
- Availability status
- Description and metadata

Provider availability is honest: instruments are marked UNAVAILABLE or LIMITED
rather than fabricating data that doesn't exist.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ProviderAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    LIMITED = "LIMITED"          # Data available but with depth/quality limitations
    UNAVAILABLE = "UNAVAILABLE"  # Provider cannot supply data
    INVALID = "INVALID"          # Symbol rejected by provider
    DATA_QUALITY_FAILED = "DATA_QUALITY_FAILED"
    PENDING = "PENDING"          # Not yet validated


@dataclass
class InstrumentSpec:
    symbol: str
    display_name: str
    asset_class: str           # INDIAN_EQUITY, INDIAN_INDEX, FOREX, CRYPTO, GOLD
    provider: str              # Which provider class handles this
    description: str
    currency: str
    availability: ProviderAvailability = ProviderAvailability.PENDING
    notes: str = ""
    yf_symbol: str = ""       # yfinance ticker if different from symbol


# ============================================================
# Phase 10 Market Universe — Initial Target
# ============================================================

INDIAN_EQUITY_UNIVERSE: List[InstrumentSpec] = [
    InstrumentSpec("RELIANCE.NS", "Reliance Industries", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Reliance Industries", "INR"),
    InstrumentSpec("TCS.NS", "Tata Consultancy Services", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: TCS", "INR"),
    InstrumentSpec("HDFCBANK.NS", "HDFC Bank", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: HDFC Bank", "INR"),
    InstrumentSpec("ICICIBANK.NS", "ICICI Bank", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: ICICI Bank", "INR"),
    InstrumentSpec("INFY.NS", "Infosys", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Infosys", "INR"),
    InstrumentSpec("SBIN.NS", "State Bank of India", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: SBI", "INR"),
    InstrumentSpec("BHARTIARTL.NS", "Bharti Airtel", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Bharti Airtel", "INR"),
    InstrumentSpec("ITC.NS", "ITC Ltd", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: ITC", "INR"),
    InstrumentSpec("LT.NS", "Larsen & Toubro", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: L&T", "INR"),
    InstrumentSpec("AXISBANK.NS", "Axis Bank", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Axis Bank", "INR"),
    InstrumentSpec("KOTAKBANK.NS", "Kotak Mahindra Bank", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Kotak Bank", "INR"),
    InstrumentSpec("HINDUNILVR.NS", "HUL", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Hindustan Unilever", "INR"),
    InstrumentSpec("MARUTI.NS", "Maruti Suzuki", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Maruti", "INR"),
    InstrumentSpec("SUNPHARMA.NS", "Sun Pharma", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Sun Pharma", "INR"),
    InstrumentSpec("BAJFINANCE.NS", "Bajaj Finance", "INDIAN_EQUITY", "IndianMarketDataProvider", "NSE: Bajaj Finance", "INR"),
]

INDIAN_INDEX_UNIVERSE: List[InstrumentSpec] = [
    InstrumentSpec("^NSEI", "Nifty 50", "INDIAN_INDEX", "IndianMarketDataProvider", "NSE: Nifty 50 Index", "INR"),
    InstrumentSpec("^NSEBANK", "Nifty Bank", "INDIAN_INDEX", "IndianMarketDataProvider", "NSE: Nifty Bank Index", "INR"),
]

FOREX_UNIVERSE: List[InstrumentSpec] = [
    InstrumentSpec("EURUSD=X", "EUR/USD", "FOREX", "ForexDataProvider", "Euro / US Dollar", "USD",
                   notes="~250 daily bars from free provider. Use CSV for deep history."),
    InstrumentSpec("GBPUSD=X", "GBP/USD", "FOREX", "ForexDataProvider", "British Pound / US Dollar", "USD",
                   notes="~250 daily bars from free provider."),
    InstrumentSpec("USDJPY=X", "USD/JPY", "FOREX", "ForexDataProvider", "US Dollar / Japanese Yen", "JPY",
                   notes="~250 daily bars from free provider."),
    InstrumentSpec("AUDUSD=X", "AUD/USD", "FOREX", "ForexDataProvider", "Australian Dollar / US Dollar", "USD",
                   notes="~250 daily bars from free provider."),
    InstrumentSpec("USDCAD=X", "USD/CAD", "FOREX", "ForexDataProvider", "US Dollar / Canadian Dollar", "CAD",
                   notes="~250 daily bars from free provider."),
    InstrumentSpec("USDCHF=X", "USD/CHF", "FOREX", "ForexDataProvider", "US Dollar / Swiss Franc", "CHF",
                   notes="~250 daily bars from free provider."),
    InstrumentSpec("USDINR=X", "USD/INR", "FOREX", "ForexDataProvider", "US Dollar / Indian Rupee", "INR",
                   notes="~250 daily bars from free provider."),
]

CRYPTO_UNIVERSE: List[InstrumentSpec] = [
    InstrumentSpec("BTC/USDT", "Bitcoin", "CRYPTO", "CryptoDataProvider", "Bitcoin (USD, via BTC-USD yfinance)", "USD",
                   yf_symbol="BTC-USD"),
    InstrumentSpec("ETH/USDT", "Ethereum", "CRYPTO", "CryptoDataProvider", "Ethereum (USD, via ETH-USD yfinance)", "USD",
                   yf_symbol="ETH-USD"),
    InstrumentSpec("SOL/USDT", "Solana", "CRYPTO", "CryptoDataProvider", "Solana (USD, via SOL-USD yfinance)", "USD",
                   yf_symbol="SOL-USD"),
    InstrumentSpec("BNB/USDT", "BNB", "CRYPTO", "CryptoDataProvider", "BNB (USD, via BNB-USD yfinance)", "USD",
                   yf_symbol="BNB-USD"),
    InstrumentSpec("XRP/USDT", "XRP", "CRYPTO", "CryptoDataProvider", "XRP (USD, via XRP-USD yfinance)", "USD",
                   yf_symbol="XRP-USD"),
]

GOLD_UNIVERSE: List[InstrumentSpec] = [
    InstrumentSpec("XAUUSD", "Gold (USD)", "GOLD", "GoldDataProvider",
                   "Gold spot/futures (USD), via GC=F yfinance", "USD",
                   yf_symbol="GC=F",
                   notes="Gold futures front month. May have limited free history."),
    InstrumentSpec("GOLDBEES.NS", "Gold BeES (India)", "GOLD", "GoldDataProvider",
                   "Nippon India ETF Gold BeES, NSE-traded INR gold ETF", "INR",
                   notes="Indian gold ETF — availability depends on yfinance coverage."),
]

# Full universe indexed by symbol
ALL_INSTRUMENTS: Dict[str, InstrumentSpec] = {}
for instruments in [INDIAN_EQUITY_UNIVERSE, INDIAN_INDEX_UNIVERSE, FOREX_UNIVERSE, CRYPTO_UNIVERSE, GOLD_UNIVERSE]:
    for inst in instruments:
        ALL_INSTRUMENTS[inst.symbol] = inst

# Asset class grouping
UNIVERSE_BY_CLASS: Dict[str, List[InstrumentSpec]] = {
    "INDIAN_EQUITY": INDIAN_EQUITY_UNIVERSE,
    "INDIAN_INDEX": INDIAN_INDEX_UNIVERSE,
    "FOREX": FOREX_UNIVERSE,
    "CRYPTO": CRYPTO_UNIVERSE,
    "GOLD": GOLD_UNIVERSE,
}


def get_instrument(symbol: str) -> Optional[InstrumentSpec]:
    """Look up an instrument by symbol."""
    return ALL_INSTRUMENTS.get(symbol)


def get_symbols_by_class(asset_class: str) -> List[str]:
    """Return symbol list for a given asset class."""
    return [inst.symbol for inst in UNIVERSE_BY_CLASS.get(asset_class, [])]


def get_provider_for_symbol(symbol: str) -> Optional[str]:
    """Return the provider class name for a given symbol."""
    inst = ALL_INSTRUMENTS.get(symbol)
    return inst.provider if inst else None
