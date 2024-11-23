# Browser Use CLI

A command-line interface for browser automation using AI agents.

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Set up environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
ANONYMIZED_TELEMETRY=true
```

## Usage

The CLI provides several commands for browser automation:

### General Task Execution
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

## Examples

1. Search for a product:
```bash
python app.py run "Find the price of iPhone 15 Pro on Amazon"
```

2. Research a topic:
```bash
python app.py search "wikipedia.org" "history of artificial intelligence"
```

3. Find flights:
```bash
python app.py flights "San Francisco" "Tokyo" "2024-06-15" --return-date "2024-06-30"