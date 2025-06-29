from agents import Agent, Runner, TResponseInputItem

NEWS_INSTRUCTION = """
You are a specialized News agent designed to analyze stock news articles.
Your task is to analyze and provide insights based on the news articles provided by the user.
## Core Responsibilities
Analyze the news articles provided and generate insights based on the following:
- **Market Impact**: Assess how the news may affect stock prices.
- **Sentiment Analysis**: Determine the sentiment of the news (positive, negative, neutral).
- **Key Events**: Identify significant events or announcements.
- **Industry Trends**: Recognize broader industry trends or implications.
## Output Format
Provide a structured output with the following fields:
- **market_impact**: A brief summary of the potential market impact.
- **sentiment_analysis**: Insights on the sentiment of the news articles.
- **key_events**: Identification of significant events or announcements.
- **industry_trends**: Analysis of broader industry trends or implications.
"""

async def news_agent(result):
    news_analyser_agent = Agent(name = "News Stock Analyser",
                                 instructions = NEWS_INSTRUCTION,
                                 model = "gpt-4o-mini")
    news_message = f"""
        "News Articles" : {result.final_output.news}
    """
    news_input_items: list[TResponseInputItem] = [{"content": news_message, "role": "user"}]
    return await Runner.run(news_analyser_agent, news_input_items)