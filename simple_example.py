"""
Simple Browser Use Example

This demonstrates the basic usage of browser-use with the modern API.
Based on the official browser-use quickstart guide.
"""

import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent

# Load environment variables
load_dotenv()


async def main():
    """Simple example of browser automation"""
    
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o")
    
    # Create and run the agent
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm,
    )
    
    result = await agent.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
