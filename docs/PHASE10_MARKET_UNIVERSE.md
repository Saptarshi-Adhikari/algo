# Phase 10: Multi-Asset Class Market Expansion

## Overview
Phase 10 expands the system's market data universe across 5 asset classes with provider routing, data quality validation, and dataset hashing.

## Asset Class Universe & Provider Mapping

| Asset Class | Instruments Included | Primary Data Provider | Depth & Status |
|---|---|---|---|
| **INDIAN_EQUITY** | RELIANCE.NS, TCS.NS, HDFCBANK.NS, ICICIBANK.NS, INFY.NS, SBIN.NS, BHARTIARTL.NS, ITC.NS, KOTAKBANK.NS, LT.NS, AXISBANK.NS, ASIANPAINT.NS, MARUTI.NS, HCLTECH.NS, SUNPHARMA.NS | `IndianMarketDataProvider` (yfinance) | 5.0 Years (1240+ bars) - AVAILABLE |
| **INDIAN_INDEX** | ^NSEI (Nifty 50), ^NSEBANK (Nifty Bank) | `IndianMarketDataProvider` (yfinance) | 5.0 Years - AVAILABLE |
| **FOREX** | EURUSD=X, GBPUSD=X, USDJPY=X, AUDUSD=X, USDCAD=X, USDCHF=X, USDINR=X | `ForexDataProvider` (yfinance) | ~250 bars (LIMITED free depth; fallback synthetic/CSV supported) |
| **CRYPTO** | BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT | `CryptoDataProvider` (ccxt / synthetic fallback) | 500+ bars - AVAILABLE |
| **GOLD** | XAUUSD (GC=F Gold Futures), GOLDBEES.NS (Indian Gold ETF) | `GoldDataProvider` (yfinance / CSV fallback) | Spot/Futures (Honest provider depth limits; no fake gold spot prices) |

## Data Pipeline & Safety Features
1. **Provider Factory Routing**: `get_provider_for_symbol(symbol)` automatically routes symbols to their appropriate normalized provider.
2. **Reproducible SHA-256 Dataset Hashes**: `MarketData` computes a 16-character SHA-256 checksum from normalized OHLCV JSON bytes, registered in `ResearchDatasetRegistry`.
3. **Data Quality Checker**: Validates strict price positivity, non-empty DataFrames, and OHLC logical relationships (`High >= Open/Close` and `Low <= Open/Close`).
4. **Read-Only / Paper Enforcement**: Market data ingestion for Crypto and Gold is strictly read-only. No live broker order execution exists (`ALLOW_REAL_BROKER=False`).
