from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, SystemPrompt
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from browser_use.history import AgentHistoryList
import asyncio
import os
from dotenv import load_dotenv
import signal
import sys
import json
from datetime import datetime
from browser_use.controller.service import Controller
from pydantic import BaseModel, SecretStr
from typing import Optional, List, Dict, Any, Union, Type
from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/browser_use.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    logger.info("Gracefully shutting down...")
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
    metadata: Optional[Dict[str, Any]] = None

class SavedContent(BaseModel):
    content: str
    source_url: str
    saved_at: str
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Define supported LLM providers
class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    DEEPSEEK_R1 = "deepseek_r1"
    OLLAMA = "ollama"

def get_llm_model(provider: str = None):
    """Initialize and return the specified LLM model"""
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    try:
        provider = LLMProvider(provider)
    except ValueError:
        logger.warning(f"Unsupported provider '{provider}'. Falling back to OpenAI.")
        provider = LLMProvider.OPENAI
    
    model_name = None
    
    if provider == LLMProvider.OPENAI:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        return ChatOpenAI(
            model=model_name,
            temperature=0.0,
            api_key=api_key
        )
    
    elif provider == LLMProvider.ANTHROPIC:
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        return ChatAnthropic(
            model_name=model_name,
            temperature=0.0,
            timeout=100,
            api_key=api_key
        )
    
    elif provider == LLMProvider.AZURE:
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_KEY')
        model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
        
        if not endpoint or not api_key:
            logger.warning("Azure OpenAI credentials not found. Falling back to OpenAI.")
            return get_llm_model(LLMProvider.OPENAI)
        
        return AzureChatOpenAI(
            model=model_name,
            api_version='2024-02-29',
            azure_endpoint=endpoint,
            api_key=SecretStr(api_key)
        )

    elif provider == LLMProvider.GEMINI:
        raise NotImplementedError("Gemini support coming soon")
        
    elif provider == LLMProvider.DEEPSEEK:
        raise NotImplementedError("DeepSeek-V3 support coming soon")
        
    elif provider == LLMProvider.DEEPSEEK_R1:
        raise NotImplementedError("DeepSeek-R1 support coming soon")
        
    elif provider == LLMProvider.OLLAMA:
        raise NotImplementedError("Ollama support coming soon")

# Add example output models
class Post(BaseModel):
    post_title: str
    post_url: str
    num_comments: int
    hours_since_post: int

class Posts(BaseModel):
    posts: List[Post]

def create_custom_controller(
    output_model: Optional[Type[BaseModel]] = None,
    excluded_actions: Optional[List[str]] = None
) -> Controller:
    """Create a custom controller with additional functions and optional output model
    
    Args:
        output_model: Optional Pydantic model for structured output
        excluded_actions: List of action names to exclude from the controller
    """
    # Get excluded actions from environment or parameter
    excluded = excluded_actions or json.loads(os.getenv('EXCLUDED_ACTIONS', '[]'))
    
    # Initialize controller with output model
    controller = Controller(output_model=output_model)
    
    # Define all available actions
    AVAILABLE_ACTIONS = {
        'confirm': {
            'func': confirm_action,
            'name': 'Ask user for confirmation',
            'requires_browser': False
        },
        'save_search': {
            'func': save_search_result,
            'name': 'Save search results',
            'param_model': SearchResult,
            'requires_browser': False
        },
        'screenshot': {
            'func': screenshot_element,
            'name': 'Take screenshot of element',
            'requires_browser': True
        },
        'extract_content': {
            'func': extract_content,
            'name': 'Extract content from page',
            'requires_browser': True
        },
        'extract_table': {
            'func': extract_table,
            'name': 'Extract table data',
            'requires_browser': True
        },
        'download': {
            'func': download_file,
            'name': 'Download file',
            'requires_browser': True
        }
    }
    
    # Register non-excluded actions
    for action_id, config in AVAILABLE_ACTIONS.items():
        if action_id not in excluded:
            if config.get('param_model'):
                @controller.action(
                    config['name'], 
                    requires_browser=config['requires_browser'],
                    param_model=config['param_model']
                )
                async def wrapper(*args, **kwargs):
                    return await config['func'](*args, **kwargs)
            else:
                @controller.action(
                    config['name'], 
                    requires_browser=config['requires_browser']
                )
                async def wrapper(*args, **kwargs):
                    return await config['func'](*args, **kwargs) if asyncio.iscoroutinefunction(config['func']) else config['func'](*args, **kwargs)
    
    return controller

# Define individual action functions outside the controller creation
async def confirm_action(message: str) -> bool:
    response = input(f"\n{message} (y/n): ").lower().strip()
    return response.startswith('y')

async def save_search_result(params: SearchResult):
    # Create results directory if it doesn't exist
    os.makedirs("logs/results", exist_ok=True)
    
    # Add timestamp if not provided
    if not params.timestamp:
        params.timestamp = datetime.now().isoformat()
    
    # Save result to JSON file with proper encoding
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/results/search_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(params.dict(), f, indent=2, ensure_ascii=False)
        
    logger.info(f"Saved search result to {filename}")
    return f"Saved search result to {filename}"

async def screenshot_element(selector: str, browser: Browser):
    page = browser.get_current_page()
    try:
        element = await page.wait_for_selector(selector, timeout=5000)
        if not element:
            return "Element not found"
        
        # Create screenshots directory
        os.makedirs("logs/screenshots", exist_ok=True)
        
        # Save screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/screenshots/element_{timestamp}.png"
        await element.screenshot(path=filename)
        
        logger.info(f"Saved element screenshot to {filename}")
        return f"Saved element screenshot to {filename}"
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return f"Failed to take screenshot: {str(e)}"

async def extract_content(browser: Browser):
    page = browser.get_current_page()
    try:
        content = await page.content()
        
        # Create content directory if it doesn't exist
        os.makedirs("logs/content", exist_ok=True)
        
        # Save content to file with proper encoding
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/content/page_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Saved page content to {filename}")
        return f"Saved page content to {filename}"
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}")
        return f"Failed to extract content: {str(e)}"

async def extract_table(selector: str, browser: Browser):
    page = browser.get_current_page()
    try:
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
        
        logger.info(f"Saved table data to {filename}")
        return f"Saved table data to {filename}"
    except Exception as e:
        logger.error(f"Error extracting table: {str(e)}")
        return f"Failed to extract table: {str(e)}"

async def download_file(url: str, browser: Browser):
    page = browser.get_current_page()
    try:
        # Create downloads directory
        os.makedirs("logs/downloads", exist_ok=True)
        
        # Configure download behavior
        download = await page.expect_download(timeout=int(os.getenv('DOWNLOAD_TIMEOUT', '30000')))
        await page.goto(url)
        
        # Wait for download to complete
        download_path = await download.path()
        if not download_path:
            return "Download failed"
            
        # Move to downloads directory
        filename = os.path.basename(download_path)
        target_path = os.path.join("logs/downloads", filename)
        os.rename(download_path, target_path)
        
        logger.info(f"Downloaded file to {target_path}")
        return f"Downloaded file to {target_path}"
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return f"Failed to download file: {str(e)}"

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
   - VALIDATE all URLs before navigation
   - SCAN for security certificates on HTTPS connections
   - REPORT any security concerns immediately
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
   - VALIDATE data before saving
   - MAINTAIN proper data structure
   - USE appropriate output formats
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
   - EVALUATE source credibility
   - TRACK research progress
   - MAINTAIN research context
"""
        return f'{existing_rules}\n{research_rules}'

# Add a new custom prompt for demonstration
class WikiFirstPrompt(SystemPrompt):
    def important_rules(self) -> str:
        existing_rules = super().important_rules()
        
        wiki_rules = """
9. WIKIPEDIA FIRST RULES:
   - ALWAYS open Wikipedia as the first step
   - VERIFY information from Wikipedia first
   - CITE Wikipedia articles properly
   - USE Wikipedia for initial context
   - FOLLOW Wikipedia links for depth
"""
        return f'{existing_rules}\n{wiki_rules}'

def get_system_prompt(prompt_type: str = None):
    """Get the appropriate system prompt based on configuration"""
    prompt_type = prompt_type or os.getenv("SYSTEM_PROMPT", "default").lower()
    
    PROMPT_CLASSES = {
        "safety": SafetyFirstPrompt,
        "collection": DataCollectionPrompt,
        "research": ResearchPrompt,
        "wiki": WikiFirstPrompt,
        "default": SystemPrompt
    }
    
    prompt_class = PROMPT_CLASSES.get(prompt_type)
    if not prompt_class:
        logger.warning(f"Unknown prompt type '{prompt_type}'. Using default.")
        prompt_class = SystemPrompt
    
    return prompt_class

def get_browser_config() -> BrowserConfig:
    """Get browser configuration from environment variables"""
    # Ensure logs directories exist
    for path in ["logs/recordings", "logs/traces"]:
        Path(path).mkdir(parents=True, exist_ok=True)
        
    return BrowserConfig(
        # Core Settings
        headless=os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true',
        disable_security=os.getenv('BROWSER_DISABLE_SECURITY', 'true').lower() == 'true',
        
        # Additional Settings
        extra_chromium_args=json.loads(os.getenv('BROWSER_EXTRA_ARGS', '[]')),
        slow_mo=int(os.getenv('BROWSER_SLOW_MO', '50')),
        
        # Alternative Initialization
        wss_url=os.getenv('BROWSER_WSS_URL'),
        cdp_url=os.getenv('BROWSER_CDP_URL'),
        chrome_instance_path=os.getenv('CHROME_INSTANCE_PATH'),
        
        # Context Configuration
        context_config=BrowserContextConfig(
            # Page Load Settings
            minimum_wait_page_load_time=float(os.getenv('MIN_PAGE_LOAD_TIME', '0.5')),
            wait_for_network_idle_page_load_time=float(os.getenv('NETWORK_IDLE_TIME', '1.0')),
            maximum_wait_page_load_time=float(os.getenv('MAX_PAGE_LOAD_TIME', '5.0')),
            
            # Display Settings
            viewport={
                'width': int(os.getenv('BROWSER_VIEWPORT_WIDTH', '1280')),
                'height': int(os.getenv('BROWSER_VIEWPORT_HEIGHT', '1100'))
            },
            locale=os.getenv('BROWSER_LOCALE'),
            highlight_elements=os.getenv('HIGHLIGHT_ELEMENTS', 'true').lower() == 'true',
            viewport_expansion=int(os.getenv('VIEWPORT_EXPANSION', '500')),
            
            # Security Settings
            ignore_https_errors=os.getenv('IGNORE_HTTPS_ERRORS', 'true').lower() == 'true',
            java_script_enabled=os.getenv('JAVASCRIPT_ENABLED', 'true').lower() == 'true',
            user_agent=os.getenv('BROWSER_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            
            # URL Restrictions
            allowed_domains=json.loads(os.getenv('ALLOWED_DOMAINS', 'null')),
            
            # Proxy Settings
            proxy={
                'server': os.getenv('HTTP_PROXY'),
                'username': os.getenv('PROXY_USERNAME'),
                'password': os.getenv('PROXY_PASSWORD')
            } if os.getenv('HTTP_PROXY') else None,
            
            # Timeouts
            navigation_timeout=int(os.getenv('NAVIGATION_TIMEOUT', '30000')),
            page_load_timeout=int(os.getenv('PAGE_LOAD_TIME', '30000')),
            
            # Debug and Recording
            save_recording_path=os.getenv('SAVE_RECORDING_PATH'),
            trace_path=os.getenv('TRACE_PATH')
        )
    )

async def process_task(
    task: str, 
    browser: Browser = None, 
    initial_actions: Optional[List[Dict[str, Any]]] = None,
    output_model: Optional[Type[BaseModel]] = None,
    excluded_actions: Optional[List[str]] = None
):
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
        
        # Create custom controller with output model and excluded actions
        controller = create_custom_controller(
            output_model=output_model,
            excluded_actions=excluded_actions
        )
        
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
            use_vision=os.getenv('USE_VISION', 'true').lower() == 'true',
            save_conversation_path=log_file,
            system_prompt_class=system_prompt_class,
            initial_actions=initial_actions
        )
        
        # Run the agent with configurable max_steps
        logger.info("Executing task...")
        history: AgentHistoryList = await agent.run(
            max_steps=int(os.getenv('MAX_STEPS', '100'))
        )
        
        # Enhanced result processing using AgentHistoryList methods
        if history.is_done():
            result = history.final_result()
            if result:
                # Try to parse result as output model if specified
                if output_model and isinstance(result, str):
                    try:
                        parsed_result = output_model.model_validate_json(result)
                        logger.info(f"Parsed result: {parsed_result.model_dump_json(indent=2)}")
                        print("\nParsed result:", parsed_result.model_dump_json(indent=2))
                    except Exception as e:
                        logger.error(f"Failed to parse result as {output_model.__name__}: {e}")
                        logger.info(f"Raw result: {result}")
                        print("\nResult:", result)
                else:
                    logger.info(f"Result: {result}")
                    print("\nResult:", result)
            
            # Add model thoughts logging if debug enabled
            if LOG_LEVEL == 'DEBUG':
                thoughts = history.model_thoughts()
                logger.debug("Model thoughts:")
                for thought in thoughts:
                    logger.debug(f"- {thought}")
        
        if history.has_errors():
            logger.warning("Warnings/Errors during execution:")
            print("\nWarnings/Errors during execution:")
            for error in history.errors():
                logger.warning(f"- {error}")
        
        # Add action results logging if debug enabled
        if LOG_LEVEL == 'DEBUG':
            action_results = history.action_results()
            logger.debug("Action results:")
            for result in action_results:
                logger.debug(f"- {result}")
        
        if history.urls():
            visited_urls = ", ".join(history.urls())
            logger.info(f"Visited URLs: {visited_urls}")
            print("\nVisited URLs:", visited_urls)
        
        return history
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        print(f"\nError executing task: {str(e)}")
        return None

async def main():
    # Create necessary directories
    for dir_path in ["logs", "logs/results", "logs/screenshots", "logs/content", 
                    "logs/tables", "logs/downloads", "logs/recordings", "logs/traces"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting Browser Use CLI")
    print("Welcome to Browser Use CLI!")
    print(f"Using LLM Provider: {os.getenv('LLM_PROVIDER', 'openai').upper()}")
    print(f"System Prompt: {os.getenv('SYSTEM_PROMPT', 'default').upper()}")
    print("Enter your tasks and watch the browser automation in action.")
    print("Press Ctrl+C to exit.")
    
    # Get browser configuration
    browser_config = get_browser_config()
    browser_context: Optional[BrowserContext] = None
    
    # Example output models that can be used
    OUTPUT_MODELS = {
        'posts': Posts,
        # Add more output models here as needed
    }
    
    try:
        # Initialize browser
        async with Browser(config=browser_config) as browser:
            # Optionally create a persistent browser context
            if os.getenv('USE_PERSISTENT_CONTEXT', 'false').lower() == 'true':
                browser_context = await browser.new_context()
            
            while True:
                task = get_task()
                if task is None or task.lower() in ['exit', 'quit']:
                    break
                
                try:
                    # Get output model from environment if specified
                    output_format = os.getenv('OUTPUT_FORMAT')
                    output_model = OUTPUT_MODELS.get(output_format) if output_format else None
                    
                    # Support for initial actions
                    initial_actions = None  # Could be loaded from config
                    
                    history = await process_task(
                        task, 
                        browser=browser,
                        initial_actions=initial_actions,
                        output_model=output_model
                    )
                    
                    if not history:
                        continue
                    
                    # Save conversation history
                    if history.save_conversation_path:
                        logger.info(f"Conversation saved to: {history.save_conversation_path}")
                        print(f"\nConversation saved to: {history.save_conversation_path}")
                    
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    print(f"\nError: {str(e)}")
                    continue
                    
            # Cleanup browser context if it was created
            if browser_context:
                await browser_context.close()
                
    except Exception as e:
        logger.error(f"Browser initialization error: {str(e)}")
        print(f"\nBrowser initialization error: {str(e)}")
    finally:
        logger.info("Browser Use CLI shutting down")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Gracefully shutting down...")
        print("\nGracefully shutting down...")
        sys.exit(0) 