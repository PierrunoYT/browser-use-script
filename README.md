# Browser Use CLI

An enhanced interactive CLI tool for browser automation using the official [browser-use](https://github.com/browser-use/browser-use) library. This tool provides a user-friendly interface to control your browser using natural language commands with advanced features and customization options.

**🚀 Now aligned with browser-use v0.2.2 - the latest official release!**

## Features

- 🤖 **Multiple LLM Provider Support**:
  - OpenAI GPT-4o (default)
  - Anthropic Claude 3.5 Sonnet (20241022)
  - Azure OpenAI Services
  - Google Gemini (via browser-use)
  - DeepSeek (via browser-use)
  - And more through browser-use's LLM integrations

- 🔒 **Configurable System Behaviors**:
  - Default mode for standard automation
  - Safety First mode with enhanced security
  - Data Collection mode for comprehensive gathering
  - Research mode for systematic exploration
  - Wikipedia First mode for research tasks

- 📸 **Advanced Logging and Recording**:
  - Automatic conversation logging
  - Session recordings (when configured)
  - Comprehensive task execution logs
  - Structured data storage
  - Debug-level logging support

- 🌐 **Modern Browser Integration**:
  - Uses browser-use's optimized browser handling
  - Vision support for visual understanding
  - Configurable browser settings
  - Support for headless and headed modes
  - Cloud browser provider compatibility

- 🛠️ **Enhanced User Experience**:
  - Interactive CLI with clear feedback
  - Structured output formats (JSON, etc.)
  - Error handling and recovery
  - Graceful shutdown handling
  - Cross-platform compatibility

## Quick Start

### Simple Usage

For basic browser automation, you can use the simple example:

```python
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent

load_dotenv()

async def main():
    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

### Interactive CLI

For an enhanced interactive experience with multiple features:

```bash
python main.py
```

## Output Formats

The tool supports structured output formats using Pydantic models. Currently available formats:

### Posts Format
```python
class Post:
    post_title: str
    post_url: str
    num_comments: int
    hours_since_post: int
```

Enable structured output by setting the `OUTPUT_FORMAT` environment variable:
```bash
# Use structured posts format
OUTPUT_FORMAT=posts
```

## Prerequisites

1. **Python 3.11 or higher** (required by browser-use)
2. **API Keys** for your chosen LLM provider:
   - OpenAI API Key (for GPT-4o - default)
   - Anthropic API Key (for Claude 3.5 Sonnet)
   - Azure OpenAI credentials (for Azure OpenAI)
   - Google API Key (for Gemini)
   - DeepSeek API Key (for DeepSeek models)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PierrunoYT/browser-use-script
cd browser-use-script
```

### 2. Install Dependencies

**Using pip:**
```bash
pip install -r requirements.txt
```

**Using uv (recommended):**
```bash
uv pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium --with-deps --no-shell
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env  # On macOS/Linux
copy .env.example .env  # On Windows
```

### 5. Edit `.env` with your settings:

```bash
# Required: Add your API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Configure LLM provider
LLM_PROVIDER=openai  # Options: openai, anthropic, azure, google, deepseek

# Optional: Configure system behavior
SYSTEM_PROMPT=default  # Options: default, safety, collection, research, wiki

# Optional: Browser settings
BROWSER_HEADLESS=false
USE_VISION=true

# Optional: Telemetry
ANONYMIZED_TELEMETRY=true
```

## Usage

### Interactive CLI

Start the enhanced CLI for interactive browser automation:

```bash
python main.py
```

The tool will display your current configuration:
```
Welcome to Browser Use CLI!
Using LLM Provider: OPENAI
System Prompt: DEFAULT
Enter your tasks and watch the browser automation in action.
Press Ctrl+C to exit.
```

### Simple Script Usage

For basic automation, use the simple example:

```bash
python simple_example.py
```

### Example Tasks

Enter your tasks in natural language. Here are some examples:

- **Web Research**: "Search for the latest AI news and summarize the top 3 articles"
- **Information Gathering**: "Go to Wikipedia and find information about quantum computing"
- **Comparison Tasks**: "Compare the pricing of OpenAI GPT-4 and Anthropic Claude"
- **Data Collection**: "Visit Hacker News and get the top 5 posts with their titles and URLs"

## System Prompt Modes

### Default Mode
- Standard browser automation behavior
- Balanced between functionality and safety

### Safety First Mode
- Enhanced security and privacy features
- Requires confirmation for form submissions
- Respects robots.txt and terms of service
- Prevents automated logins without permission
- Avoids suspicious or untrusted links

### Data Collection Mode
- Focused on comprehensive data gathering
- Automatic search result saving
- Screenshot capture of relevant content
- Organized data storage with timestamps
- Detailed URL documentation

## Output and Logs

The tool automatically creates and organizes various outputs:

- `logs/conversation_*.json`: Detailed conversation history
- `logs/results/*.json`: Structured search results
- `logs/screenshots/*.png`: Element screenshots
- `logs/recordings/`: Browser session recordings
- `logs/traces/`: Debug trace files

## Example Tasks

Here are some example tasks you can try:

- "Go to Reddit, search for 'browser-use' and return the first post's title"
- "Search for flights on kayak.com from New York to London"
- "Go to Google Docs and create a new document titled 'Meeting Notes'"
- "Visit GitHub and star the browser-use repository"

## What's New in This Version

### 🚀 Aligned with Official browser-use v0.2.2

- **Modern API**: Updated to use the latest browser-use API patterns
- **Simplified Architecture**: Removed complex custom controller logic in favor of browser-use's built-in capabilities
- **Better Performance**: Leverages browser-use's optimized browser handling
- **Enhanced Compatibility**: Full compatibility with the official browser-use ecosystem

### 🔄 Migration from Previous Versions

If you're upgrading from an older version of this script:

1. **Dependencies**: The script now uses the official browser-use package instead of custom implementations
2. **Configuration**: Environment variables remain largely the same for backward compatibility
3. **Custom Functions**: Complex custom functions have been simplified to align with browser-use patterns
4. **API Changes**: The core Agent API is now simpler and more reliable

## Dependencies

### Core Dependencies
- **browser-use** >= 0.2.2 (official browser automation library)
- **langchain-openai** >= 0.3.11 (OpenAI LLM integration)
- **langchain-anthropic** >= 0.3.3 (Anthropic Claude integration)
- **langchain-core** >= 0.3.49 (LangChain core functionality)
- **playwright** >= 1.52.0 (browser automation engine)
- **python-dotenv** >= 1.0.1 (environment variable management)
- **pydantic** >= 2.10.4 (data validation and serialization)

### Optional Dependencies
- **rich** >= 14.0.0 (enhanced CLI formatting)
- **click** >= 8.1.8 (CLI framework)
- **sentence-transformers** >= 4.0.2 (for memory features)

## Contributing

Contributions are welcome! Feel free to open issues for bugs or feature requests.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Browser Configuration Options

### Standard Browser

The default configuration launches a new browser instance with customizable settings:

```bash
# .env configuration
BROWSER_HEADLESS=false
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=1100
```

### Connect to Existing Chrome

Connect to your real Chrome browser with existing profiles and logged-in sessions:

```bash
# .env configuration
CHROME_INSTANCE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe  # Windows
CHROME_INSTANCE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome  # macOS
CHROME_INSTANCE_PATH=/usr/bin/google-chrome  # Linux
```

### Cloud Browser Providers

Connect to cloud-based browser services for enhanced reliability:

```bash
# .env configuration
# WebSocket connection (wss)
BROWSER_WSS_URL=wss://your-provider.com/browser

# Chrome DevTools Protocol (CDP)
BROWSER_CDP_URL=http://your-cdp-provider.com
```

### Additional Browser Settings

Fine-tune browser behavior with these settings:

```bash
# .env configuration
# Page Load Settings
MIN_PAGE_LOAD_TIME=0.5
NETWORK_IDLE_TIME=1.0
MAX_PAGE_LOAD_TIME=5.0

# Security Settings
BROWSER_DISABLE_SECURITY=true
IGNORE_HTTPS_ERRORS=true
JAVASCRIPT_ENABLED=true

# Display Settings
HIGHLIGHT_ELEMENTS=true
VIEWPORT_EXPANSION=500
BROWSER_LOCALE=en-US

# URL Restrictions
ALLOWED_DOMAINS=["example.com","another-domain.com"]

# Debug and Recording
SAVE_RECORDING_PATH=logs/recordings
TRACE_PATH=logs/traces
```

## Common Browser Configurations

### Local Development
```bash
BROWSER_HEADLESS=false
BROWSER_DISABLE_SECURITY=true
USE_VISION=true
```

### Production Environment
```bash
BROWSER_HEADLESS=true
BROWSER_DISABLE_SECURITY=false
USE_VISION=true
ALLOWED_DOMAINS=["trusted-domain.com"]
```

### Using Existing Chrome Profile
```bash
CHROME_INSTANCE_PATH=/path/to/chrome
USE_PERSISTENT_CONTEXT=true
```

## Environment Variables

In addition to the basic configuration, you can customize:

### Function Control
```bash
# Exclude specific functions
EXCLUDED_ACTIONS=[]  # JSON array of action IDs

# Output format
OUTPUT_FORMAT=  # Options: posts, or leave empty for text
```

### Debug Settings
```bash
# Enable debug logging for model thoughts
LOG_LEVEL=DEBUG

# Save browser recordings
SAVE_RECORDING_PATH=logs/recordings
TRACE_PATH=logs/traces
```

## Output Directory Structure

The tool organizes outputs in the following structure:

```
logs/
├── browser_use.log         # Main log file
├── conversation_*.json     # Conversation history
├── results/               # Structured search results
├── screenshots/           # Element screenshots
├── content/              # Extracted page content
├── tables/              # CSV table data
├── downloads/           # Downloaded files
├── recordings/         # Browser session recordings
└── traces/            # Debug trace files
```
