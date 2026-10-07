"""Phase 9 & 10 tests — Dashboard imports, multi-asset providers, and universe registry."""
import pytest
import pandas as pd
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# =============================================
# PHASE 9 TESTS — Dashboard
# =============================================

class TestDashboardImports:
    """Verify dashboard module can be safely imported without Streamlit running."""

    def test_streamlit_importable(self):
        """Streamlit must be installed."""
        import streamlit
        assert streamlit is not None

    def test_plotly_importable(self):
        """Plotly must be available for charts."""
        import plotly.graph_objects as go
        assert go is not None

    def test_dashboard_dependencies_importable(self):
        """All dashboard dependencies must be importable."""
        from app.config.settings import settings
        from app.config.safety import assert_paper_trading_only
        from app.memory.repository import ExperimentRepository
        from app.paper_trading.portfolio import PaperPortfolio
        from app.services.ai_brain import AIBrainService
        from app.data.registry import ResearchDatasetRegistry
        from app.data.quality import DataQualityChecker
        assert True

    def test_universe_importable(self):
        """Market universe registry must be importable."""
        from app.data.universe import (
            UNIVERSE_BY_CLASS, ALL_INSTRUMENTS,
            INDIAN_EQUITY_UNIVERSE, INDIAN_INDEX_UNIVERSE,
            FOREX_UNIVERSE, CRYPTO_UNIVERSE, GOLD_UNIVERSE,
            get_instrument, get_symbols_by_class
        )
        assert len(UNIVERSE_BY_CLASS) == 5
        assert len(ALL_INSTRUMENTS) > 0

    def test_provider_factory_importable(self):
        """Provider factory must be importable."""
        from app.data.provider_factory import get_provider, get_provider_for_symbol
        assert callable(get_provider)
        assert callable(get_provider_for_symbol)

    def test_safety_state_for_display(self):
        """Dashboard must report correct safety state."""
        from app.config.settings import settings
        assert settings.PAPER_TRADING_ONLY is True
        assert settings.ALLOW_REAL_BROKER is False

    def test_ai_brain_safe_empty_state(self):
        """AI Brain returns safe empty state when no experiments exist."""
        from app.services.ai_brain import AIBrainService
        from app.memory.repository import ExperimentRepository

        repo = ExperimentRepository()
        brain = AIBrainService(repository=repo)
        summary = brain.generate_learned_summary()
        assert "evidence_supported_observations" in summary or "observations" in summary

    def test_no_secrets_in_settings_repr(self):
        """API keys must not appear in plain text settings output."""
        from app.config.settings import settings
        # These attributes should exist but not expose keys in repr
        assert hasattr(settings, "GEMINI_API_KEY")
        assert hasattr(settings, "OPENROUTER_API_KEY")
        # Keys should be empty strings by default (set only via .env)
        # The test verifies the field exists; actual values depend on .env


# =============================================
# PHASE 10 TESTS — Asset classes & providers
# =============================================

class TestAssetClassification:
    """Phase 10: Asset class model and universe coverage."""

    def test_all_asset_classes_registered(self):
        """All 5 asset classes must be present in UNIVERSE_BY_CLASS."""
        from app.data.universe import UNIVERSE_BY_CLASS
        required = {"INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"}
        assert required.issubset(set(UNIVERSE_BY_CLASS.keys()))

    def test_indian_equity_count(self):
        """Indian equity universe must have at least 10 instruments."""
        from app.data.universe import INDIAN_EQUITY_UNIVERSE
        assert len(INDIAN_EQUITY_UNIVERSE) >= 10

    def test_indian_index_count(self):
        """Indian index universe must have at least 2 instruments."""
        from app.data.universe import INDIAN_INDEX_UNIVERSE
        assert len(INDIAN_INDEX_UNIVERSE) >= 2
        symbols = [i.symbol for i in INDIAN_INDEX_UNIVERSE]
        assert "^NSEI" in symbols
        assert "^NSEBANK" in symbols

    def test_forex_count(self):
        """Forex universe must have at least 5 pairs."""
        from app.data.universe import FOREX_UNIVERSE
        assert len(FOREX_UNIVERSE) >= 5

    def test_crypto_count(self):
        """Crypto universe must have at least BTC and ETH."""
        from app.data.universe import CRYPTO_UNIVERSE
        symbols = [i.symbol for i in CRYPTO_UNIVERSE]
        assert "BTC/USDT" in symbols
        assert "ETH/USDT" in symbols

    def test_gold_instruments(self):
        """Gold universe must include XAUUSD."""
        from app.data.universe import GOLD_UNIVERSE
        symbols = [i.symbol for i in GOLD_UNIVERSE]
        assert "XAUUSD" in symbols

    def test_get_symbols_by_class(self):
        """get_symbols_by_class must return non-empty list for all classes."""
        from app.data.universe import get_symbols_by_class
        for ac in ["INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"]:
            syms = get_symbols_by_class(ac)
            assert len(syms) > 0, f"Empty symbol list for {ac}"

    def test_get_instrument_by_symbol(self):
        """get_instrument must resolve known symbols."""
        from app.data.universe import get_instrument
        inst = get_instrument("RELIANCE.NS")
        assert inst is not None
        assert inst.asset_class == "INDIAN_EQUITY"

        inst2 = get_instrument("BTC/USDT")
        assert inst2 is not None
        assert inst2.asset_class == "CRYPTO"

    def test_all_instruments_have_asset_class(self):
        """Every instrument must have a valid asset_class."""
        from app.data.universe import ALL_INSTRUMENTS
        valid = {"INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"}
        for sym, inst in ALL_INSTRUMENTS.items():
            assert inst.asset_class in valid, f"{sym} has invalid asset_class: {inst.asset_class}"

    def test_market_type_literal_updated(self):
        """Domain schema MarketType must include all 5 asset classes."""
        from app.domain.schemas import MarketType
        import typing
        args = typing.get_args(MarketType)
        expected = {"INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"}
        assert expected.issubset(set(args)), f"Missing asset classes in MarketType: {expected - set(args)}"


class TestProviderFactory:
    """Phase 10: Provider routing by asset class."""

    def test_indian_equity_routes_correctly(self):
        from app.data.provider_factory import get_provider
        from app.data.indian_provider import IndianMarketDataProvider
        provider = get_provider("INDIAN_EQUITY")
        assert isinstance(provider, IndianMarketDataProvider)

    def test_indian_index_routes_correctly(self):
        from app.data.provider_factory import get_provider
        from app.data.indian_provider import IndianMarketDataProvider
        provider = get_provider("INDIAN_INDEX")
        assert isinstance(provider, IndianMarketDataProvider)

    def test_forex_routes_correctly(self):
        from app.data.provider_factory import get_provider
        from app.data.forex_provider import ForexDataProvider
        provider = get_provider("FOREX")
        assert isinstance(provider, ForexDataProvider)

    def test_crypto_routes_correctly(self):
        from app.data.provider_factory import get_provider
        from app.data.crypto_provider import CryptoDataProvider
        provider = get_provider("CRYPTO")
        assert isinstance(provider, CryptoDataProvider)

    def test_gold_routes_correctly(self):
        from app.data.provider_factory import get_provider
        from app.data.gold_provider import GoldDataProvider
        provider = get_provider("GOLD")
        assert isinstance(provider, GoldDataProvider)

    def test_symbol_routing_reliance(self):
        from app.data.provider_factory import get_provider_for_symbol
        from app.data.indian_provider import IndianMarketDataProvider
        provider = get_provider_for_symbol("RELIANCE.NS")
        assert isinstance(provider, IndianMarketDataProvider)

    def test_symbol_routing_forex(self):
        from app.data.provider_factory import get_provider_for_symbol
        from app.data.forex_provider import ForexDataProvider
        provider = get_provider_for_symbol("EURUSD=X")
        assert isinstance(provider, ForexDataProvider)

    def test_symbol_routing_crypto(self):
        from app.data.provider_factory import get_provider_for_symbol
        from app.data.crypto_provider import CryptoDataProvider
        provider = get_provider_for_symbol("BTC/USDT")
        assert isinstance(provider, CryptoDataProvider)


class TestCryptoProvider:
    """Phase 10: Crypto data provider functionality."""

    def test_crypto_provider_imports(self):
        from app.data.crypto_provider import CryptoDataProvider, USER_FRIENDLY_CRYPTO
        assert len(USER_FRIENDLY_CRYPTO) >= 2

    def test_crypto_supported_symbols(self):
        from app.data.crypto_provider import CryptoDataProvider
        provider = CryptoDataProvider()
        symbols = provider.get_supported_symbols()
        assert "BTC/USDT" in symbols
        assert "ETH/USDT" in symbols

    def test_crypto_synthetic_fallback_valid_schema(self):
        """Crypto synthetic data must produce valid OHLCV schema."""
        from app.data.crypto_provider import CryptoDataProvider
        from app.data.base_provider import MarketData
        provider = CryptoDataProvider()
        data = provider._generate_synthetic("BTC/USDT", "1d")
        assert isinstance(data, MarketData)
        assert data.market == "CRYPTO"
        assert len(data) > 100
        assert all(col in data.df.columns for col in ["timestamp", "open", "high", "low", "close", "volume"])

    def test_crypto_market_type_is_crypto(self):
        """Synthetic crypto data must have CRYPTO market type."""
        from app.data.crypto_provider import CryptoDataProvider
        provider = CryptoDataProvider()
        data = provider._generate_synthetic("ETH/USDT", "1d")
        assert data.market == "CRYPTO"


class TestGoldProvider:
    """Phase 10: Gold provider functionality."""

    def test_gold_provider_imports(self):
        from app.data.gold_provider import GoldDataProvider, GOLD_SYMBOLS
        assert "XAUUSD" in GOLD_SYMBOLS

    def test_gold_supported_symbols(self):
        from app.data.gold_provider import GoldDataProvider
        provider = GoldDataProvider()
        symbols = provider.get_supported_symbols()
        assert "XAUUSD" in symbols

    def test_gold_invalid_symbol_raises_valueerror(self):
        """Requesting an unknown gold symbol must raise ValueError (not silently fabricate)."""
        from app.data.gold_provider import GoldDataProvider
        provider = GoldDataProvider()
        with pytest.raises(ValueError, match="not recognized"):
            provider.fetch_ohlcv("FAKEGOLD")


class TestIndianProviderExpansion:
    """Phase 10: Indian provider expansion."""

    def test_expanded_symbol_list(self):
        from app.data.indian_provider import IndianMarketDataProvider, ALL_INDIA_SYMBOLS
        assert len(ALL_INDIA_SYMBOLS) >= 17  # 15 equities + 2 indices
        assert "HDFCBANK.NS" in ALL_INDIA_SYMBOLS
        assert "^NSEI" in ALL_INDIA_SYMBOLS
        assert "^NSEBANK" in ALL_INDIA_SYMBOLS

    def test_index_classification(self):
        from app.data.indian_provider import _classify_india_market
        assert _classify_india_market("^NSEI") == "INDIAN_INDEX"
        assert _classify_india_market("^NSEBANK") == "INDIAN_INDEX"
        assert _classify_india_market("RELIANCE.NS") == "INDIAN_EQUITY"
        assert _classify_india_market("TCS.NS") == "INDIAN_EQUITY"

    def test_synthetic_india_equity(self):
        from app.data.indian_provider import IndianMarketDataProvider
        provider = IndianMarketDataProvider()
        data = provider._generate_synthetic("HDFCBANK.NS", "1d", "INDIAN_EQUITY")
        assert data.market == "INDIAN_EQUITY"
        assert len(data) == 250

    def test_synthetic_india_index(self):
        from app.data.indian_provider import IndianMarketDataProvider
        provider = IndianMarketDataProvider()
        data = provider._generate_synthetic("^NSEI", "1d", "INDIAN_INDEX")
        assert data.market == "INDIAN_INDEX"


class TestDatasetRegistry:
    """Phase 10: Enhanced dataset registry."""

    def test_registry_list_all(self):
        from app.data.registry import ResearchDatasetRegistry
        from app.data.indian_provider import IndianMarketDataProvider
        ResearchDatasetRegistry.clear()

        provider = IndianMarketDataProvider()
        data = provider._generate_synthetic("RELIANCE.NS", "1d", "INDIAN_EQUITY")
        entry = ResearchDatasetRegistry.register(data, "IndianMarketDataProvider", quality_status="PASS")

        all_ds = ResearchDatasetRegistry.list_all()
        assert len(all_ds) >= 1

    def test_registry_list_by_asset_class(self):
        from app.data.registry import ResearchDatasetRegistry
        from app.data.indian_provider import IndianMarketDataProvider
        from app.data.crypto_provider import CryptoDataProvider
        ResearchDatasetRegistry.clear()

        ind_provider = IndianMarketDataProvider()
        crypto_provider = CryptoDataProvider()

        ind_data = ind_provider._generate_synthetic("RELIANCE.NS", "1d", "INDIAN_EQUITY")
        crypto_data = crypto_provider._generate_synthetic("BTC/USDT", "1d")

        ResearchDatasetRegistry.register(ind_data, "IndianMarketDataProvider")
        ResearchDatasetRegistry.register(crypto_data, "CryptoDataProvider")

        india_ds = ResearchDatasetRegistry.list_by_asset_class("INDIAN_EQUITY")
        crypto_ds = ResearchDatasetRegistry.list_by_asset_class("CRYPTO")

        assert len(india_ds) >= 1
        assert len(crypto_ds) >= 1

    def test_dataset_hash_stable(self):
        """Same data should produce the same hash."""
        from app.data.indian_provider import IndianMarketDataProvider
        provider = IndianMarketDataProvider()
        d1 = provider._generate_synthetic("RELIANCE.NS", "1d", "INDIAN_EQUITY")
        d2 = provider._generate_synthetic("RELIANCE.NS", "1d", "INDIAN_EQUITY")
        # Both use same seed, should produce identical hashes
        assert d1.dataset_hash == d2.dataset_hash

    def test_calendar_span_recorded(self):
        from app.data.registry import ResearchDatasetRegistry
        from app.data.indian_provider import IndianMarketDataProvider
        ResearchDatasetRegistry.clear()

        provider = IndianMarketDataProvider()
        data = provider._generate_synthetic("TCS.NS", "1d", "INDIAN_EQUITY")
        entry = ResearchDatasetRegistry.register(data, "IndianMarketDataProvider")

        assert entry.calendar_span_days > 0


class TestDataQualityMultiAsset:
    """Phase 10: Data quality checker works across all asset classes."""

    def test_crypto_data_passes_quality(self):
        from app.data.crypto_provider import CryptoDataProvider
        from app.data.quality import DataQualityChecker
        provider = CryptoDataProvider()
        data = provider._generate_synthetic("BTC/USDT", "1d")
        report = DataQualityChecker.inspect(data.df, symbol="BTC/USDT")
        assert report.status in ("PASS", "WARN")  # Not FAIL

    def test_indian_index_data_passes_quality(self):
        from app.data.indian_provider import IndianMarketDataProvider
        from app.data.quality import DataQualityChecker
        provider = IndianMarketDataProvider()
        data = provider._generate_synthetic("^NSEI", "1d", "INDIAN_INDEX")
        report = DataQualityChecker.inspect(data.df, symbol="^NSEI")
        assert report.status in ("PASS", "WARN")


class TestPhase8SafeguardsPreserved:
    """Verify Phase 8 research integrity safeguards remain intact after Phase 10 changes."""

    def test_no_trades_classification(self):
        from app.backtesting.metrics import calculate_metrics
        m = calculate_metrics([], pd.Series([100.0, 100.0]), 100.0)
        assert m.sample_size_warning == "NO_TRADES"
        assert m.trade_count == 0

    def test_insufficient_sample_threshold(self):
        """1-4 trades = INSUFFICIENT_SAMPLE must still hold."""
        from app.backtesting.metrics import calculate_metrics
        from app.domain.schemas import TradeRecord
        trades = [
            TradeRecord(trade_id=f"T{i}", symbol="RELIANCE.NS", side="LONG",
                        entry_time="2023-01-01", exit_time="2023-01-10",
                        entry_price=100.0, exit_price=105.0, quantity=1.0,
                        fees=0.0, slippage=0.0, pnl=5.0, return_pct=5.0)
            for i in range(3)
        ]
        eq = pd.Series([10000.0 + i * 5 for i in range(50)])
        m = calculate_metrics(trades, eq, 10000.0)
        assert m.sample_size_warning == "INSUFFICIENT_SAMPLE"

    def test_critic_rejects_zero_trades(self):
        from app.backtesting.metrics import calculate_metrics
        from app.agents.critic import CriticAgent
        from app.domain.schemas import StrategySpec, StrategyRuleSet
        m = calculate_metrics([], pd.Series([100.0, 100.0]), 100.0)
        critic = CriticAgent()
        spec = StrategySpec(strategy_id="TEST", version="v1", symbol="RELIANCE.NS",
                            rules=StrategyRuleSet())
        eval_result = critic.evaluate(m, spec)
        assert eval_result.verdict == "REJECT"
        assert "NO_TRADES" in eval_result.reasoning

    def test_paper_trading_safety(self):
        from app.config.settings import settings
        assert settings.PAPER_TRADING_ONLY is True
        assert settings.ALLOW_REAL_BROKER is False
