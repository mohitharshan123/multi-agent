from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
import os
from models.schemas import AgentResponse, AgentType, TenancyQuery
from utils.prompts import (
    TENANCY_FAQ_SYSTEM_PROMPT,
    TENANCY_FAQ_LOCATION_PROMPT,
    TENANCY_FAQ_FOLLOWUPS
)
import random
import json

class TenancyFAQAgent:
    """
    LangChain-powered agent for handling tenancy laws, rental agreements, and landlord-tenant issues.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the tenancy FAQ agent with LangChain."""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=800,
            api_key=openai_api_key
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.faq_prompt = ChatPromptTemplate.from_messages([
            ("system", TENANCY_FAQ_SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        
        self.faq_chain = (
            self.faq_prompt 
            | self.llm 
            | StrOutputParser()
        )

    def answer_tenancy_question(self, question: str, location: Optional[str] = None, context: Optional[str] = None) -> AgentResponse:
        """
        Answer tenancy-related questions with location-specific guidance using LangChain.
        
        Args:
            question: User's tenancy question
            location: User's location for jurisdiction-specific advice  
            context: Additional context about the situation
            
        Returns:
            AgentResponse with legal guidance and recommendations
        """
        try:
            complete_question = f"Question: {question}"
            
            if context:
                complete_question += f"\nAdditional context: {context}"
            
            if location:
                complete_question += f"\nLocation: {location}"
                complete_question += f"\n\nPlease provide location-specific guidance for {location}."
            
            ai_response = self.faq_chain.invoke({"question": complete_question})
            
            ai_response += self._add_legal_disclaimer()
            
            follow_ups = self._generate_followup_questions(question, location)
            
            confidence = 0.8 if location else 0.6
            
            return AgentResponse(
                agent_type=AgentType.TENANCY_FAQ,
                message=ai_response,
                confidence=confidence,
                follow_up_questions=follow_ups
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=AgentType.TENANCY_FAQ,
                message=f"I apologize, but I encountered an error while processing your tenancy question: {str(e)}. Please try rephrasing your question.",
                confidence=0.3,
                follow_up_questions=["Could you rephrase your question?", "What specific tenancy issue are you facing?"]
            )
    
    def _add_legal_disclaimer(self) -> str:
        """Add legal disclaimer to responses."""
        return "\n\n---\n**⚖️ Legal Disclaimer:** This information is for general guidance only and should not be considered legal advice. Laws vary by jurisdiction and change over time. For specific legal situations, please consult with a qualified lawyer or local tenant rights organization."
    
    def _generate_followup_questions(self, question: str, location: Optional[str]) -> List[str]:
        """Generate relevant follow-up questions based on the query."""
        question_lower = question.lower()
        
        if not location:
            return ["What city or state/province are you located in for more specific guidance?"]
        
        follow_ups = []
        
        if "rent" in question_lower and "increase" in question_lower:
            follow_ups.extend([
                "What type of rental agreement do you have (month-to-month or fixed-term)?",
                "Have you received written notice of the rent increase?"
            ])
        elif "eviction" in question_lower:
            follow_ups.extend([
                "Have you received any formal eviction notices?",
                "Are you current on your rent payments?"
            ])
        elif "deposit" in question_lower:
            follow_ups.extend([
                "Do you have documentation of the property's condition when you moved in?",
                "How long has it been since you moved out?"
            ])
        elif "repair" in question_lower or "maintenance" in question_lower:
            follow_ups.extend([
                "Have you notified your landlord in writing about these issues?",
                "How long have these repair issues been ongoing?"
            ])
        else:
            follow_ups = random.sample(TENANCY_FAQ_FOLLOWUPS, 2)
        
        return follow_ups[:3]
    
    def get_jurisdiction_info(self, location: str) -> str:
        """Get specific jurisdiction information for a location."""
        try:
            jurisdiction_prompt = ChatPromptTemplate.from_messages([
                ("system", "Provide key tenancy law information for the specified jurisdiction, including typical notice periods, tenant protection agencies, and relevant housing authorities."),
                ("human", "Provide key tenancy law information for: {location}")
            ])
            
            jurisdiction_chain = jurisdiction_prompt | self.llm | StrOutputParser()
            
            response = jurisdiction_chain.invoke({"location": location})
            
            return response
            
        except Exception as e:
            return f"Unable to retrieve specific information for {location}. Please consult local housing authorities or tenant rights organizations."
    
    def add_to_memory(self, user_input: str, response: str):
        """Add interaction to LangChain memory."""
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response) 