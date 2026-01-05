from mcp.server.fastmcp import FastMCP
from database import read_account

mcp = FastMCP("accounts_server")

@mcp.tool()
async def get_balance(username: str) -> float:
    """Get the cash balance for the account."""
    acc = read_account(username)
    if acc is not None:
        return acc.__dict__["cash_balance"]
    else:
        raise ValueError(f"Account {username} not found")

@mcp.tool()
async def get_holdings(username: str) -> list:
    """Get the current holdings as a list of (symbol, quantity) tuples."""
    acc = read_account(username)
    if acc is not None:
        return acc.__dict__["holdings"]
    else:
        raise ValueError(f"Account {username} not found")

@mcp.tool()
async def buy_shares(username: str, symbol: str, quantity: int) -> None:
    """Buy shares of the given symbol."""
    acc = read_account(username)
    if acc is not None:
        acc.buy(symbol, quantity)
    else:
        raise ValueError(f"Account {username} not found")

@mcp.tool()
async def sell_shares(username: str, symbol: str, quantity: int) -> None:
    """Sell shares of the given symbol."""
    acc = read_account(username)
    if acc is not None:
        acc.sell(symbol, quantity)
    else:
        raise ValueError(f"Account {username} not found")
    

@mcp.tool()
async def change_strategy(username: str, strategy: str) -> str:
    """At your discretion, if you choose to, call this to change your investment strategy for the future.
   
    Args:
        username: The name of the account holder
        strategy: The new strategy for the account
    """
    acc = read_account(username)
    if acc is not None:
        acc.change_strategy(strategy)
    else:
        raise ValueError(f"Account {username} not found")
    return f"Strategy updated to '{strategy}'"

@mcp.resource("accounts://resources/{username}")
async def read_account_resource(username: str) -> str:
    acc = read_account(username)
    if acc is not None:
        return acc.report()
    else:
        raise ValueError(f"Account {username} not found")
    
@mcp.resource("accounts://strategy/{username}")
async def read_strategy_resource(username: str) -> str:
    acc = read_account(username)
    if acc is not None:
        return acc.get_strategy()
    else:
        raise ValueError(f"Account {username} not found")
    
if __name__ == "__main__":
    mcp.run(transport = 'stdio')