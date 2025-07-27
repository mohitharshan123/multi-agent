from typing import TypedDict, Annotated, Optional, List, Dict, Any, Sequence
from typing_extensions import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage,
    ToolMessage
)
from langchain_core.tools import tool
from PIL import Image
import json

from models.schemas import AgentType, AgentResponse
from agents.router import LangChainRouterAgent
from agents.issue_agent import LangChainIssueDetectionAgent
from agents.faq_agent import TenancyFAQAgent 
from utils.prompts import EMERGENCY_RESPONSE


class ConversationState(TypedDict):
    """State maintained throughout the conversation workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_text: str
    user_location: Optional[str]
    has_image: bool
    image_data: Optional[Image.Image]
    current_agent: Optional[str]
    agent_response: Optional[str]
    confidence_score: float
    is_emergency: bool
    follow_up_questions: List[str]
    session_id: str
    conversation_history: List[Dict[str, Any]]


class RealEstateWorkflow:
    """
    LangGraph-powered workflow orchestrating the multi-agent real estate system.
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize the workflow with all agents."""
        self.router_agent = LangChainRouterAgent(openai_api_key)
        self.issue_agent = LangChainIssueDetectionAgent(openai_api_key)
        self.faq_agent = TenancyFAQAgent(openai_api_key) 
        
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow definition."""
        
        workflow = StateGraph(ConversationState)
        
        workflow.add_node("route_request", self._route_request)
        workflow.add_node("handle_emergency", self._handle_emergency)
        workflow.add_node("issue_detection", self._handle_issue_detection)
        workflow.add_node("tenancy_faq", self._handle_tenancy_faq)
        workflow.add_node("router_clarification", self._handle_router_clarification)
        workflow.add_node("finalize_response", self._finalize_response)
        
        workflow.set_entry_point("route_request")
        
        workflow.add_conditional_edges(
            "route_request",
            self._determine_next_step,
            {
                "emergency": "handle_emergency",
                "issue_detection": "issue_detection",
                "tenancy_faq": "tenancy_faq",
                "clarification": "router_clarification"
            }
        )
        
        workflow.add_edge("handle_emergency", "finalize_response")
        workflow.add_edge("issue_detection", "finalize_response")
        workflow.add_edge("tenancy_faq", "finalize_response")
        workflow.add_edge("router_clarification", "finalize_response")

        workflow.set_finish_point("finalize_response") 
        
        return workflow
    
    def _route_request(self, state: ConversationState) -> ConversationState:
        """Route the incoming request to appropriate agent."""
        
        agent_type, message, is_emergency = self.router_agent.route_request(
            user_text=state["user_text"],
            has_image=state["has_image"],
            location=state["user_location"],
            conversation_history=state["conversation_history"]
        )
        
        state["current_agent"] = agent_type.value if hasattr(agent_type, 'value') else str(agent_type)
        state["is_emergency"] = is_emergency
        state["agent_response"] = message
        
        if message: 
            state["messages"].append(AIMessage(content=f"[Router] {message}"))
        
        return state
    
    def _determine_next_step(self, state: ConversationState) -> Literal["emergency", "issue_detection", "tenancy_faq", "clarification"]:
        """Determine which node to execute next based on routing decision."""
        
        if state["is_emergency"]:
            return "emergency"
        elif state["current_agent"] == "issue_detection":
            return "issue_detection"
        elif state["current_agent"] == "tenancy_faq":
            return "tenancy_faq"
        else:
            return "clarification"
    
    def _handle_emergency(self, state: ConversationState) -> ConversationState:
        """Handle emergency situations with immediate response."""
        
        state["agent_response"] = EMERGENCY_RESPONSE
        state["confidence_score"] = 1.0
        state["follow_up_questions"] = [
            "Are you currently safe?",
            "Have you contacted emergency services?",
            "Do you need immediate evacuation guidance?"
        ]
        
        state["messages"].append(AIMessage(content=f"[Emergency] {EMERGENCY_RESPONSE}"))
        
        return state
    
    def _handle_issue_detection(self, state: ConversationState) -> ConversationState:
        """Handle property issue detection and analysis."""
        
        try:
            response = self.issue_agent.analyze_issue(
                user_text=state["user_text"],
                image=state["image_data"]
            )
            
            state["agent_response"] = response.message
            state["confidence_score"] = response.confidence
            state["follow_up_questions"] = response.follow_up_questions or []
            
            self.issue_agent.add_to_memory(state["user_text"], response.message)
            
            state["messages"].append(AIMessage(content=f"[Issue Detection] {response.message}"))
            
        except Exception as e:
            state["agent_response"] = f"Error analyzing property issue: {str(e)}"
            state["confidence_score"] = 0.3
            state["follow_up_questions"] = ["Could you provide more details about the issue?"]
            
            state["messages"].append(AIMessage(content=f"[Issue Detection Error] {state['agent_response']}"))
        
        return state
    
    def _handle_tenancy_faq(self, state: ConversationState) -> ConversationState:
        """Handle tenancy and legal questions."""
        
        try:
            response = self.faq_agent.answer_tenancy_question(
                question=state["user_text"],
                location=state["user_location"]
            )
            
            state["agent_response"] = response.message
            state["confidence_score"] = response.confidence
            state["follow_up_questions"] = response.follow_up_questions or []
            
            state["messages"].append(AIMessage(content=f"[Tenancy FAQ] {response.message}"))
            
        except Exception as e:
            state["agent_response"] = f"Error answering tenancy question: {str(e)}"
            state["confidence_score"] = 0.3
            state["follow_up_questions"] = ["Could you rephrase your question?"]
            
            state["messages"].append(AIMessage(content=f"[Tenancy FAQ Error] {state['agent_response']}"))
        
        return state
    
    def _handle_router_clarification(self, state: ConversationState) -> ConversationState:
        """Handle cases where router needs clarification."""
        
        state["confidence_score"] = 0.8
        state["follow_up_questions"] = [
            "Are you asking about property damage or maintenance issues?",
            "Or are you asking about tenancy laws and rental agreements?"
        ]
        
        return state
    
    def _finalize_response(self, state: ConversationState) -> ConversationState:
        """Finalize the response and update memory."""
        
        if hasattr(self.router_agent, 'add_to_memory'):
            self.router_agent.add_to_memory(
                user_message=state["user_text"],
                agent_response=state["agent_response"],
                agent_type=state["current_agent"]
            )
        
        if not state["agent_response"]:
            state["agent_response"] = "I encountered an issue processing your request. Please try again."
            state["confidence_score"] = 0.1
        
        return state
    
    def process_request(
        self,
        user_text: str,
        session_id: str,
        image: Optional[Image.Image] = None,
        location: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process a user request through the LangGraph workflow.
        
        Args:
            user_text: User's message
            session_id: Session identifier
            image: Optional image for analysis
            location: User's location
            conversation_history: Previous conversation messages
            
        Returns:
            Complete response with agent analysis
        """
        
        initial_state = ConversationState(
            messages=[HumanMessage(content=user_text)],
            user_text=user_text,
            user_location=location,
            has_image=image is not None,
            image_data=image,
            current_agent=None,
            agent_response="",
            confidence_score=0.0,
            is_emergency=False,
            follow_up_questions=[],
            session_id=session_id,
            conversation_history=conversation_history or []
        )
        
        final_state = self.app.invoke(initial_state)
        
        return {
            "agent_type": final_state["current_agent"],
            "message": final_state["agent_response"],
            "confidence": final_state["confidence_score"],
            "is_emergency": final_state["is_emergency"],
            "follow_up_questions": final_state["follow_up_questions"],
            "session_id": session_id,
            "conversation_messages": [
                {
                    "role": "human" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "agent_type": final_state["current_agent"]
                }
                for msg in final_state["messages"]
            ]
        } 