import os
from dotenv import load_dotenv

load_dotenv(override = True)

PATH_TO_INDEX_DOT_JS = os.getenv("PATH_TO_INDEX_DOT_JS")

massive_api_key = os.getenv("MASSIVE_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
coincap_api_key = os.getenv("COINCAP_API_KEY")

market_mcp_server_params = {
    "command": "uv",
    "args": ["run", "market_server.py"],
}

yahoo_finance_mcp_params = {
            "command": "uvx",
            "args": ["mcp-yahoo-finance"],
        }

coincap_mcp_params = {
    "command": "npx",
    "args": ["-y", "mcp-crypto-price"],
    "env": {
        "COINCAP_API_KEY": coincap_api_key
    }
}

trader_mcp_server_params = [
    {"command": "uv", "args": ["run", "accounts_server.py"]},
    {"command": "uv", "args": ["run", "push_server.py"]},
    market_mcp_server_params,
    yahoo_finance_mcp_params,
    coincap_mcp_params
]

def researcher_mcp_server_params(name: str):
    return [
        yahoo_finance_mcp_params,
        coincap_mcp_params,
        {
            "command": "uvx",
            "args": ["mcp-server-fetch"],
        },
        {
            "command": "node",
            "args": [
                PATH_TO_INDEX_DOT_JS
            ],
            "env": {
                "GOOGLE_API_KEY": google_api_key,
                "GOOGLE_SEARCH_ENGINE_ID": google_search_engine_id,
            },
        },
        {
            "command": "npx",
            "args": ["-y", "--silent", "mcp-memory-libsql"],
            "env": {"LIBSQL_URL": f"file:./memory/{name}.db"},
        },
    ]