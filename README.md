### AI Stock Analysis Agents autonomously gather and analyze data, simulate trading scenarios, and update their recommendations without manual intervention. They can be integrated into portfolio trackers or used as standalone advisors, often accessible via chatbots or web dashboards.
 
•	Market Data Agent (market_data_expert) – Fetches real-time stock prices, P/E ratios, EPS, and revenue growth. Responsible for fetching real-time financial data, including stock prices, price-to-earnings (P/E) ratios, earnings per share (EPS), and revenue growth. Ensures that the system has up-to-date market data for analysis.

•	Sentiment Analysis Agent (sentiment_expert) – Analyzes news and social media sentiment for stocks. Categorizes sentiment as positive, neutral, or negative to assess the market mood toward specific stocks.

•	Quantitative Analysis Agent (quant_expert) – Computes stock price trends, moving averages, and volatility metrics. Helps detect trends, potential breakout points, and risk levels based on past market data.

•	Investment Strategy Agent (strategy_expert) – Uses all available insights to generate a Buy/Sell/Hold recommendation. Determines whether a stock should be marked as a Buy, Sell, or Hold based on calculated risks and opportunities.

•	Supervisor Agent (market_supervisor) – Manages all agents, ensuring smooth task delegation and decision-making. Coordinates multi-agent teractions, monitors workflow efficiency and aggregates final recommendations for the user.
