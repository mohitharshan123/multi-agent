"""
LangChain-based router agent for intelligent request routing.
"""

from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from models.schemas import AgentType
from utils.prompts import ROUTER_SYSTEM_PROMPT, EMERGENCY_KEYWORDS, EMERGENCY_RESPONSE
import re


class LangChainRouterAgent:
    """
    Intelligent routing agent with advanced memory management.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the LangChain router agent."""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=100,
            api_key=openai_api_key
        )
        
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.router_prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "User location: {location}\nHas image: {has_image}\nPrevious agent: {last_agent}\nUser message: {user_text}")
        ])
        
        self.router_chain = (
            self.router_prompt 
            | self.llm 
            | StrOutputParser()
        )
    
    def route_request(
        self, 
        user_text: str, 
        has_image: bool = False, 
        location: Optional[str] = None, 
        conversation_history: Optional[List[Dict]] = None
    ) -> tuple[AgentType, str, bool]:
        """
        Route request using LangChain with advanced context awareness.
        
        Args:
            user_text: User's input text
            has_image: Whether image is attached
            location: User's location
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (agent_type, message, is_emergency)
        """
        
        if self._detect_emergency(user_text):
            return AgentType.ISSUE_DETECTION, EMERGENCY_RESPONSE, True
        
        if has_image:
            return AgentType.ISSUE_DETECTION, "", False
        
        last_agent = self._extract_last_agent(conversation_history)
        
        try:
            routing_input = {
                "user_text": user_text,
                "location": location or "Not provided",
                "has_image": str(has_image),
                "last_agent": last_agent or "None"
            }
            
            router_response = self.router_chain.invoke(routing_input)
            
            return self._parse_router_response(router_response)
            
        except Exception as e:
            print(f"LangChain router error: {e}")
            return self._fallback_routing(user_text)
    
    def _detect_emergency(self, text: str) -> bool:
        """Fast keyword-based emergency detection."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)
    
    def _extract_last_agent(self, conversation_history: Optional[List[Dict]]) -> Optional[str]:
        """Extract the last active agent from conversation history."""
        if not conversation_history:
            return None
            
        for msg in reversed(conversation_history):
            if isinstance(msg, dict):
                role = msg.get("role")
                agent_type = msg.get("agent_type")
            else:
                role = getattr(msg, 'role', None)
                agent_type = getattr(msg, 'agent_type', None)
                
            if role == "assistant" and agent_type:
                return agent_type
        return None
    
    def _parse_router_response(self, response: str) -> tuple[AgentType, str, bool]:
        """Parse LangChain router response."""
        response = response.strip()
        
        if response.startswith("ISSUE_DETECTION"):
            return AgentType.ISSUE_DETECTION, "", False
        elif response.startswith("TENANCY_FAQ"):
            return AgentType.TENANCY_FAQ, "", False
        elif response.startswith("CLARIFY:"):
            clarification = response.replace("CLARIFY:", "").strip()
            return AgentType.ROUTER, clarification, False
        else:
            return AgentType.ROUTER, "I need clarification. Are you asking about property issues or tenancy questions?", False
    
    def _fallback_routing(self, text: str) -> tuple[AgentType, str, bool]:
        """Keyword-based fallback routing when LangChain fails."""
        text_lower = text.lower()
        
        issue_keywords = [
            "damage", "broken", "leak", "crack", "mold", "water", "repair",
            "fix", "maintenance", "issue", "problem", "wall", "ceiling"
        ]
        
        tenancy_keywords = [
            "landlord", "tenant", "rent", "lease", "eviction", "deposit",
            "notice", "agreement", "legal", "rights", "law"
        ]
        
        issue_score = sum(1 for keyword in issue_keywords if keyword in text_lower)
        tenancy_score = sum(1 for keyword in tenancy_keywords if keyword in text_lower)
        
        if issue_score > tenancy_score:
            return AgentType.ISSUE_DETECTION, "", False
        elif tenancy_score > issue_score:
            return AgentType.TENANCY_FAQ, "", False
        else:
            return AgentType.ROUTER, "Please clarify: is this about property damage or tenancy law?", False
    
    def add_to_memory(self, user_message: str, agent_response: str, agent_type: str):
        """Add conversation to LangChain memory."""
        self.memory.chat_memory.add_user_message(user_message)
        self.memory.chat_memory.add_ai_message(f"[{agent_type}] {agent_response}")
    
    def get_memory_context(self) -> List[BaseMessage]:
        """Get conversation history from LangChain memory."""
        return self.memory.chat_memory.messages 