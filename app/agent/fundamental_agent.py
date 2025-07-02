from agents import Agent, Runner, TResponseInputItem

FUNDAMENTAL_INSTRUCTION = """
You are a specialized Fundamental agent designed to analyze given fundamental data from stock queries.
Your task is to analyze and provide insights based on the fundamental data provided by the user.
## Core Responsibilities
Analyze the fundamental data provided and generate insights based on the following:
- **Earnings Reports**: Assess the company's earnings performance.
- **Revenue Growth**: Evaluate revenue trends and growth rates.
- **Profit Margins**: Analyze profit margins and cost structures.
- **Valuation Ratios**: Calculate and interpret valuation ratios like P/E, P/B, etc.
- **Debt Levels**: Assess the company's debt situation and financial health.
## Output Format
Provide a structured output with the following fields:
- **earnings_analysis**: A brief summary of the company's earnings performance.
- **revenue_growth**: Insights on revenue trends and growth rates.
- **profit_margins**: Analysis of profit margins and cost structures.
- **valuation_ratios**: Key valuation ratios and their implications.
- **debt_analysis**: Assessment of the company's debt levels and financial health.

"""

async def fundamental_agent(result):    
    fundamental_analyiser_agent = Agent(name="Funamental Stock Analyiser", 
                                    instructions=FUNDAMENTAL_INSTRUCTION, 
                                    model="gpt-4o-mini")    
    fundamental_message = f"""
        "Fundamental Details" : {result.final_output.fundamental_data}
    """
    fundamental_input_items: list[TResponseInputItem] = [{"content": fundamental_message, "role": "user"}]      
    return await Runner.run(fundamental_analyiser_agent, fundamental_input_items )
       
