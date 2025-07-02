import pandas as pd
from app.stock.stock_news import StockNewsExtractor


def test_analyze_sentiment_positive():
    extractor = StockNewsExtractor()
    result = extractor.analyze_sentiment('Strong buy recommendation with profit')
    assert result['sentiment'] == 'Positive'


def test_get_news_summary():
    extractor = StockNewsExtractor()
    df = pd.DataFrame({
        'source': ['Yahoo', 'Yahoo', 'Finviz'],
        'extraction_method': ['Yahoo', 'Yahoo', 'Finviz'],
        'sentiment': ['Positive', 'Negative', 'Positive'],
        'published': ['2024-01-01', '2024-01-02', '2024-01-03'],
    })
    summary = extractor.get_news_summary(df)
    assert summary['total_articles'] == 3
    assert summary['sources']['Yahoo'] == 2
