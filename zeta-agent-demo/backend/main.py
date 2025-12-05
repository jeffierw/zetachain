import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import qwen-agent related modules
# Note: qwen-agent usage might vary slightly based on version, assuming standard usage for tool calling or generation
# Since the requirement is "Agent output structured parameters", we can use a system prompt to enforce JSON output.
import dashscope
from http import HTTPStatus

from zetachain import send_zeta, get_address

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

class ExecuteRequest(BaseModel):
    recipient: str
    amount: float
    token: str

@app.get("/api/status")
def get_status():
    address = get_address()
    return {"status": "ok", "address": address}

@app.post("/api/chat")
def chat_to_agent(request: ChatRequest):
    """
    Simulate Agent behavior: Input Natural Language -> Output Structured Intent
    We use Qwen via DashScope SDK or Qwen-Agent if installed.
    Since we need struct output, we will prompt Qwen to return JSON.
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY not found")
    
    # Simple prompt for the agent
    # We want to extract: type, recipient, amount, token
    system_prompt = """You are a blockchain agent. Your goal is to extract transaction details from user input.
    Output ONLY valid JSON with keys: "type" (must be "transfer"), "recipient" (address), "amount" (number), "token" (e.g. "ZETA").
    If information is missing, try to infer or set null.
    Example output: {"type": "transfer", "recipient": "0x123", "amount": 0.1, "token": "ZETA"}
    """
    
    # Using dashscope directly as it's the core of qwen-agent for simple generation
    # Or using qwen_agent.llm if strictly following qwen-agent wrapper
    # Let's use dashscope for simplicity as qwen-agent wraps it but often adds complexity for multi-agent.
    # User asked for "qwen agent", let's try to use the library concepts if possible.
    # But for a single turn extraction, simple generation is best.
    
    try:
        response = dashscope.Generation.call(
            model='qwen-turbo',
            api_key=api_key,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': request.prompt}
            ],
            result_format='message',  # set the result to be "message" format.
        )
        
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0].message.content
            # Clean up content to ensure it's JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError:
                 return {"error": "Failed to parse JSON from agent", "raw": content}
        else:
            raise HTTPException(status_code=500, detail=f"Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
def execute_transaction(request: ExecuteRequest):
    if request.token.upper() != "ZETA":
         raise HTTPException(status_code=400, detail="Only ZETA token supported")
    
    try:
        tx_hash = send_zeta(request.recipient, request.amount)
        return {"status": "success", "tx_hash": tx_hash, "explorer_url": f"https://athens3.explorer.zetachain.com/tx/{tx_hash}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
