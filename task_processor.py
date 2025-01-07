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
        entry = {
            'action': str(item.action),
            'input': str(item.input),
            'output': str(item.output),
            'timestamp': str(item.timestamp)
        }
        serialized.append(entry)
    return serialized

async def process_task(task: Dict, browser: Browser = None) -> Dict:
    """Process a single task using browser-use-script."""
    # Ensure directories exist
    Path(task['save_path']).mkdir(parents=True, exist_ok=True)
    Path(task['screenshot_dir']).mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Starting task for website: {task['website']}")
        
        # Create a combined task description that includes the website and validation
        task_description = f"Go to {task['website']} and {task['search_prompt']}. Verify that '{task['response_string']}' appears on the page."
        
        # Initialize browser config
        browser_config = BrowserConfig(
            screenshot_dir=task['screenshot_dir'],
            headless=False  # Make browser visible for debugging
        )
        
        # Initialize agent with task and browser config
        agent = Agent(
            task=task_description,
            llm=ChatOpenAI(model="gpt-4o"),
            controller=controller,
            browser_config=browser_config
        )
        
        # Run the task
        history = await agent.run()
        
        print(f"✓ Successfully completed task for {task['website']}")
        return {
            'task': task,
            'success': True,
            'history': serialize_history(history)
        }
    except Exception as e:
        print(f"✗ Failed task for {task['website']}: {str(e)}")
        return {
            'task': task,
            'success': False,
            'error': str(e)
        }

async def process_all_tasks(tasks_file: str):
    """Process all tasks from the JSON file concurrently."""
    tasks = await load_tasks(tasks_file)
    
    # Create all tasks concurrently
    tasks_coroutines = [process_task(task) for task in tasks]
    results = await asyncio.gather(*tasks_coroutines, return_exceptions=True)
    
    # Process results
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
    print(f"\nProcessing complete: {successful}/{len(results)} tasks successful")
    
    # Print detailed results
    for result in results:
        if isinstance(result, dict):
            website = result['task']['website']
            if result['success']:
                print(f"Task for {website}: Success")
                # Save results if needed
                save_path = result['task']['save_path']
                os.makedirs(save_path, exist_ok=True)
                with open(os.path.join(save_path, 'result.json'), 'w') as f:
                    json.dump(result['history'], f, indent=2)
            else:
                print(f"Task for {website}: Failed - {result.get('error', 'Unknown error')}")
        else:
            print(f"Task failed with unexpected error: {str(result)}")
    
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
