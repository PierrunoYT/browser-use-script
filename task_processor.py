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
        print(f"Starting task for website: {task['website']}")
        # Run the browser script for this task
        result = await run_browser_script(script_config)
        print(f"✓ Successfully completed task for {task['website']}")
        return {
            'task': task,
            'success': True,
            'result': result
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
