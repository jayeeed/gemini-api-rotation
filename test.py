import asyncio
from gemini_rotate import GeminiRotationClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = GeminiRotationClient()

    response = await client.generate_content("Hola!")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())