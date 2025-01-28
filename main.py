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
        
        # Save result to JSON file with proper encoding
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/results/search_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(params.dict(), f, indent=2, ensure_ascii=False)
            
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
    
    @controller.action('Extract content from page', requires_browser=True)
    async def extract_content(browser: Browser):
        page = browser.get_current_page()
        content = await page.content()
        
        # Create content directory if it doesn't exist
        os.makedirs("logs/content", exist_ok=True)
        
        # Save content to file with proper encoding
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/content/page_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Saved page content to {filename}"
    
    @controller.action('Extract table data', requires_browser=True)
    async def extract_table(selector: str, browser: Browser):
        page = browser.get_current_page()
        table = await page.query_selector(selector)
        if not table:
            return "Table not found"
        
        # Extract table data
        data = await table.evaluate('''table => {
            const rows = Array.from(table.querySelectorAll('tr'));
            return rows.map(row => {
                const cells = Array.from(row.querySelectorAll('td, th'));
                return cells.map(cell => cell.textContent.trim());
            });
        }''')
        
        # Save to CSV
        os.makedirs("logs/tables", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/tables/table_{timestamp}.csv"
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        return f"Saved table data to {filename}"

    @controller.action('Download file', requires_browser=True)
    async def download_file(url: str, browser: Browser):
        page = browser.get_current_page()
        
        # Create downloads directory
        os.makedirs("logs/downloads", exist_ok=True)
        
        # Configure download behavior
        download = await page.expect_download(timeout=30000)
        await page.goto(url)
        
        # Wait for download to complete
        download_path = await download.path()
        if not download_path:
            return "Download failed"
            
        # Move to downloads directory
        filename = os.path.basename(download_path)
        target_path = os.path.join("logs/downloads", filename)
        os.rename(download_path, target_path)
        
        return f"Downloaded file to {target_path}"

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

class ResearchPrompt(SystemPrompt):
    def important_rules(self) -> str:
        existing_rules = super().important_rules()
        
        research_rules = """
9. RESEARCH RULES:
   - SYSTEMATICALLY explore topics in depth
   - VERIFY information from multiple sources
   - DOCUMENT all findings with proper citations
   - ORGANIZE research data hierarchically
   - SUMMARIZE key findings clearly
"""
        return f'{existing_rules}\n{research_rules}'

def get_system_prompt(prompt_type: str = None):
    """Get the appropriate system prompt based on configuration"""
    prompt_type = prompt_type or os.getenv("SYSTEM_PROMPT", "default")
    
    if prompt_type.lower() == "safety":
        return SafetyFirstPrompt
    elif prompt_type.lower() == "collection":
        return DataCollectionPrompt
    elif prompt_type.lower() == "research":
        return ResearchPrompt
    else:
        return SystemPrompt  # Default prompt

async def process_task(task: str, browser: Browser = None):
    if not task:
        return
    
    try:
        # Configure system encoding for Windows
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        
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
        if history.final_result():
            print("\nResult:", history.final_result())
        
        if history.has_errors():
            print("\nWarnings/Errors during execution:")
            for error in history.errors():
                print(f"- {error}")
        
        if history.urls():
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
        headless=False,  # Set to True for headless mode
        slow_mo=50,  # Add delay between actions for visibility
        viewport={'width': 1280, 'height': 800},
        context_config=BrowserContextConfig(
            ignore_https_errors=True,
            java_script_enabled=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    )
    
    # Create directories for recordings and traces
    os.makedirs("logs/recordings", exist_ok=True)
    os.makedirs("logs/traces", exist_ok=True)
    
    try:
        # Initialize browser
        async with Browser(config=browser_config) as browser:
            while True:
                task = get_task()
                if task is None or task.lower() in ['exit', 'quit']:
                    break
                
                try:
                    history = await process_task(task, browser)
                    if not history:
                        continue
                    
                    # Save conversation history
                    if history.save_conversation_path:
                        print(f"\nConversation saved to: {history.save_conversation_path}")
                    
                except Exception as e:
                    print(f"\nError: {str(e)}")
                    continue
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