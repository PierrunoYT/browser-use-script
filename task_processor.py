import json
import os
from pathlib import Path
from typing import List, Dict
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent
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
            
            # Create task description
            task_description = (
                f"Go to {task['website']} and {task['search_prompt']}. "
                f"Make sure '{task['response_string']}' appears on the page. "
                f"Save any results to {task['save_path']}."
            )
            
            # Initialize browser config and browser
            # Initialize agent with task
            agent = Agent(
                task=task_description,
                llm=ChatOpenAI(model="gpt-4"),
                headless=False  # Make browser visible for debugging
            )
            
            # Run the task
            result = await agent.run()
            
            print(f"✓ Successfully completed task for {task['website']}")
            if browser:
                await browser.close()
            
            return {
                'task': task,
                'success': True,
                'attempts': attempt,
                'history': serialize_history(result)
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
    browser = None
    
    for task in tasks:
        try:
            result = await process_task(task)
            results.append(result)
            
            # Save progress after each task
            with open('task_results.json', 'w') as f:
                json.dump({'results': results}, f, indent=2)
                
        except Exception as e:
            print(f"Failed to process task for {task['website']}: {str(e)}")
            results.append({
                'task': task,
                'success': False,
                'error': str(e)
            })
        finally:
            if browser:
                await browser.close()
                browser = None
    
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
