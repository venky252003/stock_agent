import asyncio
from types import SimpleNamespace
import app.agent.fundamental_agent as fa
import app.agent.technical_agent as ta
import app.agent.investment_agent as ia
import app.agent.news_agent as na
import app.agent.stock_manager_agent as sm


def test_fundamental_agent(monkeypatch):
    async def dummy_run(agent, items):
        return 'ok'
    monkeypatch.setattr(fa.Runner, 'run', dummy_run)
    result = SimpleNamespace(final_output=SimpleNamespace(fundamental_data={}))
    assert asyncio.run(fa.fundamental_agent(result)) == 'ok'


def test_technical_agent(monkeypatch):
    async def dummy_run(agent, items):
        return 'ok'
    monkeypatch.setattr(ta.Runner, 'run', dummy_run)
    result = SimpleNamespace(final_output=SimpleNamespace(technical_data={}))
    assert asyncio.run(ta.technical_agent(result)) == 'ok'


def test_news_agent(monkeypatch):
    async def dummy_run(agent, items):
        return 'ok'
    monkeypatch.setattr(na.Runner, 'run', dummy_run)
    result = SimpleNamespace(final_output=SimpleNamespace(news=[]))
    assert asyncio.run(na.news_agent(result)) == 'ok'


def test_investment_agent(monkeypatch):
    async def dummy_run(agent, items):
        return 'ok'
    monkeypatch.setattr(ia.Runner, 'run', dummy_run)
    out = asyncio.run(ia.investment_agent({}, {}, {}, {}))
    assert out == 'ok'


def test_supervisor_final_report(monkeypatch):
    manager = sm.SupervisorManager()
    manager.table_report = SimpleNamespace(final_output='table')
    manager.technical_result = SimpleNamespace(final_output='tech')
    manager.fundamental_result = SimpleNamespace(final_output='fund')
    manager.news_result = SimpleNamespace(final_output='news')
    manager.investment_result = SimpleNamespace(final_output='inv')

    monkeypatch.setattr(sm, 'AgentOutputSchema', SimpleNamespace)
    result = asyncio.run(manager.final_report())
    assert result == 'table\n\ntech\n\nfund\n\nnews\n\ninv\n\n'
