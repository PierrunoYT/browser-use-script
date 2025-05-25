"""
Browser Use CLI - Interactive browser automation with AI agents

This script provides an enhanced CLI interface for browser-use with:
- Multiple LLM provider support
- Custom system prompts and behaviors
- Advanced logging and recording
- Custom actions and functions
- Structured output formats
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

# Browser-use imports (aligned with official API)
from browser_use import Agent

# LLM provider imports
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI, ChatOpenAI

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
    """Handle graceful shutdown on SIGINT"""
    logger.info("Gracefully shutting down...")
    sys.exit(0)


def get_task():
    """Get user input for browser task"""
    try:
        return input("\nEnter your browser task (Ctrl+C to exit):\n> ").strip()
    except EOFError:
        return None


# Data models for structured output
class SearchResult(BaseModel):
    """Model for search result data"""
    title: str
    url: str
    description: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SavedContent(BaseModel):
    """Model for saved content data"""
    content: str
    source_url: str
    saved_at: str
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Post(BaseModel):
    """Model for post data (example structured output)"""
    post_title: str
    post_url: str
    num_comments: int
    hours_since_post: int


class Posts(BaseModel):
    """Collection of posts"""
    posts: List[Post]

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

def get_llm_model(provider: str = None):
    """Initialize and return the specified LLM model"""
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

    try:
        provider = LLMProvider(provider)
    except ValueError:
        logger.warning(f"Unsupported provider '{provider}'. Falling back to OpenAI.")
        provider = LLMProvider.OPENAI

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

    elif provider == LLMProvider.GOOGLE:
        raise NotImplementedError("Google support coming soon")

    elif provider == LLMProvider.DEEPSEEK:
        raise NotImplementedError("DeepSeek support coming soon")

    else:
        raise NotImplementedError(f"Provider {provider} not implemented")


async def process_task(task: str, output_model: Optional[Type[BaseModel]] = None):
    """Process a single task using browser-use Agent"""
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

        # Initialize the LLM model based on configuration
        llm = get_llm_model()

        # Initialize the agent with modern browser-use API
        agent = Agent(
            task=task,
            llm=llm,
            use_vision=os.getenv('USE_VISION', 'true').lower() == 'true',
            save_conversation_path=log_file,
        )

        # Run the agent with configurable max_steps
        logger.info("Executing task...")
        result = await agent.run(
            max_steps=int(os.getenv('MAX_STEPS', '100'))
        )

        # Process and display results
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

        logger.info(f"Conversation saved to: {log_file}")
        print(f"\nConversation saved to: {log_file}")

        return result

    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        print(f"\nError executing task: {str(e)}")
        return None


async def main():
    """Main function for the Browser Use CLI"""
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

    # Example output models that can be used
    OUTPUT_MODELS = {
        'posts': Posts,
        # Add more output models here as needed
    }

    try:
        while True:
            task = get_task()
            if task is None or task.lower() in ['exit', 'quit']:
                break

            try:
                # Get output model from environment if specified
                output_format = os.getenv('OUTPUT_FORMAT')
                output_model = OUTPUT_MODELS.get(output_format) if output_format else None

                result = await process_task(task, output_model=output_model)

                if not result:
                    continue

            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print(f"\nError: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\nApplication error: {str(e)}")
    finally:
        logger.info("Browser Use CLI shutting down")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Gracefully shutting down...")
        print("\nGracefully shutting down...")
        sys.exit(0)