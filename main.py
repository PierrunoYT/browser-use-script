from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
import os
from dotenv import load_dotenv
import signal
import sys

# Load environment variables
load_dotenv()

def signal_handler(sig, frame):
    print("\nGracefully shutting down...")
    sys.exit(0)

def get_task():
    try:
        return input("\nEnter your browser task (Ctrl+C to exit):\n> ").strip()
    except EOFError:
        return None

async def process_task(task: str):
    if not task:
        return
    
    try:
        # Initialize the agent with the user's task
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model="gpt-4"),
        )
        
        # Run the agent and get the result
        print("\nExecuting task...")
        result = await agent.run()
        print("\nResult:")
        print(result)
        print("\n" + "-"*50)
    except Exception as e:
        print(f"\nError executing task: {str(e)}")

async def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Welcome to Browser Use CLI!")
    print("Enter your tasks and watch the browser automation in action.")
    print("Press Ctrl+C to exit.")
    
    while True:
        task = get_task()
        if task is None:
            break
        if task.lower() in ['exit', 'quit']:
            break
        
        await process_task(task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
        sys.exit(0) 