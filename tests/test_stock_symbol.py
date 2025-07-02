import pandas as pd
import pytest
from app.stock.stock_symbol import StockSymbolFinder, validate_symbol

class DummyTicker:
    def __init__(self, valid=True):
        self.valid = valid
        self.info = {'longName':'Apple Inc','sector':'Tech','industry':'SW','exchange':'NAS'} if valid else {}


def test_generate_potential_symbols_single_word():
    finder = StockSymbolFinder()
    symbols = finder._generate_potential_symbols('Apple')
    assert 'APPL' in symbols


def test_is_name_match():
    finder = StockSymbolFinder()
    assert finder._is_name_match('Apple Inc', 'Apple Inc.')


def test_deduplicate_results():
    finder = StockSymbolFinder()
    results = [{'symbol':'AAPL','name':'A'}, {'symbol':'AAPL','name':'B'}, {'symbol':'MSFT','name':'C'}]
    unique = finder._deduplicate_results(results)
    assert len(unique) == 2


def test_validate_symbol(monkeypatch):
    monkeypatch.setattr('yfinance.Ticker', lambda sym: DummyTicker(True))
    data = validate_symbol('AAPL')
    assert data['valid']
    monkeypatch.setattr('yfinance.Ticker', lambda sym: DummyTicker(False))
    data = validate_symbol('XXXX')
    assert not data['valid']
