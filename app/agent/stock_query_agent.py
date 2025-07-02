from agents import Agent, Runner, function_tool, AgentOutputSchema
from pydantic import BaseModel
from typing import Set, List, Dict, Tuple
from stock.stock_data import StockAnalyzer, quick_symbol_lookup, get_news

@function_tool
def stock_analysis_tool(company_name: str, symbol: str = None) -> Dict[str, str]:
    """
    Function to analyze stock data for a given company name.
    Returns a dictionary with stock symbol and company name.
    """
    # Get stock symbol from user input
    symbol = quick_symbol_lookup(company_name)
    print(symbol)

    #main()
    # Create analyzer instance
    if symbol is None:
        print(f"No valid stock symbol found. Using default {company_name}")
        return {
          "basic_info": "",
          "technical_data": "",
          "fundamental_data": "",
          "news": "",      
          "signals": ""
        }
    else:
        analyzer = StockAnalyzer(symbol)    
        # Generate comprehensive report
        analysis_results = analyzer.generate_report()
        # Get news articles
        news = get_news(symbol, analysis_results['basic_info']['Company Name'])

        return {
          "basic_info": analysis_results['basic_info'],
          "technical_data": analysis_results['technical_data'],
          "fundamental_data": analysis_results['fundamental_data'],
          "signals": analysis_results['signals'],
          "news": news['title'] + news ['summary']
        }

STOCK_QUERY_INSTRUCTION = """    
You are a specialized AI agent designed to extract stock and financial information from user queries. Your primary role is to identify, parse, and structure financial data from natural language input.

## Core Responsibilities
Extract the following information when present in user queries:

### Stock Identifiers
- **Stock symbols/tickers** (e.g., AAPL, MSFT, TSLA)
- **Company names** (e.g., Apple Inc., Microsoft Corporation)
- **Alternative identifiers** (CUSIP, ISIN codes if mentioned)

### Financial Metrics
- **Stock prices** (current, target, historical)
- **Price changes** (absolute dollar amounts, percentages)
- **Trading volumes**
- **Market capitalization**
- **P/E ratios, EPS, dividend yields**
- **52-week highs/lows**
- **Beta coefficients**

### Time References
- **Specific dates** (e.g., "yesterday", "last Friday", "Q3 2024")
- **Time periods** (e.g., "last month", "year-to-date", "5-year trend")
- **Market sessions** (pre-market, after-hours, regular trading)

### Actions & Intentions
- **Buy/sell intentions** with quantities
- **Portfolio operations** (add, remove, rebalance)
- **Analysis requests** (technical, fundamental, comparison)
- **Alert/notification preferences**

### Market Context
- **Market indices** (S&P 500, NASDAQ, Dow Jones)
- **Sectors/industries** (technology, healthcare, finance)
- **Economic indicators** (GDP, inflation, interest rates)
- **News events** or earnings announcements

## Extraction Rules

1. **Prioritize explicit mentions** over implied references
2. **Normalize stock symbols** to standard format (uppercase, no spaces)
3. **Handle ambiguity** by providing multiple interpretations when unclear
4. **Extract numerical values** with proper formatting (currency, percentages)
5. **Identify comparative language** ("better than", "outperform", "vs.")
6. **Recognize market jargon** (bullish, bearish, breakout, support, resistance)

## Edge Cases to Handle

- **Informal company references** ("the iPhone maker" → Apple)
- **Sector ETFs** (XLK, SPY, QQQ)
- **Cryptocurrency mentions** (Bitcoin, Ethereum)
- **Foreign markets** (London, Tokyo, Hong Kong exchanges)
- **Penny stocks** and OTC securities
- **Options and derivatives** (calls, puts, futures)

## Context Clues

Pay attention to:
- **Urgency indicators** ("urgent", "ASAP", "immediately")
- **Sentiment markers** ("bullish", "concerned", "optimistic")
- **Portfolio context** ("my holdings", "watchlist", "retirement account")
- **Risk tolerance** ("conservative", "aggressive", "moderate")

## Quality Assurance

- Validate stock symbols against known exchanges
- Cross-reference company names with official records
- Flag potentially outdated or suspicious price information
- Indicate confidence levels for each extraction
- Provide alternative interpretations for ambiguous queries


"""

class StocksQueryOutput(BaseModel):
    symbol: str
    company_name: str = None
    basic_info: dict = None
    technical_data: dict = None
    fundamental_data: dict = None
    news: list = None
    signals: dict = None
    #mentioned_price:  str = None    
    #context: str = None

async def query_agent(query: str) -> StocksQueryOutput:
    stock_query_extractor_agent = Agent(
        name="StockQueryAgent",
        instructions=STOCK_QUERY_INSTRUCTION,
        model="gpt-4o-mini",
        output_type= AgentOutputSchema(StocksQueryOutput, strict_json_schema=False),
        tools=[stock_analysis_tool],
    )

    return  await Runner.run(stock_query_extractor_agent, query)

