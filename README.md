# Browser Use CLI

An interactive CLI tool for browser automation using the [browser-use](https://github.com/browser-use/browser-use) library. This tool allows you to control your browser using natural language commands through an interactive command-line interface.

## Features

- 🤖 Multiple LLM Provider Support:
  - OpenAI GPT-4o (default)
  - Anthropic Claude 3.5 Sonnet (20241022)
  - Azure OpenAI Services
- 🔒 Configurable System Behaviors:
  - Default mode for standard automation
  - Safety First mode with enhanced security
  - Data Collection mode for comprehensive gathering
- 📸 Advanced Logging and Recording:
  - Automatic screenshots of elements
  - Session recordings
  - Comprehensive conversation logs
  - Structured data storage
- 🌐 Customizable Browser Settings:
  - Non-headless mode for visibility
  - Optimized window sizing
  - Network idle waiting
  - Trace and debug capabilities
- 🛠️ Custom Actions:
  - User confirmations
  - Search result saving
  - Element screenshots
  - Structured data handling

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
