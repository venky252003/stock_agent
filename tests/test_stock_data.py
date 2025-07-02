import pandas as pd
import pytest
from stock.stock_data import StockAnalyzer, get_alpha_vantage_data

class DummyTicker:
    info = {}
    financials = pd.DataFrame()
    balance_sheet = pd.DataFrame()
    cashflow = pd.DataFrame()
    recommendations = pd.DataFrame()
    def history(self, *args, **kwargs):
        return pd.DataFrame()


def test_calculate_technical_indicators_empty(monkeypatch):
    monkeypatch.setattr('yfinance.Ticker', lambda symbol: DummyTicker())
    analyzer = StockAnalyzer('TEST')
    result = analyzer.calculate_technical_indicators()
    assert result == {}


def test_analyze_stock_signals(monkeypatch):
    monkeypatch.setattr('yfinance.Ticker', lambda symbol: DummyTicker())
    analyzer = StockAnalyzer('TEST')
    technical = {
        'Current Price': 120,
        'SMA 20': 110,
        'SMA 50': 100,
        'RSI': 80,
        'MACD': 1,
        'MACD Signal': 0.5,
    }
    signals = analyzer.analyze_stock_signals(technical)
    assert any('RSI Overbought' in s for s in signals)
    assert any('Price above both SMA 20 and 50' in s for s in signals)
    assert any('MACD above Signal Line' in s for s in signals)


def test_get_alpha_vantage_data(monkeypatch):
    class DummyResponse:
        def __init__(self, json_data):
            self._json = json_data
        def json(self):
            return self._json
    monkeypatch.setattr('requests.get', lambda url: DummyResponse({'MarketCapitalization': '1000'}))
    data = get_alpha_vantage_data('TEST', 'key')
    assert data['Market Cap'] == '1000'
