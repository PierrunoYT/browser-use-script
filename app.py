#!/usr/bin/env python3
import click
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BrowserUseCLI:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(model=model)
        
    async def execute_task(self, task: str) -> None:
        agent = Agent(
            task=task,
            llm=self.llm,
        )
        result = await agent.run()
        print(result)

@click.group()
def cli():
    """Browser Use CLI - Automate browser tasks with AI"""
    pass

@cli.command()
@click.argument('task', required=True)
@click.option('--model', '-m', default="gpt-4", help='OpenAI model to use')
@click.option('--api-key', '-k', help='OpenAI API key (optional if set in .env)')
def run(task: str, model: str, api_key: Optional[str]):
    """Execute a browser automation task"""
    browser_cli = BrowserUseCLI(model=model, api_key=api_key)
    asyncio.run(browser_cli.execute_task(task))

@cli.command()
@click.argument('url')
@click.argument('query')
@click.option('--model', '-m', default="gpt-4", help='OpenAI model to use')
@click.option('--api-key', '-k', help='OpenAI API key (optional if set in .env)')
def search(url: str, query: str, model: str, api_key: Optional[str]):
    """Search and extract information from a specific website"""
    task = f"Go to {url} and search for information about: {query}"
    browser_cli = BrowserUseCLI(model=model, api_key=api_key)
    asyncio.run(browser_cli.execute_task(task))

@cli.command()
@click.argument('from_location')
@click.argument('to_location')
@click.argument('date')
@click.option('--return-date', '-r', help='Return date for round trip')
@click.option('--model', '-m', default="gpt-4", help='OpenAI model to use')
@click.option('--api-key', '-k', help='OpenAI API key (optional if set in .env)')
def flights(from_location: str, to_location: str, date: str, 
           return_date: Optional[str], model: str, api_key: Optional[str]):
    """Search for flights using Google Flights"""
    task = f"Find {'a one-way' if not return_date else ''} flight from {from_location} to {to_location} on {date}"
    if return_date:
        task += f" with return on {return_date}"
    task += " on Google Flights. Return me the cheapest option."
    
    browser_cli = BrowserUseCLI(model=model, api_key=api_key)
    asyncio.run(browser_cli.execute_task(task))

if __name__ == "__main__":
    cli()