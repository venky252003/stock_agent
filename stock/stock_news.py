import yfinance as yf
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import feedparser
import re
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

class StockNewsExtractor:
    def __init__(self):
        """Initialize the Stock News Extractor"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_yahoo_finance_news(self, symbol, limit=10):
        """
        Get news from Yahoo Finance for a specific stock
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            limit (int): Number of news articles to retrieve
            
        Returns:
            list: List of news articles
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            news_list = []
            for i, article in enumerate(news[:limit]):
                news_item = {
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('link', ''),
                    'published': datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'source': article.get('publisher', ''),
                    'symbol': symbol,
                    'extraction_method': 'Yahoo Finance API'
                }
                news_list.append(news_item)
            
            return news_list
        except Exception as e:
            print(f"Error getting Yahoo Finance news for {symbol}: {e}")
            return []
    
    def get_finviz_news(self, symbol, limit=10):
        """
        Scrape news from Finviz for a specific stock
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of articles to retrieve
            
        Returns:
            list: List of news articles
        """
        try:
            url = f"https://finviz.com/quote.ashx?t={symbol}"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            news_table = soup.find('table', class_='fullview-news-outer')
            
            if news_table:
                rows = news_table.find_all('tr')
                for i, row in enumerate(rows[:limit]):
                    try:
                        # Extract date/time
                        date_cell = row.find('td', align='right')
                        if date_cell:
                            date_text = date_cell.get_text(strip=True)
                        else:
                            date_text = ''
                        
                        # Extract title and link
                        link_cell = row.find('a')
                        if link_cell:
                            title = link_cell.get_text(strip=True)
                            link = link_cell.get('href', '')
                            
                            # Extract source
                            source_span = row.find('span', style=lambda x: x and 'color:#666666' in x)
                            source = source_span.get_text(strip=True) if source_span else 'Finviz'
                            
                            news_item = {
                                'title': title,
                                'summary': '',
                                'url': link,
                                'published': date_text,
                                'source': source,
                                'symbol': symbol,
                                'extraction_method': 'Finviz Scraping'
                            }
                            news_list.append(news_item)
                    except Exception as e:
                        continue
            
            return news_list
        except Exception as e:
            print(f"Error scraping Finviz news for {symbol}: {e}")
            return []
    
    def get_marketwatch_news(self, symbol, limit=10):
        """
        Get news from MarketWatch RSS feed
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of articles to retrieve
            
        Returns:
            list: List of news articles
        """
        try:
            # MarketWatch RSS feed for specific stock
            url = f"https://feeds.marketwatch.com/marketwatch/companyNews/{symbol}/"
            feed = feedparser.parse(url)
            
            news_list = []
            for i, entry in enumerate(feed.entries[:limit]):
                news_item = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': 'MarketWatch',
                    'symbol': symbol,
                    'extraction_method': 'MarketWatch RSS'
                }
                news_list.append(news_item)
            
            return news_list
        except Exception as e:
            print(f"Error getting MarketWatch news for {symbol}: {e}")
            return []
    
    def get_newsapi_stock_news(self, symbol, company_name, api_key, limit=10):
        """
        Get news using NewsAPI (requires API key from newsapi.org)
        
        Args:
            symbol (str): Stock symbol
            company_name (str): Company name for search
            api_key (str): NewsAPI key
            limit (int): Number of articles
            
        Returns:
            list: List of news articles
        """
        try:
            # Search for news about the company
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{company_name}" OR "{symbol}"',
                'sortBy': 'publishedAt',
                'language': 'en',
                'domains': 'reuters.com,bloomberg.com,cnbc.com,marketwatch.com,finance.yahoo.com',
                'pageSize': limit,
                'apiKey': api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            news_list = []
            if data.get('status') == 'ok':
                for article in data.get('articles', []):
                    news_item = {
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'symbol': symbol,
                        'extraction_method': 'NewsAPI'
                    }
                    news_list.append(news_item)
            
            return news_list
        except Exception as e:
            print(f"Error getting NewsAPI news for {symbol}: {e}")
            return []
    
    def get_seeking_alpha_news(self, symbol, limit=10):
        """
        Get news from Seeking Alpha (web scraping)
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of articles
            
        Returns:
            list: List of news articles
        """
        try:
            url = f"https://seekingalpha.com/symbol/{symbol}/news"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            # Look for article containers
            articles = soup.find_all('article', limit=limit)
            
            for article in articles:
                try:
                    # Extract title
                    title_elem = article.find('a', {'data-test': 'article-title'})
                    if not title_elem:
                        title_elem = article.find('h3') or article.find('h2')
                    
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Extract link
                    link = title_elem.get('href', '') if title_elem else ''
                    if link and not link.startswith('http'):
                        link = f"https://seekingalpha.com{link}"
                    
                    # Extract summary
                    summary_elem = article.find('p') or article.find('div', class_='summary')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    # Extract date
                    date_elem = article.find('time') or article.find('span', class_='date')
                    date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    if title:
                        news_item = {
                            'title': title,
                            'summary': summary,
                            'url': link,
                            'published': date,
                            'source': 'Seeking Alpha',
                            'symbol': symbol,
                            'extraction_method': 'Seeking Alpha Scraping'
                        }
                        news_list.append(news_item)
                except Exception as e:
                    continue
            
            return news_list
        except Exception as e:
            print(f"Error scraping Seeking Alpha news for {symbol}: {e}")
            return []
    
    def get_google_news(self, symbol, company_name, limit=10):
        """
        Get news from Google News RSS feed
        
        Args:
            symbol (str): Stock symbol
            company_name (str): Company name
            limit (int): Number of articles
            
        Returns:
            list: List of news articles
        """
        try:
            # Google News RSS feed
            query = f"{company_name} {symbol} stock"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            
            news_list = []
            for i, entry in enumerate(feed.entries[:limit]):
                news_item = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'symbol': symbol,
                    'extraction_method': 'Google News RSS'
                }
                news_list.append(news_item)
            
            return news_list
        except Exception as e:
            print(f"Error getting Google News for {symbol}: {e}")
            return []
    
    def get_alpha_vantage_news(self, symbol, api_key, limit=10):
        """
        Get news using Alpha Vantage API (requires API key)
        
        Args:
            symbol (str): Stock symbol
            api_key (str): Alpha Vantage API key
            limit (int): Number of articles
            
        Returns:
            list: List of news articles
        """
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'limit': limit,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            news_list = []
            if 'feed' in data:
                for article in data['feed']:
                    news_item = {
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'published': article.get('time_published', ''),
                        'source': article.get('source', ''),
                        'symbol': symbol,
                        'sentiment_score': article.get('overall_sentiment_score', 0),
                        'sentiment_label': article.get('overall_sentiment_label', ''),
                        'extraction_method': 'Alpha Vantage API'
                    }
                    news_list.append(news_item)
            
            return news_list
        except Exception as e:
            print(f"Error getting Alpha Vantage news for {symbol}: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """
        Simple sentiment analysis (can be enhanced with NLTK or TextBlob)
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            # Simple keyword-based sentiment analysis
            positive_words = ['buy', 'bullish', 'positive', 'growth', 'profit', 'gain', 'rise', 'increase', 'strong', 'beat', 'outperform']
            negative_words = ['sell', 'bearish', 'negative', 'loss', 'decline', 'fall', 'decrease', 'weak', 'miss', 'underperform']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = 'Positive'
                score = positive_count / (positive_count + negative_count + 1)
            elif negative_count > positive_count:
                sentiment = 'Negative'
                score = -negative_count / (positive_count + negative_count + 1)
            else:
                sentiment = 'Neutral'
                score = 0
            
            return {
                'sentiment': sentiment,
                'score': score,
                'positive_words': positive_count,
                'negative_words': negative_count
            }
        except Exception as e:
            return {'sentiment': 'Neutral', 'score': 0, 'positive_words': 0, 'negative_words': 0}
    
    def get_comprehensive_news(self, symbol, company_name=None, news_api_key=None, alpha_vantage_key=None, sources='all'):
        """
        Get news from multiple sources and combine them
        
        Args:
            symbol (str): Stock symbol
            company_name (str): Company name (optional)
            news_api_key (str): NewsAPI key (optional)
            alpha_vantage_key (str): Alpha Vantage API key (optional)
            sources (str or list): Sources to use ('all', 'free', or list of sources)
            
        Returns:
            pd.DataFrame: Combined news data
        """
        all_news = []
        
        # Define available sources
        free_sources = ['yahoo', 'finviz', 'marketwatch', 'google', 'seeking_alpha']
        paid_sources = ['newsapi', 'alpha_vantage']
        
        if sources == 'all':
            sources_to_use = free_sources + paid_sources
        elif sources == 'free':
            sources_to_use = free_sources
        elif isinstance(sources, list):
            sources_to_use = sources
        else:
            sources_to_use = free_sources
        
        print(f"Extracting news for {symbol} from {len(sources_to_use)} sources...")
        
        # Yahoo Finance
        if 'yahoo' in sources_to_use:
            print("Getting Yahoo Finance news...")
            yahoo_news = self.get_yahoo_finance_news(symbol)
            all_news.extend(yahoo_news)
            time.sleep(1)  # Rate limiting
        
        # Finviz
        if 'finviz' in sources_to_use:
            print("Getting Finviz news...")
            finviz_news = self.get_finviz_news(symbol)
            all_news.extend(finviz_news)
            time.sleep(1)
        
        # MarketWatch
        if 'marketwatch' in sources_to_use:
            print("Getting MarketWatch news...")
            marketwatch_news = self.get_marketwatch_news(symbol)
            all_news.extend(marketwatch_news)
            time.sleep(1)
        
        # Google News
        if 'google' in sources_to_use and company_name:
            print("Getting Google News...")
            google_news = self.get_google_news(symbol, company_name)
            all_news.extend(google_news)
            time.sleep(1)
        
        # Seeking Alpha
        if 'seeking_alpha' in sources_to_use:
            print("Getting Seeking Alpha news...")
            seeking_alpha_news = self.get_seeking_alpha_news(symbol)
            all_news.extend(seeking_alpha_news)
            time.sleep(1)
        
        # NewsAPI (requires API key)
        if 'newsapi' in sources_to_use and news_api_key and company_name:
            print("Getting NewsAPI news...")
            newsapi_news = self.get_newsapi_stock_news(symbol, company_name, news_api_key)
            all_news.extend(newsapi_news)
            time.sleep(1)
        
        # Alpha Vantage (requires API key)
        if 'alpha_vantage' in sources_to_use and alpha_vantage_key:
            print("Getting Alpha Vantage news...")
            av_news = self.get_alpha_vantage_news(symbol, alpha_vantage_key)
            all_news.extend(av_news)
            time.sleep(1)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_news = []
        for news in all_news:
            if news['title'] not in seen_titles:
                seen_titles.add(news['title'])
                # Add sentiment analysis
                sentiment = self.analyze_sentiment(news['title'] + ' ' + news['summary'])
                news.update(sentiment)
                unique_news.append(news)
        
        # Convert to DataFrame
        df = pd.DataFrame(unique_news)
        
        # Sort by published date (newest first)
        if not df.empty and 'published' in df.columns:
            df = df.sort_values('published', ascending=False)
        
        return df
    
    def save_news_to_csv(self, news_df, filename=None):
        """
        Save news data to CSV file
        
        Args:
            news_df (pd.DataFrame): News data
            filename (str): Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_news_{timestamp}.csv"
        
        news_df.to_csv(filename, index=False)
        print(f"News data saved to {filename}")
    
    def get_news_summary(self, news_df):
        """
        Get summary statistics of news data
        
        Args:
            news_df (pd.DataFrame): News data
            
        Returns:
            dict: Summary statistics
        """
        if news_df.empty:
            return {}
        
        summary = {
            'total_articles': len(news_df),
            'sources': news_df['source'].value_counts().to_dict(),
            'extraction_methods': news_df['extraction_method'].value_counts().to_dict(),
            'sentiment_distribution': news_df['sentiment'].value_counts().to_dict() if 'sentiment' in news_df.columns else {},
            'date_range': {
                'earliest': news_df['published'].min() if 'published' in news_df.columns else None,
                'latest': news_df['published'].max() if 'published' in news_df.columns else None
            }
        }
        
        return summary
    
def get_news(symbol, company_name=None, news_api_key=None, alpha_vantage_key=None, sources='all'):
    """

    Get comprehensive news for a specific stock symbol
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        company_name (str): Company name for news search (optional)
        news_api_key (str): NewsAPI key (optional)
        alpha_vantage_key (str): Alpha Vantage API key (optional)
        sources (str or list): Sources to use ('all', 'free', or list of sources)

    Returns:
        pd.DataFrame: Combined news data
    """
    extractor = StockNewsExtractor()
    # Get news from free sources
    news_df = extractor.get_comprehensive_news(
        symbol=symbol,
        company_name=company_name,
        sources='free'  # Use only free sources
    )
    return news_df

# Example usage and main function
def main():
    """Main function to demonstrate usage"""
    
    # Initialize the news extractor
    extractor = StockNewsExtractor()
    
    # Example 1: Get news for a single stock (free sources only)
    print("=== SINGLE STOCK NEWS EXTRACTION ===")
    symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
    company_name = input("Enter company name (optional): ").strip()
    
    if not symbol:
        symbol = "AAPL"
        company_name = "Apple Inc"
    
    print(f"\nExtracting news for {symbol}...")
    
    # Get news from free sources
    news_df = extractor.get_comprehensive_news(
        symbol=symbol,
        company_name=company_name,
        sources='free'  # Use only free sources
    )
    
    # Display results
    if not news_df.empty:
        print(f"\nFound {len(news_df)} news articles:")
        print("\nTop 5 Headlines:")
        for i, row in news_df.head().iterrows():
            print(f"{i+1}. {row['title']}")
            print(f"   Source: {row['source']} | Sentiment: {row.get('sentiment', 'N/A')}")
            print(f"   URL: {row['url'][:100]}...")
            print()
        
        # Get summary
        summary = extractor.get_news_summary(news_df)
        print(f"\nNews Summary:")
        print(f"Total Articles: {summary['total_articles']}")
        print(f"Sources: {summary['sources']}")
        print(f"Sentiment Distribution: {summary['sentiment_distribution']}")
        
        # Save to CSV
        save_option = input("\nSave to CSV? (y/n): ").strip().lower()
        if save_option == 'y':
            extractor.save_news_to_csv(news_df, f"{symbol}_news.csv")
    else:
        print("No news articles found.")
    
    # # Example 2: Multiple stocks batch processing
    # print("\n=== BATCH NEWS EXTRACTION ===")
    # batch_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    # company_names = ['Apple Inc', 'Microsoft', 'Alphabet Inc', 'Tesla Inc', 'Amazon']
    
    # batch_results = {}
    # for symbol, company in zip(batch_symbols, company_names):
    #     print(f"\nProcessing {symbol}...")
    #     try:
    #         # Get limited news for batch processing
    #         news_df = extractor.get_comprehensive_news(
    #             symbol=symbol,
    #             company_name=company,
    #             sources=['yahoo', 'finviz']  # Use only quick sources for batch
    #         )
            
    #         if not news_df.empty:
    #             batch_results[symbol] = {
    #                 'count': len(news_df),
    #                 'latest_headline': news_df.iloc[0]['title'],
    #                 'sentiment': news_df['sentiment'].value_counts().to_dict()
    #             }
    #         else:
    #             batch_results[symbol] = {'count': 0, 'latest_headline': 'No news found', 'sentiment': {}}
                
    #     except Exception as e:
    #         print(f"Error processing {symbol}: {e}")
    #         batch_results[symbol] = {'count': 0, 'latest_headline': 'Error', 'sentiment': {}}
    
    # # Display batch results
    # print("\n=== BATCH RESULTS ===")
    # for symbol, data in batch_results.items():
    #     print(f"\n{symbol}:")
    #     print(f"  Articles: {data['count']}")
    #     print(f"  Latest: {data['latest_headline'][:80]}...")
    #     print(f"  Sentiment: {data['sentiment']}")

if __name__ == "__main__":
    print("Stock News Extractor")
    print("Required packages: pip install yfinance requests pandas beautifulsoup4 feedparser")
    print("Optional: NewsAPI key from newsapi.org, Alpha Vantage key from alphavantage.co")
    print("=" * 70)
    
    main()