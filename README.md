# Browser Use CLI

A command-line interface for browser automation using AI agents. This tool helps automate various browser-based tasks including web searches, flight searches, and general browser automation tasks.

## Quick Start

On Windows, simply run the PowerShell script to set up and start the application:
```powershell
.\start_app.ps1
```
This script will:
1. Create a virtual environment (if it doesn't exist)
2. Activate the virtual environment
3. Install all required dependencies
4. Install Playwright browsers
5. Start the application in continuous execution mode

The only prerequisite is having Python installed on your system.

## Environment Setup

Before running the application, make sure to set up your environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
ANONYMIZED_TELEMETRY=true
```

## Manual Installation

If you prefer to set up the environment manually, follow these steps:

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- Windows:
```powershell
.\.venv\Scripts\activate
```
- Unix/MacOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Usage

The CLI provides several commands for browser automation. All results are automatically saved as markdown files in the `results` directory with timestamps.

### General Task Execution
```bash
python app.py run
```
This will start an interactive session where you can input your automation tasks.

You can also provide a task directly:
```bash
python app.py run "your task description"
```

Example:
```bash
python app.py run "Go to wikipedia.org and search for artificial intelligence"
```

### Search on Specific Website
```bash
python app.py search URL "search query"
```

Example:
```bash
python app.py search "https://example.com" "product information"
```

### Flight Search
```bash
python app.py flights FROM_LOCATION TO_LOCATION DATE [--return-date RETURN_DATE]
```

Example:
```bash
# One-way flight
python app.py flights "New York" "London" "2024-05-01"

# Round trip
python app.py flights "New York" "London" "2024-05-01" --return-date "2024-05-15"
```

### Options

All commands support the following options:
- `--model`, `-m`: Specify the OpenAI model to use (default: "gpt-4")
- `--api-key`, `-k`: Provide OpenAI API key directly (optional if set in .env)

## Output

All task results are automatically saved as markdown files in the `results` directory. Each file includes:
- Timestamp of execution
- Task description
- Task result

Files are named in the format: `task_YYYYMMDD_HHMMSS.md`

## Examples

1. Search for a product:
```bash
python app.py run "Find the price of iPhone 15 Pro on Amazon"
```

2. Research a topic:
```bash
python app.py run "Research and summarize recent developments in AI"
```

3. Compare prices:
```bash
python app.py run "Compare prices of MacBook Pro across different retailers"