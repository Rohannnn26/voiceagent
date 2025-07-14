from realtime_client_new import RealtimeClient
from instructions import INSTRUCTIONS

import asyncio
import logging
from logger import logger
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = RealtimeClient(instructions=INSTRUCTIONS, voice="ash")
    try:
        await client.run()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
    finally:
        print("✅ Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
