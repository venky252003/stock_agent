from agents import Agent, Runner, trace, gen_trace_id, TResponseInputItem, AgentOutputSchema
from agent.technical_agent import technical_agent
from agent.fundamental_agent import fundamental_agent
from agent.investment_agent import investment_agent
from agent.news_agent import news_agent
from agent.stock_query_agent import query_agent

REPORT_INSTRUCTION = """
            You need create tabular report based on the stock data of technical, fundamental, trend signal and stock news.
            output of this report should be in markdown format.
            The report should include the following sections:
        1. **Basic Information**: Company name, stock symbol, exchange, and sector.
        2. **Technical Data**: all technical data.
        3. **Fundamental Data**: all fundamental data.
        4. **Trend Signals**: all trend signal.
        5. **News Summary**: all news articles with titles and summaries.
        """

class SupervisorManager:
    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        if not query or len(query) == 0:
            raise ValueError("Query cannot be empty. Please provide a valid stock query.")
        
        trace_id = gen_trace_id()
        with trace("Stock Analysis trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting extracting stock data...")
            self.stock_data = await query_agent(query)
            yield "Technical analysis started ...."     
            self.technical_result = await technical_agent(self.stock_data)
            yield "Fundamental analysis started ..."
            self.fundamental_result = await fundamental_agent(self.stock_data)
            self.news_result = ""
            if self.stock_data.final_output.news is not None and len(self.stock_data.final_output.news) > 0:
                yield "News analysis started ..."
                self.news_result = await news_agent(self.stock_data)
            
            yield "Investment Recommendation started ..."
            self.investment_result = await investment_agent(self.stock_data, self.technical_result , self.fundamental_result, self.news_result)
            yield "Report Prepration..."
            self.table_report = await self.data_report(query)
            yield "Report Prepared..."
            report = await self.final_report()
            #yield "Email sent, research complete"
            yield report

    async def final_report(self):
        result = ""
        if self.table_report is not None:
            result += self.table_report.final_output + "\n\n"

        if self.technical_result is not None:
            result += self.technical_result.final_output + "\n\n"

        if self.fundamental_result is not None:
            result += self.fundamental_result.final_output + "\n\n"

        if isinstance(self.news_result, AgentOutputSchema):
            result += self.news_result.final_output + "\n\n"

        if self.investment_result is not None:
            result += self.investment_result.final_output + "\n\n"

        return result



    async def data_report(self, query: str):
        """ Query the stock data for the query """
        print("Querying stock data...")       

        report_agent = Agent(
            name="StockReportAgent",
            instructions=REPORT_INSTRUCTION,
            model="gpt-4o-mini"
        )

        message = f"""
            "Company Name": {self.stock_data.final_output.company_name},
            "Company Details" : {self.stock_data.final_output.basic_info},
            "Technical Details" : {self.stock_data.final_output.technical_data},
            "Fundamental Details" : {self.stock_data.final_output.fundamental_data},
            "News Details" : {self.stock_data.final_output.news}
        """

        data_input_items: list[TResponseInputItem] = [{"content": message, "role": "user"}]

        return await Runner.run(report_agent, data_input_items)
        
    
    
    
    
        
    