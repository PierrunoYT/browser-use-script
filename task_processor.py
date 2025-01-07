import json
import os
from pathlib import Path
from typing import List, Dict
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize controller for custom actions
controller = Controller()

async def load_tasks(json_file_path: str) -> List[Dict]:
    """Load tasks from a JSON file."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data['tasks']

def serialize_history(history):
    """Convert agent history to JSON serializable format."""
    if history is None:
        return []
    
    serialized = []
    for item in history:
        # Handle case where item is a tuple
        if isinstance(item, tuple):
            action, input_val, output, timestamp = item
        else:
            action = getattr(item, 'action', 'unknown')
            input_val = getattr(item, 'input', '')
            output = getattr(item, 'output', '')
            timestamp = getattr(item, 'timestamp', '')
            
        entry = {
            'action': str(action),
            'input': str(input_val),
            'output': str(output),
            'timestamp': str(timestamp)
        }
        serialized.append(entry)
    return serialized

async def process_task(task: Dict, max_attempts: int = 3) -> Dict:
    """Process a single task using browser-use-script with retry mechanism."""
    # Ensure directories exist
    Path(task['save_path']).mkdir(parents=True, exist_ok=True)
    Path(task['screenshot_dir']).mkdir(parents=True, exist_ok=True)
    
    browser = None
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            print(f"Processing task for {task['website']} (Attempt {attempt}/{max_attempts})")
            
            # Create a combined task description that includes all paths and validation
            task_description = (
                f"1. Navigate directly to {task['website']} and wait for the page to load completely.\n"
                f"2. Once loaded, {task['search_prompt']}.\n"
                f"3. Wait for and verify that '{task['response_string']}' appears on the page.\n"
                f"4. Save any screenshots to {task['screenshot_dir']}.\n"
                f"5. Save any extracted data or results to {task['save_path']}."
            )
            
            # Initialize browser config and browser
            browser_config = BrowserConfig(
                headless=False  # Make browser visible for debugging
            )
            
            if browser is None:
                browser = Browser(config=browser_config)
            
            # Initialize agent with task and browser
            agent = Agent(
                task=task_description,
                llm=ChatOpenAI(
                    model="gpt-4o",
                    temperature=0,  # More deterministic responses
                    max_retries=2  # Limit retries on failure
                ),
                controller=controller,
                browser=browser
            )
            
            # Run the task
            history = await agent.run()
            
            print(f"✓ Successfully completed task for {task['website']}")
            return {
                'task': task,
                'success': True,
                'attempts': attempt,
                'history': serialize_history(history)
            }
            
        except Exception as e:
            print(f"✗ Attempt {attempt} failed for {task['website']}: {str(e)}")
            if browser:
                await browser.close()
                browser = None
            
            if attempt == max_attempts:
                return {
                    'task': task,
                    'success': False,
                    'attempts': attempt,
                    'error': str(e)
                }
            
            attempt += 1
            await asyncio.sleep(2)  # Wait before retrying
    
    return {
        'task': task,
        'success': False,
        'attempts': max_attempts,
        'error': 'Maximum attempts reached'
    }

async def process_all_tasks(tasks_file: str):
    """Process tasks from the JSON file one at a time."""
    tasks = await load_tasks(tasks_file)
    results = []
    
    for task in tasks:
        result = await process_task(task)
        results.append(result)
        
        # Save progress after each task
        with open('task_results.json', 'w') as f:
            json.dump({'results': results}, f, indent=2)
    
    return results

async def main():
    # Example usage
    tasks_file = "tasks.json"
    if not os.path.exists(tasks_file):
        print(f"Please create a {tasks_file} file with your tasks first.")
        return
    
    await process_all_tasks(tasks_file)

if __name__ == "__main__":
    asyncio.run(main())
