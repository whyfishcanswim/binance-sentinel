import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


BINANCE_MCP_URL = "https://agent.binance.com/mcp/agentic"


async def main() -> None:
    print("Binance Sentinel v0.1")
    print("Connecting to Binance Agent OS MCP...")

    try:
        async with streamable_http_client(BINANCE_MCP_URL) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                print("Connected successfully.\n")
                print("Discovering available Binance MCP tools...\n")

                result = await session.list_tools()

                if not result.tools:
                    print("Connected, but no tools were returned.")
                    return

                for index, tool in enumerate(result.tools, start=1):
                    print(f"{index}. {tool.name}")

                print(f"\nTotal tools discovered: {len(result.tools)}")

    except Exception as exc:
        print("\nConnection failed.")
        print(f"Error type: {type(exc).__name__}")
        print(f"Details: {exc}")
        print(
            "\nThis is our first diagnostic step. "
            "If Binance requests authorization or returns another connection error, "
            "we will handle that in the next version."
        )


if __name__ == "__main__":
    asyncio.run(main())
