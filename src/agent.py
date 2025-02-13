import os
import json
import subprocess
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import aiohttp
import sqlite3
import pandas as pd
from PIL import Image
import numpy as np
import re
import markdown2
import requests
import git
from io import BytesIO

class TaskAgent:
    def __init__(self):
        self.ai_proxy_token = os.environ.get("AIPROXY_TOKEN")
        if not self.ai_proxy_token:
            raise ValueError("AIPROXY_TOKEN environment variable is required")
        
        # Ensure data directory exists
        os.makedirs('/data', exist_ok=True)

    def _validate_path(self, path: str) -> bool:
        """Validate path is within /data directory."""
        try:
            full_path = os.path.abspath(path)
            data_dir = os.path.abspath('/data')
            return full_path.startswith(data_dir)
        except:
            return False

    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute a task based on its description."""
        try:
            # Phase A Tasks
            if any(word in task_description.lower() for word in ["install uv", "datagen"]):
                return await self._handle_uv_installation(task_description)
            elif "format" in task_description.lower() and "prettier" in task_description.lower():
                return await self._handle_prettier_formatting(task_description)
            elif any(word in task_description.lower() for word in ["wednesday", "thursday", "sunday"]):
                return await self._handle_date_counting(task_description)
            elif "sort" in task_description.lower() and "contacts" in task_description.lower():
                return await self._handle_json_sorting(task_description)
            elif "log" in task_description.lower() and "recent" in task_description.lower():
                return await self._handle_log_processing(task_description)
            elif "markdown" in task_description.lower() and "h1" in task_description.lower():
                return await self._handle_markdown_index(task_description)
            elif "email" in task_description.lower() and "sender" in task_description.lower():
                return await self._handle_email_extraction(task_description)
            elif "credit" in task_description.lower() and "card" in task_description.lower():
                return await self._handle_credit_card_extraction(task_description)
            elif "similar" in task_description.lower() and "comments" in task_description.lower():
                return await self._handle_comment_similarity(task_description)
            elif any(word in task_description.lower() for word in ["sqlite", "database", "ticket"]):
                return await self._handle_database_query(task_description)
            
            # Phase B Tasks
            elif "api" in task_description.lower() and "fetch" in task_description.lower():
                return await self._handle_api_fetch(task_description)
            elif "git" in task_description.lower():
                return await self._handle_git_operations(task_description)
            elif "sql" in task_description.lower():
                return await self._handle_sql_query(task_description)
            elif "scrape" in task_description.lower() or "extract" in task_description.lower():
                return await self._handle_web_scraping(task_description)
            elif "image" in task_description.lower():
                return await self._handle_image_processing(task_description)
            elif "audio" in task_description.lower() or "mp3" in task_description.lower():
                return await self._handle_audio_processing(task_description)
            elif "markdown" in task_description.lower() and "html" in task_description.lower():
                return await self._handle_markdown_conversion(task_description)
            elif "csv" in task_description.lower() and "filter" in task_description.lower():
                return await self._handle_csv_filtering(task_description)
            else:
                return {"status": "error", "message": "Task type not recognized"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Phase A Task Handlers
    async def _handle_uv_installation(self, task_description: str) -> Dict[str, Any]:
        """A1: Install uv and run datagen.py"""
        try:
            # Install uv
            subprocess.run(['curl', '-LsSf', 'https://astral.sh/uv/install.sh', '|', 'sh'], shell=True, check=True)
            
            # Download and run datagen.py
            script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
            email = os.environ.get("USER_EMAIL", "default@example.com")
            
            response = requests.get(script_url)
            with open("datagen.py", "w") as f:
                f.write(response.text)
            
            subprocess.run(['python', 'datagen.py', email], check=True)
            return {"status": "success", "message": "UV installed and datagen.py executed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _handle_prettier_formatting(self, task_description: str) -> Dict[str, Any]:
        """A2: Format markdown with prettier"""
        try:
            input_file = "/data/format.md"
            subprocess.run(['prettier', '--write', input_file], check=True)
            return {"status": "success", "message": f"Formatted {input_file}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ... [Previous handlers remain the same] ...

    # Phase B Task Handlers
    async def _handle_api_fetch(self, task_description: str) -> Dict[str, Any]:
        """B3: Fetch data from an API"""
        try:
            # Use LLM to extract API URL and parameters from task description
            prompt = f"Extract the API URL and parameters from: {task_description}"
            api_info = await self._handle_llm_request(prompt)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(api_info['url'], params=api_info.get('params', {})) as response:
                    data = await response.json()
                    
                    # Save response to data directory
                    output_file = '/data/api_response.json'
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    return {"status": "success", "message": "API data fetched and saved"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _handle_git_operations(self, task_description: str) -> Dict[str, Any]:
        """B4: Clone repo and make commit"""
        try:
            # Extract repo URL and commit message from task description using LLM
            prompt = f"Extract the git repository URL and commit message from: {task_description}"
            git_info = await self._handle_llm_request(prompt)
            
            repo_path = '/data/git_repo'
            repo = git.Repo.clone_from(git_info['url'], repo_path)
            
            # Make changes and commit
            with open(f"{repo_path}/README.md", 'a') as f:
                f.write("\nUpdated by LLM Agent")
            
            repo.index.add(['README.md'])
            repo.index.commit(git_info['commit_message'])
            
            return {"status": "success", "message": "Git operations completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ... Additional Phase B handlers ...

    async def _handle_llm_request(self, prompt: str) -> str:
        """Helper method to make LLM API requests"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.ai_proxy_token}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
            async with session.post(
                "https://api.aiproxy.xyz/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content']