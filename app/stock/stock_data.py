import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import warnings

from .stock_symbol import quick_symbol_lookup
from .stock_news import get_news
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self, symbol):
        """
        Initialize the Stock Analyzer with a stock symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
        """
        self.symbol = symbol.upper()
        self.stock = yf.Ticker(self.symbol)
        
    def get_basic_info(self):
        """Get basic stock information"""
        try:
            info = self.stock.info
            basic_data = {
                'Symbol': self.symbol,
                'Company Name': info.get('longName', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Current Price': info.get('currentPrice', 'N/A'),
                'Market Cap': info.get('marketCap', 'N/A'),
                'Currency': info.get('currency', 'N/A')
            }
            return basic_data
        except Exception as e:
            print(f"Error getting basic info: {e}")
            return {}
    
    def get_fundamental_data(self):
        """Get fundamental analysis data"""
        try:
            info = self.stock.info
            
            # Financial ratios and metrics
            fundamental_data = {
                # Valuation Metrics
                'P/E Ratio': info.get('trailingPE', 'N/A'),
                'Forward P/E': info.get('forwardPE', 'N/A'),
                'PEG Ratio': info.get('pegRatio', 'N/A'),
                'Price/Book': info.get('priceToBook', 'N/A'),
                'Price/Sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'Enterprise Value': info.get('enterpriseValue', 'N/A'),
                'EV/Revenue': info.get('enterpriseToRevenue', 'N/A'),
                'EV/EBITDA': info.get('enterpriseToEbitda', 'N/A'),
                
                # Profitability Metrics
                'Profit Margin': info.get('profitMargins', 'N/A'),
                'Operating Margin': info.get('operatingMargins', 'N/A'),
                'Return on Assets': info.get('returnOnAssets', 'N/A'),
                'Return on Equity': info.get('returnOnEquity', 'N/A'),
                'Revenue Growth': info.get('revenueGrowth', 'N/A'),
                'Earnings Growth': info.get('earningsGrowth', 'N/A'),
                
                # Financial Health
                'Total Cash': info.get('totalCash', 'N/A'),
                'Total Debt': info.get('totalDebt', 'N/A'),
                'Debt/Equity': info.get('debtToEquity', 'N/A'),
                'Current Ratio': info.get('currentRatio', 'N/A'),
                'Quick Ratio': info.get('quickRatio', 'N/A'),
                
                # Dividend Information
                'Dividend Rate': info.get('dividendRate', 'N/A'),
                'Dividend Yield': info.get('dividendYield', 'N/A'),
                'Payout Ratio': info.get('payoutRatio', 'N/A'),
                
                # Other Key Metrics
                'Beta': info.get('beta', 'N/A'),
                'Book Value': info.get('bookValue', 'N/A'),
                'Free Cash Flow': info.get('freeCashflow', 'N/A'),
                'Revenue TTM': info.get('totalRevenue', 'N/A'),
                'Net Income TTM': info.get('netIncomeToCommon', 'N/A')
            }
            
            return fundamental_data
        except Exception as e:
            print(f"Error getting fundamental data: {e}")
            return {}
    
    def calculate_technical_indicators(self, period='1y'):
        """Calculate technical indicators"""
        try:
            # Get historical data
            hist = self.stock.history(period=period)
            
            if hist.empty:
                return {}
            
            # Calculate moving averages
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            hist['EMA_12'] = hist['Close'].ewm(span=12).mean()
            hist['EMA_26'] = hist['Close'].ewm(span=26).mean()
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            hist['MACD'] = hist['EMA_12'] - hist['EMA_26']
            hist['MACD_Signal'] = hist['MACD'].ewm(span=9).mean()
            hist['MACD_Histogram'] = hist['MACD'] - hist['MACD_Signal']
            
            # Calculate Bollinger Bands
            hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
            bb_std = hist['Close'].rolling(window=20).std()
            hist['BB_Upper'] = hist['BB_Middle'] + (bb_std * 2)
            hist['BB_Lower'] = hist['BB_Middle'] - (bb_std * 2)
            
            # Calculate Stochastic Oscillator
            low_14 = hist['Low'].rolling(window=14).min()
            high_14 = hist['High'].rolling(window=14).max()
            hist['%K'] = 100 * ((hist['Close'] - low_14) / (high_14 - low_14))
            hist['%D'] = hist['%K'].rolling(window=3).mean()
            
            # Get latest values
            latest = hist.iloc[-1]
            
            technical_data = {
                'Current Price': round(latest['Close'], 2),
                'SMA 20': round(latest['SMA_20'], 2) if not pd.isna(latest['SMA_20']) else 'N/A',
                'SMA 50': round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else 'N/A',
                'SMA 200': round(latest['SMA_200'], 2) if not pd.isna(latest['SMA_200']) else 'N/A',
                'EMA 12': round(latest['EMA_12'], 2) if not pd.isna(latest['EMA_12']) else 'N/A',
                'EMA 26': round(latest['EMA_26'], 2) if not pd.isna(latest['EMA_26']) else 'N/A',
                'RSI': round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else 'N/A',
                'MACD': round(latest['MACD'], 4) if not pd.isna(latest['MACD']) else 'N/A',
                'MACD Signal': round(latest['MACD_Signal'], 4) if not pd.isna(latest['MACD_Signal']) else 'N/A',
                'Bollinger Upper': round(latest['BB_Upper'], 2) if not pd.isna(latest['BB_Upper']) else 'N/A',
                'Bollinger Lower': round(latest['BB_Lower'], 2) if not pd.isna(latest['BB_Lower']) else 'N/A',
                'Stochastic %K': round(latest['%K'], 2) if not pd.isna(latest['%K']) else 'N/A',
                'Stochastic %D': round(latest['%D'], 2) if not pd.isna(latest['%D']) else 'N/A',
                'Volume': latest['Volume'],
                '52 Week High': round(hist['High'].max(), 2),
                '52 Week Low': round(hist['Low'].min(), 2)
            }
            
            return technical_data, hist
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {}, pd.DataFrame()
    
    def get_financial_statements(self):
        """Get financial statements"""
        try:
            financials = {}
            
            # Income Statement
            income_stmt = self.stock.financials
            if not income_stmt.empty:
                financials['Income Statement'] = income_stmt.head()
            
            # Balance Sheet
            balance_sheet = self.stock.balance_sheet
            if not balance_sheet.empty:
                financials['Balance Sheet'] = balance_sheet.head()
            
            # Cash Flow Statement
            cash_flow = self.stock.cashflow
            if not cash_flow.empty:
                financials['Cash Flow'] = cash_flow.head()
            
            return financials
        except Exception as e:
            print(f"Error getting financial statements: {e}")
            return {}
    
    def get_analyst_recommendations(self):
        """Get analyst recommendations"""
        try:
            recommendations = self.stock.recommendations
            if recommendations is not None and not recommendations.empty:
                return recommendations.tail(10)  # Last 10 recommendations
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting analyst recommendations: {e}")
            return pd.DataFrame()
    
    def analyze_stock_signals(self, technical_data):
        """Analyze technical signals"""
        signals = []
        
        try:
            current_price = technical_data.get('Current Price', 0)
            rsi = technical_data.get('RSI', 0)
            sma_20 = technical_data.get('SMA 20', 0)
            sma_50 = technical_data.get('SMA 50', 0)
            macd = technical_data.get('MACD', 0)
            macd_signal = technical_data.get('MACD Signal', 0)
            
            # RSI Signals
            if isinstance(rsi, (int, float)):
                if rsi > 70:
                    signals.append("SELL SIGNAL: RSI Overbought (RSI > 70)")
                elif rsi < 30:
                    signals.append("BUY SIGNAL: RSI Oversold (RSI < 30)")
            
            # Moving Average Signals
            if isinstance(current_price, (int, float)) and isinstance(sma_20, (int, float)) and isinstance(sma_50, (int, float)):
                if current_price > sma_20 > sma_50:
                    signals.append("BUY SIGNAL: Price above both SMA 20 and 50")
                elif current_price < sma_20 < sma_50:
                    signals.append("SELL SIGNAL: Price below both SMA 20 and 50")
            
            # MACD Signals
            if isinstance(macd, (int, float)) and isinstance(macd_signal, (int, float)):
                if macd > macd_signal:
                    signals.append("BUY SIGNAL: MACD above Signal Line")
                else:
                    signals.append("SELL SIGNAL: MACD below Signal Line")
            
            return signals
        except Exception as e:
            print(f"Error analyzing signals: {e}")
            return []
    
    def generate_report(self):
        """Generate comprehensive stock analysis report"""
        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE STOCK ANALYSIS REPORT")
        print(f"{'='*60}")
        
        # Basic Info
        print(f"\n{'BASIC INFORMATION':-^60}")
        basic_info = self.get_basic_info()
        for key, value in basic_info.items():
            print(f"{key:<20}: {value}")
        
        # Fundamental Analysis
        print(f"\n{'FUNDAMENTAL ANALYSIS':-^60}")
        fundamental_data = self.get_fundamental_data()
        for key, value in fundamental_data.items():
            if isinstance(value, float):
                if abs(value) >= 1:
                    print(f"{key:<25}: {value:,.2f}")
                else:
                    print(f"{key:<25}: {value:.4f}")
            else:
                print(f"{key:<25}: {value}")
        
        # Technical Analysis
        print(f"\n{'TECHNICAL ANALYSIS':-^60}")
        technical_data, hist_data = self.calculate_technical_indicators()
        for key, value in technical_data.items():
            if isinstance(value, (int, float)):
                print(f"{key:<20}: {value:,.2f}")
            else:
                print(f"{key:<20}: {value}")
        
        # Trading Signals
        print(f"\n{'TRADING SIGNALS':-^60}")
        signals = self.analyze_stock_signals(technical_data)
        if signals:
            for i, signal in enumerate(signals, 1):
                print(f"{i}. {signal}")
        else:
            print("No clear signals detected")
        
        # Analyst Recommendations
        # print(f"\n{'RECENT ANALYST RECOMMENDATIONS':-^60}")
        # recommendations = self.get_analyst_recommendations()
        # if not recommendations.empty:
        #     print(recommendations[['To Grade', 'From Grade', 'Action']].to_string())
        # else:
        #     print("No recent analyst recommendations available")
        
        return {
            'basic_info': basic_info,
            'fundamental_data': fundamental_data,
            'technical_data': technical_data,
            'signals': signals,
            'historical_data': hist_data
        }

# Alternative API-based approach for additional data
def get_alpha_vantage_data(symbol, api_key):
    """
    Get stock data using Alpha Vantage API (requires free API key)
    Register at: https://www.alphavantage.co/support/#api-key
    """
    try:
        # Company Overview
        url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
        response = requests.get(url)
        data = response.json()
        
        if 'Error Message' not in data and data:
            overview_data = {
                'Market Cap': data.get('MarketCapitalization', 'N/A'),
                'P/E Ratio': data.get('PERatio', 'N/A'),
                'PEG Ratio': data.get('PEGRatio', 'N/A'),
                'Dividend Yield': data.get('DividendYield', 'N/A'),
                'EPS': data.get('EPS', 'N/A'),
                '52 Week High': data.get('52WeekHigh', 'N/A'),
                '52 Week Low': data.get('52WeekLow', 'N/A'),
                'Beta': data.get('Beta', 'N/A')
            }
            return overview_data
        else:
            print("Alpha Vantage API error or invalid API key")
            return {}
    except Exception as e:
        print(f"Error with Alpha Vantage API: {e}")
        return {}

# Example usage and main function
def main():
    """Main function to demonstrate usage"""
    
    # Example 1: Analyze a single stock
    print("Enter stock symbol (e.g., AAPL, MSFT, TSLA): ", end="")
    symbol = input().strip().upper()
    
    if not symbol:
        symbol = "AAPL"  # Default example
    
    print(f"\nAnalyzing {symbol}...")
    
    # Create analyzer instance
    analyzer = StockAnalyzer(symbol)
    
    # Generate comprehensive report
    analysis_results = analyzer.generate_report()
    
    # Example 2: Batch analysis of multiple stocks
    print(f"\n{'BATCH ANALYSIS EXAMPLE':-^60}")
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    
    batch_results = {}
    for sym in symbols:
        try:
            analyzer = StockAnalyzer(sym)
            basic_info = analyzer.get_basic_info()
            technical_data, _ = analyzer.calculate_technical_indicators()
            
            batch_results[sym] = {
                'Price': basic_info.get('Current Price', 'N/A'),
                'RSI': technical_data.get('RSI', 'N/A'),
                'P/E': analyzer.get_fundamental_data().get('P/E Ratio', 'N/A')
            }
        except Exception as e:
            print(f"Error analyzing {sym}: {e}")
    
    # Display batch results
    print(f"\n{'Symbol':<10}{'Price':<12}{'RSI':<10}{'P/E Ratio':<10}")
    print("-" * 42)
    for symbol, data in batch_results.items():
        price = f"${data['Price']}" if isinstance(data['Price'], (int, float)) else str(data['Price'])
        rsi = f"{data['RSI']:.1f}" if isinstance(data['RSI'], (int, float)) else str(data['RSI'])
        pe = f"{data['P/E']:.1f}" if isinstance(data['P/E'], (int, float)) else str(data['P/E'])
        print(f"{symbol:<10}{price:<12}{rsi:<10}{pe:<10}")

