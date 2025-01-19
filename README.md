# Browser Use CLI

An interactive CLI tool for browser automation using the [browser-use](https://github.com/browser-use/browser-use) library. This tool allows you to control your browser using natural language commands through an interactive command-line interface.

## Prerequisites

1. **OpenAI API Key**: Required for GPT-4 integration. Get it from [OpenAI's platform](https://platform.openai.com/api-keys)
2. **Browser Use API Key**: Optional but recommended. Get it by:
   - Visiting [browser-use GitHub repository](https://github.com/browser-use/browser-use)
   - Following their documentation for API key generation
   - Note: The tool works without this key but may have limited functionality

## Features

- Interactive CLI for continuous browser automation tasks
- Powered by GPT-4 and browser-use
- Simple setup and usage
- Graceful exit handling
- Cross-platform support (Windows, macOS, Linux)

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

2. Install the required packages:

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

4. Set up your environment variables:

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

5. Edit the `.env` file and add your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key_here
BROWSER_USE_API_KEY=your_browser_use_api_key_here  # Optional
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

2. Enter your browser automation tasks when prompted. For example:
```
Welcome to Browser Use CLI!
Enter your tasks and watch the browser automation in action.
Press Ctrl+C to exit.

Enter your browser task (Ctrl+C to exit):
> Go to Reddit and search for "browser-use"
```

3. The tool will execute your task and show the results.

4. Continue entering new tasks or exit:
   - Press Ctrl+C to exit
   - Type 'exit' or 'quit' to close the program
   - Enter a new task to continue automation

## Example Tasks

Here are some example tasks you can try:

- "Go to Reddit, search for 'browser-use' and return the first post's title"
- "Search for flights on kayak.com from New York to London"
- "Go to Google Docs and create a new document titled 'Meeting Notes'"
- "Visit GitHub and star the browser-use repository"

## Dependencies

- langchain-openai
- browser-use
- playwright
- python-dotenv
- lxml
- lxml-html-clean

## Contributing

Contributions are welcome! Feel free to open issues for bugs or feature requests.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
