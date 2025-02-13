import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional
from pathlib import Path
from .agent import TaskAgent

# Load environment variables
load_dotenv()

app = FastAPI()
agent = TaskAgent()

@app.get("/")
async def root():
    return {"message": "LLM Automation Agent API is running"}

@app.post("/run")
async def run_task(task: str):
    try:
        # Security checks
        if not task:
            raise HTTPException(status_code=400, detail="Task description is required")
        
        if "../" in task or (task.startswith("/") and not task.startswith("/data")):
            raise HTTPException(status_code=400, detail="Invalid path access")
        
        if any(word in task.lower() for word in ["delete", "remove", "rm", "del"]):
            raise HTTPException(status_code=400, detail="File deletion not allowed")
        
        result = await agent.execute_task(task)
        return {"status": "success", "result": result}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    try:
        if not path:
            raise HTTPException(status_code=400, detail="File path is required")
        
        # Security check
        if "../" in path or not path.startswith("/data"):
            raise HTTPException(status_code=400, detail="Invalid path access")
        
        file_path = Path(path.lstrip("/"))
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        content = file_path.read_text()
        return PlainTextResponse(content)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))