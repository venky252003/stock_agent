import gradio as gr
from dotenv import load_dotenv
from agent.stock_manager_agent import SupervisorManager

load_dotenv(override=True)


async def run(query: str):
    async for chunk in SupervisorManager().run(query):
        yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# AI Agent Stock Analysist ")
    query_textbox = gr.Textbox(label="Analysis Apple stock")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    
    run_button.click(fn=run, inputs=query_textbox, outputs=report)
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

#ui.launch(inbrowser=True)
ui.launch(
    inbrowser=True,
    auth=[("venky", "Venky25")],  # or auth=[("user1", "pass1"), ("user2", "pass2")]
    auth_message="Please log in to use the stock analysis tool"
)
