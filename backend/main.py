"""
FastAPI backend using LangChain and LangGraph for multi-agent orchestration.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from typing import Optional, List
from PIL import Image
import io
import os

from models.schemas import ChatResponse
from agents.langgraph_workflow import RealEstateWorkflow

app = FastAPI(title="Real Estate Multi-Agent Chatbot (LangGraph)", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://multi-agent-vvuk.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow: Optional[RealEstateWorkflow] = None

def get_workflow() -> RealEstateWorkflow:
    """Get or initialize the LangGraph workflow."""
    global workflow
    if workflow is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        workflow = RealEstateWorkflow(openai_api_key)
    return workflow

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real Estate Multi-Agent Chatbot API (LangGraph)",
        "version": "2.0.0",
        "framework": "LangChain + LangGraph",
        "features": [
            "Intelligent agent routing",
            "Emergency detection",
            "Image analysis",
            "Conversation memory",
            "State management"
        ]
    }

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    location: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    conversation_history: str = Form("[]")
):
    """Unified endpoint to handle both text and image requests using LangGraph workflow."""
    try:
        workflow_instance = get_workflow()
        
        try:
            parsed_history = json.loads(conversation_history) if conversation_history else []
        except json.JSONDecodeError:
            parsed_history = []
        
        image = None
        if file and file.content_type and file.content_type.startswith('image/'):
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
        
        result = workflow_instance.process_request(
            user_text=message,
            session_id=session_id or str(uuid.uuid4()),
            image=image,
            location=location,
            conversation_history=parsed_history
        )
        
        return ChatResponse(
            agent_type=result["agent_type"],
            message=result["message"],
            confidence=result["confidence"],
            is_emergency=result["is_emergency"],
            session_id=result["session_id"],
            follow_up_questions=result["follow_up_questions"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        workflow_instance = get_workflow()
        return {
            "status": "healthy",
            "framework": "LangChain + LangGraph",
            "agents": {
                "router": "LangChainRouterAgent",
                "issue_detection": "LangChainIssueDetectionAgent", 
                "tenancy_faq": "TenancyFAQAgent"
            },
            "features": {
                "emergency_detection": True,
                "image_analysis": True,
                "conversation_memory": True,
                "state_management": True,
                "unified_endpoint": True
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 