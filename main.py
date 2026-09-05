import asyncio

from mcp import Client


BINANCE_MCP_URL = "https://agent.binance.com/mcp/agentic"


def print_exception_tree(exc: BaseException, level: int = 0) -> None:
    """Print nested ExceptionGroup errors in a readable way."""
    prefix = "  " * level
    print(f"{prefix}- {type(exc).__name__}: {exc}")

    if isinstance(exc, BaseExceptionGroup):
        for child in exc.exceptions:
            print_exception_tree(child, level + 1)


async def main() -> None:
    print("Binance Sentinel v0.1.1")
    print("Connecting to Binance Agent OS MCP...")

    try:
        # The current MCP Python SDK accepts a remote MCP URL directly.
        async with Client(BINANCE_MCP_URL) as client:
            print("Connected successfully.\n")
            print("Discovering available Binance MCP tools...\n")

            result = await client.list_tools()

            if not result.tools:
                print("Connected, but no tools were returned.")
                return

            for index, tool in enumerate(result.tools, start=1):
                print(f"{index}. {tool.name}")

            print(f"\nTotal tools discovered: {len(result.tools)}")

    except BaseException as exc:
        print("\nConnection failed.")
        print("Detailed error:")
        print_exception_tree(exc)
        print(
            "\nIf the error mentions 401, 403, authorization, or OAuth, "
            "the MCP connection is reaching Binance and the next step is authentication."
        )


if __name__ == "__main__":
    asyncio.run(main())
