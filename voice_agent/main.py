from realtime_client import RealtimeClient
from instructions import INSTRUCTIONS

import asyncio
import logging
from logger import logger
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = RealtimeClient(instructions=INSTRUCTIONS, voice="sage")
    try:
        await client.run()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
    finally:
        print("✅ Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
