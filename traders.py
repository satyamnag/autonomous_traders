import json
import asyncio
from contextlib import AsyncExitStack

from agents import Agent, Tool, Runner, OpenAIChatCompletionsModel, trace
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents.mcp import MCPServerStdio

from accounts_client import read_accounts_resource, read_strategy_resource
from tracers import make_trace_id
from templates import (
    researcher_instructions,
    trader_instructions,
    trade_message,
    rebalance_message,
    research_tool,
)
from mcp_params import trader_mcp_server_params, researcher_mcp_server_params

load_dotenv(override = True)

MAX_TURNS = 10
openai_client = AsyncOpenAI()

async def get_researcher(mcp_servers) -> Agent:
    return Agent(
        name = "Researcher",
        instructions = researcher_instructions(),
        model = OpenAIChatCompletionsModel(
            model = "gpt-4o-mini",
            openai_client = openai_client,
        ),
        mcp_servers = mcp_servers,
    )

async def get_researcher_tool(mcp_servers) -> Tool:
    researcher = await get_researcher(mcp_servers)
    return researcher.as_tool(
        tool_name = "Researcher",
        tool_description = research_tool(),
    )

class Trader:
    def __init__(self, username: str, lastname="Trader", model_name="gpt-4o-mini"):
        self.username = username
        self.lastname = lastname
        self.agent = None
        self.model_name = model_name
        self.do_trade = True

    async def create_agent(self, trader_mcp_servers, researcher_mcp_servers) -> Agent:
        tool = await get_researcher_tool(researcher_mcp_servers)
        self.agent = Agent(
            name = self.username,
            instructions = trader_instructions(self.username),
            model = OpenAIChatCompletionsModel(
                model = self.model_name,
                openai_client = openai_client,
            ),
            tools = [tool],
            mcp_servers = trader_mcp_servers,
        )
        return self.agent

    async def get_account_report(self) -> str:
        account = await read_accounts_resource(self.username)
        try:
            account_json = json.loads(account)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid account JSON for trader '{self.username}': {account}"
            ) from e
        account_json.pop("portfolio_value_time_series", None)
        return json.dumps(account_json)

    async def _run_agent_inner(self, trader_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(trader_mcp_servers, researcher_mcp_servers)

        account = await self.get_account_report()
        strategy = await read_strategy_resource(self.username)

        message = (
            trade_message(self.username, strategy, account)
            if self.do_trade
            else rebalance_message(self.username, strategy, account)
        )

        await Runner.run(
            self.agent,
            message,
            max_turns=MAX_TURNS,
        )

    async def run_agent(self, trader_mcp_servers, researcher_mcp_servers):
        try:
            await asyncio.wait_for(
                self._run_agent_inner(trader_mcp_servers, researcher_mcp_servers),
                timeout=300,
            )
        except asyncio.TimeoutError:
            print(f"Agent {self.username} timed out after 5 minutes")
        except Exception as e:
            print(f"Error running agent {self.username}: {e}")
            raise

    async def run_with_mcp_servers(self):
        async with AsyncExitStack() as stack:
            trader_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds = 120)
                )
                for params in trader_mcp_server_params
            ]
            researcher_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds = 120)
                )
                for params in researcher_mcp_server_params(self.username)
            ]
            await self.run_agent(trader_mcp_servers, researcher_mcp_servers)

    async def run_with_trace(self):
        trace_username = (
            f"{self.username}-trading"
            if self.do_trade
            else f"{self.username}-rebalancing"
        )
        trace_id = make_trace_id(self.username.lower())
        with trace(trace_username, trace_id = trace_id):
            await self.run_with_mcp_servers()

    async def run(self):
        try:
            await self.run_with_trace()
            self.do_trade = not self.do_trade
        except Exception as e:
            print(f"Error running trader {self.username}: {e}")