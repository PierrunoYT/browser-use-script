# Browser Use CLI

An interactive CLI tool for browser automation using the [browser-use](https://github.com/browser-use/browser-use) library. This tool allows you to control your browser using natural language commands through an interactive command-line interface.

## Features

- 🤖 Multiple LLM Provider Support:
  - OpenAI GPT-4o (default)
  - Anthropic Claude 3.5 Sonnet (20241022)
  - Azure OpenAI Services
  - Gemini (coming soon)
  - DeepSeek-V3 (coming soon)
  - DeepSeek-R1 (coming soon)
  - Ollama (coming soon)
- 🔒 Configurable System Behaviors:
  - Default mode for standard automation
  - Safety First mode with enhanced security
  - Data Collection mode for comprehensive gathering
  - Research mode for systematic exploration
  - Wikipedia First mode for research tasks
- 📸 Advanced Logging and Recording:
  - Automatic screenshots of elements
  - Session recordings
  - Comprehensive conversation logs
  - Structured data storage
  - Debug-level thought process logging
- 🌐 Customizable Browser Settings:
  - Non-headless mode for visibility
  - Optimized window sizing
  - Network idle waiting
  - Trace and debug capabilities
  - Connect to existing Chrome instance
  - Support for cloud browser providers
- 🛠️ Custom Actions:
  - User confirmations
  - Search result saving
  - Element screenshots
  - Structured data handling
  - Table data extraction
  - File downloads
  - Content extraction

## Custom Functions

The tool provides several built-in custom functions that can be enabled or disabled:

- `confirm`: Ask for user confirmation before actions
- `save_search`: Save structured search results
- `screenshot`: Take screenshots of specific elements
- `extract_content`: Save page content
- `extract_table`: Extract and save table data as CSV
- `download`: Download files from URLs

You can exclude specific functions using the `EXCLUDED_ACTIONS` environment variable:

```bash
# Exclude file downloads and table extraction
EXCLUDED_ACTIONS=["download", "extract_table"]
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

1. **API Keys Required**:
   - OpenAI API Key (default provider, for GPT-4o)
   - Anthropic API Key (optional, for Claude 3.5 Sonnet)
   - Azure OpenAI credentials (optional)
2. **Browser Use API Key** (optional but recommended)

## Setup

1. Clone this repository:

**Windows:**
```bash
git clone https://github.com/PierrunoYT/browser-use-script
cd browser-use-script
```

**macOS/Linux:**
```bash
git clone https://github.com/PierrunoYT/browser-use-script
cd browser-use-script
```

2. Install dependencies:

**Windows:**
```bash
python -m pip install -r requirements.txt
```

**macOS/Linux:**
```bash
pip3 install -r requirements.txt
```

3. Install playwright browsers:

**All platforms:**
```bash
playwright install
```

4. Configure environment:

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

5. Edit `.env` with your settings:
```bash
# Required: Choose your LLM provider and add API key
LLM_PROVIDER=openai  # Options: openai, anthropic, azure
OPENAI_API_KEY=your_key_here

# Optional: Configure system behavior
SYSTEM_PROMPT=default  # Options: default, safety, collection

# Optional: Alternative LLM providers
ANTHROPIC_API_KEY=your_key_here  # Required for Claude 3.5 Sonnet
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_KEY=your_key_here

# Optional: Telemetry settings
ANONYMIZED_TELEMETRY=true
```

## Usage

1. Start the CLI:

**Windows:**
```bash
python main.py
```

**macOS/Linux:**
```bash
python3 main.py
```

2. The tool will display your current configuration:
```
Welcome to Browser Use CLI!
Using LLM Provider: OPENAI
System Prompt: DEFAULT
Enter your tasks and watch the browser automation in action.
Press Ctrl+C to exit.
```

3. Enter your tasks in natural language. Examples:
- "Search for the latest AI news and save the results"
- "Go to Wikipedia and find information about quantum computing"
- "Visit a tech blog and take screenshots of interesting articles"

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

## Dependencies

- langchain-openai
- langchain-anthropic
- browser-use
- playwright
- python-dotenv
- pydantic

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
