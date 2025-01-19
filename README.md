# Browser Use CLI

An interactive CLI tool for browser automation using the [browser-use](https://github.com/browser-use/browser-use) library. This tool allows you to control your browser using natural language commands through an interactive command-line interface.

## Features

- Interactive CLI for continuous browser automation tasks
- Powered by GPT-4 and browser-use
- Simple setup and usage
- Graceful exit handling

## Setup

1. Clone this repository:
```bash
git clone [your-repo-url]
cd [your-repo-name]
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Install playwright browsers:
```bash
playwright install
```

4. Set up your environment variables:
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
```bash
python main.py
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

This project is licensed under the MIT License - see the LICENSE file for details.
