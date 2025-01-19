from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, SystemPrompt
from browser_use.browser.context import BrowserContextConfig
import asyncio
import os
from dotenv import load_dotenv
import signal
import sys
import json
from datetime import datetime
from browser_use.controller.service import Controller
from pydantic import BaseModel, SecretStr
from typing import Optional, List
from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI

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

# Add custom function models
class SearchResult(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    timestamp: Optional[str] = None

class SavedContent(BaseModel):
    content: str
    source_url: str
    saved_at: str

# Define supported LLM providers
class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"

def get_llm_model(provider: str = None):
    """Initialize and return the specified LLM model"""
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    try:
        provider = LLMProvider(provider)
    except ValueError:
        print(f"Warning: Unsupported provider '{provider}'. Falling back to OpenAI.")
        provider = LLMProvider.OPENAI
    
    model_name = None
    
    if provider == LLMProvider.OPENAI:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(
            model=model_name,
            temperature=0.0
        )
    
    elif provider == LLMProvider.ANTHROPIC:
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        return ChatAnthropic(
            model_name=model_name,
            temperature=0.0,
            timeout=100  # Increased timeout for complex tasks
        )
    
    elif provider == LLMProvider.AZURE:
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_KEY')
        model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
        
        if not endpoint or not api_key:
            print("Warning: Azure OpenAI credentials not found. Falling back to OpenAI.")
            return get_llm_model(LLMProvider.OPENAI)
        
        return AzureChatOpenAI(
            model=model_name,
            api_version='2024-10-21',
            azure_endpoint=endpoint,
            api_key=SecretStr(api_key)
        )

def create_custom_controller():
    controller = Controller()
    
    @controller.action('Ask user for confirmation', requires_browser=False)
    def confirm_action(message: str) -> bool:
        response = input(f"\n{message} (y/n): ").lower().strip()
        return response.startswith('y')
    
    @controller.action('Save search results', param_model=SearchResult)
    async def save_search_result(params: SearchResult):
        # Create results directory if it doesn't exist
        os.makedirs("logs/results", exist_ok=True)
        
        # Save result to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/results/search_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(params.dict(), f, indent=2)
            
        return f"Saved search result to {filename}"
    
    @controller.action('Take screenshot of element', requires_browser=True)
    async def screenshot_element(selector: str, browser: Browser):
        page = browser.get_current_page()
        element = await page.wait_for_selector(selector)
        
        # Create screenshots directory
        os.makedirs("logs/screenshots", exist_ok=True)
        
        # Save screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/screenshots/element_{timestamp}.png"
        await element.screenshot(path=filename)
        
        return f"Saved element screenshot to {filename}"
    
    return controller

# Add custom system prompts
class SafetyFirstPrompt(SystemPrompt):
    def important_rules(self) -> str:
        existing_rules = super().important_rules()
        
        safety_rules = """
9. SAFETY AND PRIVACY RULES:
   - NEVER submit sensitive information without user confirmation
   - ALWAYS ask for confirmation before form submissions
   - AVOID clicking on suspicious or untrusted links
   - RESPECT website terms of service and robots.txt
   - DO NOT automate login processes without explicit user permission
"""
        return f'{existing_rules}\n{safety_rules}'

class DataCollectionPrompt(SystemPrompt):
    def important_rules(self) -> str:
        existing_rules = super().important_rules()
        
        collection_rules = """
9. DATA COLLECTION RULES:
   - ALWAYS save important search results
   - TAKE screenshots of relevant content
   - DOCUMENT all visited URLs
   - EXTRACT and save useful information
   - ORGANIZE collected data with clear timestamps
"""
        return f'{existing_rules}\n{collection_rules}'

def get_system_prompt(prompt_type: str = None):
    """Get the appropriate system prompt based on configuration"""
    prompt_type = prompt_type or os.getenv("SYSTEM_PROMPT", "default")
    
    if prompt_type.lower() == "safety":
        return SafetyFirstPrompt
    elif prompt_type.lower() == "collection":
        return DataCollectionPrompt
    else:
        return SystemPrompt  # Default prompt

async def process_task(task: str, browser: Browser = None):
    if not task:
        return
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Generate timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/conversation_{timestamp}.json"
        
        # Create custom controller with additional functions
        controller = create_custom_controller()
        
        # Initialize the LLM model based on configuration
        llm = get_llm_model()
        
        # Get appropriate system prompt
        system_prompt_class = get_system_prompt()
        
        # Initialize the agent with enhanced configuration
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            controller=controller,
            use_vision=False,  # Disable vision for now as it's causing issues
            save_conversation_path=log_file,
            system_prompt_class=system_prompt_class
        )
        
        # Run the agent and get the result
        print("\nExecuting task...")
        history = await agent.run(max_steps=50)  # Limit maximum steps
        
        # Process and display results
        print("\nResult:", history.final_result())
        
        if history.has_errors():
            print("\nWarnings/Errors during execution:")
            for error in history.errors():
                print(f"- {error}")
        
        print("\nVisited URLs:", ", ".join(history.urls()))
        print("\n" + "-"*50)
        
        return history
    except Exception as e:
        print(f"\nError executing task: {str(e)}")
        return None

async def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Welcome to Browser Use CLI!")
    print(f"Using LLM Provider: {os.getenv('LLM_PROVIDER', 'openai').upper()}")
    print(f"System Prompt: {os.getenv('SYSTEM_PROMPT', 'default').upper()}")
    print("Enter your tasks and watch the browser automation in action.")
    print("Press Ctrl+C to exit.")
    
    # Configure browser settings
    browser_config = BrowserConfig(
        headless=False,  # Show browser UI
        disable_security=True,  # Disable security for better compatibility
        new_context_config=BrowserContextConfig(
            wait_for_network_idle_page_load_time=3.0,
            browser_window_size={'width': 1280, 'height': 1100},
            save_recording_path="logs/recordings",
            trace_path="logs/traces"
        )
    )
    
    # Create directories for recordings and traces
    os.makedirs("logs/recordings", exist_ok=True)
    os.makedirs("logs/traces", exist_ok=True)
    
    try:
        # Initialize browser
        browser = Browser(config=browser_config)
        
        while True:
            task = get_task()
            if task is None or task.lower() in ['exit', 'quit']:
                break
            
            await process_task(task, browser)
            
    finally:
        # Ensure browser is closed properly
        if 'browser' in locals():
            await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
        sys.exit(0) 