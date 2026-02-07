import asyncio
import logging
from gemini_rotate import GeminiRotationClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

async def main():
    try:
        client = GeminiRotationClient()
        
        response = await client.generate_content(
            contents="Hi!"
        )

        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
