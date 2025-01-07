import json
import os
from pathlib import Path
from typing import List, Dict
import asyncio
from cli import run_browser_script

async def load_tasks(json_file_path: str) -> List[Dict]:
    """Load tasks from a JSON file."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data['tasks']

async def process_task(task: Dict) -> Dict:
    """Process a single task using browser-use-script."""
    # Ensure directories exist
    Path(task['save_path']).mkdir(parents=True, exist_ok=True)
    Path(task['screenshot_dir']).mkdir(parents=True, exist_ok=True)
    
    # Prepare the script configuration
    script_config = {
        'website': task['website'],
        'search_prompt': task['search_prompt'],
        'response_string': task['response_string'],
        'save_path': task['save_path'],
        'screenshot_dir': task['screenshot_dir']
    }
    
    try:
        # Run the browser script for this task
        result = await run_browser_script(script_config)
        return {
            'task': task,
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'task': task,
            'success': False,
            'error': str(e)
        }

async def process_all_tasks(tasks_file: str):
    """Process all tasks from the JSON file."""
    tasks = await load_tasks(tasks_file)
    results = []
    
    for task in tasks:
        print(f"Processing task for website: {task['website']}")
        result = await process_task(task)
        results.append(result)
        
        # Log the result
        if result['success']:
            print(f"✓ Successfully processed task for {task['website']}")
        else:
            print(f"✗ Failed to process task for {task['website']}: {result.get('error', 'Unknown error')}")
    
    return results

async def main():
    # Example usage
    tasks_file = "tasks.json"
    if not os.path.exists(tasks_file):
        print(f"Please create a {tasks_file} file with your tasks first.")
        return
    
    results = await process_all_tasks(tasks_file)
    
    # Print summary
    successful = sum(1 for r in results if r['success'])
    print(f"\nProcessing complete: {successful}/{len(results)} tasks successful")

if __name__ == "__main__":
    asyncio.run(main())
