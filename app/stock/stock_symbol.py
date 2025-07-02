import yfinance as yf
import requests
import pandas as pd
import json
from fuzzywuzzy import fuzz, process
import re
import time
from typing import List, Dict, Optional, Tuple

class StockSymbolFinder:
    def __init__(self):
        """Initialize the Stock Symbol Finder"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def search_yahoo_finance(self, company_name: str) -> List[Dict]:
        """
        Search for stock symbols using Yahoo Finance search API
        
        Args:
            company_name (str): Company name to search for
            
        Returns:
            List[Dict]: List of matching stocks with symbol and name
        """
        try:
            # Yahoo Finance search endpoint
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                'q': company_name,
                'lang': 'en-US',
                'region': 'US',
                'quotesCount': 10,
                'newsCount': 0,
                'enableFuzzyQuery': False,
                'quotesQueryId': 'tss_match_phrase_query',
                'multiQuoteQueryId': 'multi_quote_single_token_query'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'quotes' in data:
                for quote in data['quotes']:
                    if quote.get('isYahooFinance', False):
                        result = {
                            'symbol': quote.get('symbol', ''),
                            'name': quote.get('longname') or quote.get('shortname', ''),
                            'exchange': quote.get('exchange', ''),
                            'type': quote.get('quoteType', ''),
                            'sector': quote.get('sector', ''),
                            'industry': quote.get('industry', ''),
                            'source': 'Yahoo Finance'
                        }
                        results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching Yahoo Finance: {e}")
            return []
    
    def search_yfinance_ticker(self, company_name: str) -> List[Dict]:
        """
        Search using yfinance Ticker search functionality
        
        Args:
            company_name (str): Company name to search for
            
        Returns:
            List[Dict]: List of matching stocks
        """
        try:
            # Try common variations of the company name
            variations = [
                company_name,
                company_name.replace('Inc.', '').replace('Corp.', '').replace('Ltd.', '').strip(),
                company_name.replace(' ', ''),
                company_name.split()[0] if ' ' in company_name else company_name
            ]
            
            results = []
            for variation in variations:
                try:
                    # This is a workaround - we'll try to validate potential symbols
                    # by checking if they exist as valid tickers
                    potential_symbols = self._generate_potential_symbols(variation)
                    
                    for symbol in potential_symbols:
                        try:
                            ticker = yf.Ticker(symbol)
                            info = ticker.info
                            
                            if info and 'longName' in info:
                                result = {
                                    'symbol': symbol,
                                    'name': info.get('longName', ''),
                                    'sector': info.get('sector', ''),
                                    'industry': info.get('industry', ''),
                                    'exchange': info.get('exchange', ''),
                                    'type': 'EQUITY',
                                    'source': 'yfinance validation'
                                }
                                
                                # Check if the company name matches reasonably well
                                if self._is_name_match(company_name, info.get('longName', '')):
                                    results.append(result)
                                    
                        except:
                            continue
                            
                except:
                    continue
                    
            return results
            
        except Exception as e:
            print(f"Error in yfinance search: {e}")
            return []
    
    def _generate_potential_symbols(self, company_name: str) -> List[str]:
        """
        Generate potential stock symbols based on company name
        
        Args:
            company_name (str): Company name
            
        Returns:
            List[str]: List of potential symbols
        """
        symbols = []
        
        # Clean the name
        clean_name = re.sub(r'[^\w\s]', '', company_name).upper()
        words = clean_name.split()
        
        if not words:
            return symbols
        
        # Single word company - try variations
        if len(words) == 1:
            word = words[0]
            symbols.extend([
                word[:4],  # First 4 letters
                word[:3],  # First 3 letters  
                word[:2],  # First 2 letters
                word,      # Full word
            ])
        
        # Multiple words - try combinations
        else:
            # First letters of each word
            acronym = ''.join([word[0] for word in words])
            symbols.append(acronym)
            
            # First word variations
            first_word = words[0]
            symbols.extend([
                first_word[:4],
                first_word[:3],
                first_word
            ])
            
            # Combination of first letters
            if len(words) >= 2:
                symbols.append(words[0][:2] + words[1][:2])
                symbols.append(words[0][:3] + words[1][:1])
        
        # Remove duplicates and filter valid symbols
        unique_symbols = list(set(symbols))
        valid_symbols = [s for s in unique_symbols if len(s) >= 1 and len(s) <= 5]
        
        return valid_symbols[:10]  # Limit to prevent too many requests
    
    def _is_name_match(self, search_name: str, company_name: str, threshold: int = 60) -> bool:
        """
        Check if two company names match using fuzzy matching
        
        Args:
            search_name (str): Name being searched for
            company_name (str): Company name from API
            threshold (int): Minimum similarity score (0-100)
            
        Returns:
            bool: True if names match above threshold
        """
        if not search_name or not company_name:
            return False
            
        # Clean names for comparison
        clean_search = re.sub(r'[^\w\s]', '', search_name.lower())
        clean_company = re.sub(r'[^\w\s]', '', company_name.lower())
        
        # Calculate similarity ratio
        ratio = fuzz.ratio(clean_search, clean_company)
        partial_ratio = fuzz.partial_ratio(clean_search, clean_company)
        token_ratio = fuzz.token_sort_ratio(clean_search, clean_company)
        
        # Return True if any ratio exceeds threshold
        return max(ratio, partial_ratio, token_ratio) >= threshold
    
    def search_alpha_vantage(self, company_name: str, api_key: str) -> List[Dict]:
        """
        Search using Alpha Vantage API (requires API key)
        Get free API key at: https://www.alphavantage.co/support/#api-key
        
        Args:
            company_name (str): Company name to search for
            api_key (str): Alpha Vantage API key
            
        Returns:
            List[Dict]: List of matching stocks
        """
        try:
            url = f'https://www.alphavantage.co/query'
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': company_name,
                'apikey': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'bestMatches' in data:
                for match in data['bestMatches']:
                    result = {
                        'symbol': match.get('1. symbol', ''),
                        'name': match.get('2. name', ''),
                        'type': match.get('3. type', ''),
                        'region': match.get('4. region', ''),
                        'market_open': match.get('5. marketOpen', ''),
                        'market_close': match.get('6. marketClose', ''),
                        'timezone': match.get('7. timezone', ''),
                        'currency': match.get('8. currency', ''),
                        'match_score': match.get('9. matchScore', ''),
                        'source': 'Alpha Vantage'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching Alpha Vantage: {e}")
            return []
    
    def search_finnhub(self, company_name: str, api_key: str) -> List[Dict]:
        """
        Search using Finnhub API (requires API key)
        Get free API key at: https://finnhub.io/register
        
        Args:
            company_name (str): Company name to search for
            api_key (str): Finnhub API key
            
        Returns:
            List[Dict]: List of matching stocks
        """
        try:
            url = 'https://finnhub.io/api/v1/search'
            params = {
                'q': company_name,
                'token': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'result' in data:
                for item in data['result']:
                    result = {
                        'symbol': item.get('symbol', ''),
                        'name': item.get('description', ''),
                        'type': item.get('type', ''),
                        'source': 'Finnhub'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching Finnhub: {e}")
            return []
    
    def find_symbol(self, company_name: str, alpha_vantage_key: str = None, 
                   finnhub_key: str = None) -> List[Dict]:
        """
        Find stock symbol using multiple sources
        
        Args:
            company_name (str): Company name to search for
            alpha_vantage_key (str, optional): Alpha Vantage API key
            finnhub_key (str, optional): Finnhub API key
            
        Returns:
            List[Dict]: Combined results from all sources
        """
        print(f"Searching for: {company_name}")
        all_results = []
        
        # Search Yahoo Finance (no API key required)
        print("Searching Yahoo Finance...")
        yahoo_results = self.search_yahoo_finance(company_name)
        all_results.extend(yahoo_results)
        
        # Search using yfinance validation
        print("Validating with yfinance...")
        yf_results = self.search_yfinance_ticker(company_name)
        all_results.extend(yf_results)
        
        # Search Alpha Vantage if API key provided
        if alpha_vantage_key:
            print("Searching Alpha Vantage...")
            av_results = self.search_alpha_vantage(company_name, alpha_vantage_key)
            all_results.extend(av_results)
            time.sleep(0.2)  # Rate limiting
        
        # Search Finnhub if API key provided
        if finnhub_key:
            print("Searching Finnhub...")
            fh_results = self.search_finnhub(company_name, finnhub_key)
            all_results.extend(fh_results)
        
        # Remove duplicates and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(company_name, unique_results)
        
        return ranked_results
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on symbol"""
        seen_symbols = set()
        unique_results = []
        
        for result in results:
            symbol = result.get('symbol', '').upper()
            if symbol and symbol not in seen_symbols:
                seen_symbols.add(symbol)
                unique_results.append(result)
        
        return unique_results
    
    def _rank_results(self, search_name: str, results: List[Dict]) -> List[Dict]:
        """Rank results by relevance to search name"""
        for result in results:
            company_name = result.get('name', '')
            # Calculate match score
            if company_name:
                ratio = fuzz.ratio(search_name.lower(), company_name.lower())
                partial_ratio = fuzz.partial_ratio(search_name.lower(), company_name.lower())
                token_ratio = fuzz.token_sort_ratio(search_name.lower(), company_name.lower())
                result['match_score'] = max(ratio, partial_ratio, token_ratio)
            else:
                result['match_score'] = 0
        
        # Sort by match score descending
        return sorted(results, key=lambda x: x.get('match_score', 0), reverse=True)
    
    def display_results(self, results: List[Dict], max_results: int = 10):
        """Display search results in a formatted table"""
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:")
        print("-" * 100)
        print(f"{'Rank':<4} {'Symbol':<8} {'Company Name':<40} {'Exchange':<10} {'Match%':<7} {'Source':<15}")
        print("-" * 100)
        
        for i, result in enumerate(results[:max_results], 1):
            symbol = result.get('symbol', 'N/A')[:7]
            name = result.get('name', 'N/A')[:39]
            exchange = result.get('exchange', 'N/A')[:9]
            match_score = result.get('match_score', 0)
            source = result.get('source', 'N/A')[:14]
            
            print(f"{i:<4} {symbol:<8} {name:<40} {exchange:<10} {match_score:<7.1f} {source:<15}")

def batch_search_symbols(company_names: List[str], finder: StockSymbolFinder) -> Dict[str, List[Dict]]:
    """
    Search for multiple company symbols at once
    
    Args:
        company_names (List[str]): List of company names to search
        finder (StockSymbolFinder): Finder instance
        
    Returns:
        Dict[str, List[Dict]]: Results for each company
    """
    results = {}
    
    for company_name in company_names:
        print(f"\n{'='*60}")
        results[company_name] = finder.find_symbol(company_name)
        time.sleep(0.5)  # Rate limiting
    
    return results

def main():
    """Main function to demonstrate usage"""
    # Initialize the finder
    finder = StockSymbolFinder()
    
    # Example 1: Single company search
    print("=== SINGLE COMPANY SEARCH ===")
    company_name = input("Enter company name (or press Enter for 'Apple'): ").strip()
    if not company_name:
        company_name = "Tata Motors"
    
    # Search for the symbol
    results = finder.find_symbol(company_name)
    finder.display_results(results)
    
    # Example 2: Batch search
    print(f"\n{'='*60}")
    print("=== BATCH SEARCH EXAMPLE ===")
    
    companies_to_search = [
        "Tata Motors"
    ]
    
    batch_results = batch_search_symbols(companies_to_search, finder)
    
    # Display batch results summary
    print(f"\n{'BATCH SEARCH SUMMARY':-^60}")
    print(f"{'Company':<20} {'Top Symbol':<10} {'Match Score':<12} {'Company Name'}")
    print("-" * 70)
    
    for company, results in batch_results.items():
        if results:
            top_result = results[0]
            symbol = top_result.get('symbol', 'N/A')
            score = top_result.get('match_score', 0)
            name = top_result.get('name', 'N/A')[:30]
            print(f"{company:<20} {symbol:<10} {score:<12.1f} {name}")
        else:
            print(f"{company:<20} {'N/A':<10} {'0':<12} {'No results found'}")
    
    # Example 3: Get best match only
    print(f"\n{'='*60}")
    print("=== GET BEST MATCH FUNCTION ===")
    
    def get_best_symbol_match(company_name: str) -> Optional[str]:
        """Get the best matching symbol for a company name"""
        results = finder.find_symbol(company_name)
        if results and results[0].get('match_score', 0) > 50:
            return results[0].get('symbol')
        return None
    
    # Test with some company names
    test_companies = ["Apple Inc", "Microsoft Corporation", "Tesla Motors", "Invalid Company XYZ"]
    
    for company in test_companies:
        symbol = get_best_symbol_match(company)
        print(f"{company:<25} -> {symbol if symbol else 'Not found'}")

def quick_symbol_lookup(company_name: str) -> str:
    """
    Quick lookup function that returns the best matching symbol
    
    Args:
        company_name (str): Company name to search
        
    Returns:
        str: Best matching stock symbol or empty string if not found
    """
    finder = StockSymbolFinder()
    results = finder.find_symbol(company_name)
    
    if results and results[0].get('match_score', 0) > 60:
        return results[0].get('symbol', '')
    
    return ''

def validate_symbol(symbol: str) -> Dict:
    """
    Validate if a symbol exists and get basic info
    
    Args:
        symbol (str): Stock symbol to validate
        
    Returns:
        Dict: Company information if valid, empty dict if invalid
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if info and 'longName' in info:
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'exchange': info.get('exchange', ''),
                'valid': True
            }
    except:
        pass
    
    return {'valid': False}

