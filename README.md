### AI Stock Analysis Agents autonomously gather and analyze data, simulate trading scenarios, and update their recommendations without manual intervention. They can be integrated into portfolio trackers or used as standalone advisors, often accessible via chatbots or web dashboards.
 
•	Market Data Agent (market_data_expert) – Fetches real-time stock prices, P/E ratios, EPS, and revenue growth. Responsible for fetching real-time financial data, including stock prices, price-to-earnings (P/E) ratios, earnings per share (EPS), and revenue growth. Ensures that the system has up-to-date market data for analysis.

•	Sentiment Analysis Agent (sentiment_expert) – Analyzes news and social media sentiment for stocks. Categorizes sentiment as positive, neutral, or negative to assess the market mood toward specific stocks.

•	Quantitative Analysis Agent (quant_expert) – Computes stock price trends, moving averages, and volatility metrics. Helps detect trends, potential breakout points, and risk levels based on past market data.

•	Investment Strategy Agent (strategy_expert) – Uses all available insights to generate a Buy/Sell/Hold recommendation. Determines whether a stock should be marked as a Buy, Sell, or Hold based on calculated risks and opportunities.

•	Supervisor Agent (market_supervisor) – Manages all agents, ensuring smooth task delegation and decision-making. Coordinates multi-agent teractions, monitors workflow efficiency and aggregates final recommendations for the user.


### Technical documentation

---

## Agents

### 1. `stock_query_agent`
**Purpose:** Identify a stock symbol (ticker) from a user query, fetch market data, fundamental indicators, technical analysis, and relevant news.  

- Uses `function_tool` to integrate with `StockAnalyzer` and `get_news`.
- Instruction set (`STOCK_QUERY_INSTRUCTION`) specifies the broad range of financial terms it can parse.
- Returns a structured `StocksQueryOutput` with basic info, fundamentals, technical data, news, and trading signals.

### 2. `technical_agent`
**Purpose:** Interpret technical data provided by `stock_query_agent`.  
Summarizes trends, identifies support/resistance, evaluates indicators (moving averages, RSI, MACD), and notes chart patterns.  
Outputs fields such as `trend_analysis`, `support_levels`, `resistance_levels`, etc.

### 3. `fundamental_agent`
**Purpose:** Analyze fundamentals like earnings, revenue growth, profit margins, valuation ratios, and debt.  
Produces a structured summary including `earnings_analysis`, `revenue_growth`, `profit_margins`, and `debt_analysis`.

### 4. `news_agent`
**Purpose:** Examine news articles, assess sentiment, and extract impactful events or industry trends.  
Outputs `market_impact`, `sentiment_analysis`, `key_events`, and `industry_trends`.

### 5. `investment_agent`
**Purpose:** Combine the results of technical, fundamental, and news analyses into a detailed investment recommendation.  
Outputs `company_overview` and `investment_recommendation`.

### 6. `stock_manager_agent` (`SupervisorManager`)
Orchestrates all agents:

1. Retrieve stock data via `query_agent`.
2. Run technical, fundamental, and (if available) news analysis.
3. Generate an overall investment recommendation.
4. Prepare a markdown report summarizing all findings.

---

## Data Retrieval Utilities

### `StockAnalyzer` (`stock/stock_data.py`)
- Wraps `yfinance` to obtain basic info, technical indicators, financial statements, and signals.
- Calculates moving averages, RSI, MACD, Bollinger Bands, Stochastic Oscillator, and trading signals.

### `StockNewsExtractor` (`stock/stock_news.py`)
- Aggregates news from Yahoo Finance, Finviz, MarketWatch, Google News, Seeking Alpha, etc.
- Performs sentiment analysis on articles.
- Exposes `get_comprehensive_news()` which merges results, removes duplicates, and sorts by date.

### `StockSymbolFinder` (`stock/stock_symbol.py`)
- Determines a ticker symbol from a company name.
- Searches Yahoo Finance, yfinance validation, and optionally Alpha Vantage or Finnhub.
- Uses fuzzy matching to rank results, providing quick lookup via `quick_symbol_lookup()`.

---

## Entry Point (`main.py`)
Implements a minimal Gradio interface:

- Textbox for entering a company query.
- “Run” button triggers `SupervisorManager().run(query)` asynchronously.
- Displays the generated markdown report within the UI.

---

## Execution Flow

```text
User Query
   │
   ▼
SupervisorManager.run(query)
   ├─ query_agent → StockAnalyzer + News retrieval
   ├─ technical_agent ← technical_data
   ├─ fundamental_agent ← fundamental_data
   ├─ news_agent (if news present) ← news articles
   ├─ investment_agent ← aggregated analysis
   └─ data_report() → final report
   ▼
Markdown report displayed in Gradio UI

