from pydantic import BaseModel
from typing import Optional, List, Union
from enum import Enum

class AgentType(str, Enum):
    ISSUE_DETECTION = "issue_detection"
    TENANCY_FAQ = "tenancy_faq"
    ROUTER = "router"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    MIXED = "mixed"

class UserMessage(BaseModel):
    text: Optional[str] = None
    image_path: Optional[str] = None
    location: Optional[str] = None
    message_type: MessageType

class AgentResponse(BaseModel):
    agent_type: AgentType
    message: str
    confidence: float
    follow_up_questions: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None

class ChatSession(BaseModel):
    session_id: str
    messages: List[dict]
    current_agent: Optional[AgentType] = None

class IssueDetection(BaseModel):
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    recommendations: List[str]
    professional_needed: Optional[str] = None

class TenancyQuery(BaseModel):
    question: str
    location: Optional[str] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    agent_type: str
    message: str
    confidence: float
    is_emergency: bool = False
    session_id: str
    follow_up_questions: Optional[List[str]] = None