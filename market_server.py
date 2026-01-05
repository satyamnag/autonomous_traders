from mcp.server.fastmcp import FastMCP

from market import get_share_price

mcp = FastMCP("market_server")

@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    """This tool provides the stock price (EOD if market is closed) of the given stock symbol.

    Args:
        symbol: the symbol of the stock
    """
    try:
        return get_share_price(symbol)
    except Exception as e:
        raise ValueError(f"Price lookup failed for {symbol}: {str(e)}")

if __name__ == "__main__":
    mcp.run(transport = 'stdio')