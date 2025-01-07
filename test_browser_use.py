import unittest
import asyncio
from unittest.mock import patch, MagicMock
from cli import ask_human
from task_processor import load_tasks, serialize_history
import json
import os
from pathlib import Path

class TestBrowserUse(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sample_tasks = {
            "tasks": [
                {
                    "id": "1",
                    "description": "Search for flights",
                    "url": "https://example.com"
                }
            ]
        }
        # Create a temporary tasks file for testing
        self.test_tasks_file = "test_tasks.json"
        with open(self.test_tasks_file, "w") as f:
            json.dump(self.sample_tasks, f)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_tasks_file):
            os.remove(self.test_tasks_file)

    @patch('builtins.input', return_value='test input')
    def test_ask_human(self, mock_input):
        result = ask_human("Test question")
        self.assertEqual(result, 'test input')
        mock_input.assert_called_once()

    async def test_load_tasks(self):
        tasks = await load_tasks(self.test_tasks_file)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['id'], '1')
        self.assertEqual(tasks[0]['description'], 'Search for flights')

    def test_serialize_history(self):
        # Test with empty history
        self.assertEqual(serialize_history(None), [])

        # Test with actual history items
        history = [
            ('action1', 'input1', 'output1', '2025-01-07T18:45:21+01:00'),
            ('action2', 'input2', 'output2', '2025-01-07T18:45:21+01:00')
        ]
        serialized = serialize_history(history)
        self.assertEqual(len(serialized), 2)
        self.assertEqual(serialized[0]['action'], 'action1')
        self.assertEqual(serialized[0]['input'], 'input1')
        self.assertEqual(serialized[0]['output'], 'output1')

if __name__ == '__main__':
    unittest.main()
