from agents import Agent, Runner, TResponseInputItem

INVESTMENT_INSTRUCTION = """
You are a specialized Investment agent designed to provide investment recommendations based on technical, Fundamental and News analysis report data.
Your task is to analyze given analysis provided data and generate investment recommendations.
The final output should be in markdown format, and it should be lengthy and detailed. 
## Core Responsibilities
Analyze the stock data provided and generate insights based on the following:
- **Company Overview**: Summarize the company's business model, market position, and competitive advantages.
- **Investment Recommendations**: Provide details analysis on given data and recommendation for stock to buy, sell or hold with given period.
## Output Format
Provide a structured output with the following fields:
- **company_overview**: A brief summary of the company's business and market position.
- **investment_recommendation**: A brief summary of the investment recommendation.
"""

async def investment_agent(stock_data, technical_analysis, fundamental_analysis, news_analysis):
    investment_analyser_agent = Agent(name="Investment Stock Analyser",
                                      instructions=INVESTMENT_INSTRUCTION,
                                      model="gpt-4o-mini")
    investment_message = f"""
        "Technical Analysis" : {technical_analysis},
        "Fundamental Analysis" : {fundamental_analysis},
        "News Analysis" : {news_analysis}
    """
    investment_input_items: list[TResponseInputItem] = [{"content": investment_message, "role": "user"}]
    return await Runner.run(investment_analyser_agent, investment_input_items)