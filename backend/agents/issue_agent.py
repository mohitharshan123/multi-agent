from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage,
    ToolMessage
)
from langchain.memory import ConversationBufferMemory
from PIL import Image
import base64
import json
import random

from models.schemas import AgentResponse, AgentType
from utils.image_utils import (
    preprocess_image, 
    enhance_image_for_analysis, 
    detect_image_issues, 
    encode_image_for_openai
)
from utils.prompts import (
    ISSUE_DETECTION_SYSTEM_PROMPT,
    ISSUE_DETECTION_IMAGE_PROMPT,
    ISSUE_DETECTION_FOLLOWUPS
)


@tool
def analyze_property_image(image_data: str, user_description: str) -> Dict[str, Any]:
    """
    Analyze property image for potential issues using computer vision.
    
    Args:
        image_data: Base64 encoded image data
        user_description: User's description of what they're concerned about
        
    Returns:
        Analysis results with detected issues and confidence scores
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image
        import base64
        import io
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        processed_image = preprocess_image(image)
        enhanced_image = enhance_image_for_analysis(processed_image)
        cv_issues = detect_image_issues(enhanced_image)
        
        return {
            "tool_name": "analyze_property_image",
            "darkness_detected": cv_issues.get("darkness", False),
            "blur_detected": cv_issues.get("blur", False),
            "cracks_detected": cv_issues.get("cracks_detected", False),
            "moisture_indicators": cv_issues.get("moisture_indicators", False),
            "user_concern": user_description,
            "analysis_confidence": 0.85,
            "recommendations": [
                f"Analysis focused on: {user_description}",
                "Image quality assessment completed",
                "Computer vision preprocessing applied"
            ]
        }
    except Exception as e:
        return {
            "tool_name": "analyze_property_image",
            "error": str(e),
            "analysis_confidence": 0.0,
            "recommendations": ["Unable to process image", "Please try with a different image"]
        }


@tool
def assess_issue_severity(issue_description: str, visible_indicators: List[str]) -> Dict[str, Any]:
    """
    Assess the severity level of a property issue based on description and indicators.
    
    Args:
        issue_description: Description of the property issue
        visible_indicators: List of visible signs or indicators
        
    Returns:
        Severity assessment and recommended actions
    """
    high_severity = ["structural", "electrical", "gas", "flood", "fire", "collapse"]
    medium_severity = ["leak", "crack", "mold", "damage", "malfunction"]
    low_severity = ["wear", "maintenance", "cosmetic", "minor"]
    
    description_lower = issue_description.lower()
    
    if any(keyword in description_lower for keyword in high_severity):
        severity = "high"
        urgency = "immediate"
    elif any(keyword in description_lower for keyword in medium_severity):
        severity = "medium"
        urgency = "within_days"
    else:
        severity = "low"
        urgency = "within_weeks"
    
    return {
        "tool_name": "assess_issue_severity",
        "severity_level": severity,
        "urgency_timeline": urgency,
        "priority_score": {"high": 9, "medium": 6, "low": 3}[severity],
        "recommended_actions": [
            f"Priority level: {severity.upper()}",
            f"Recommended timeline: {urgency}",
            "Document the issue with photos",
            "Consider professional assessment" if severity != "low" else "Monitor for changes"
        ]
    }


class LangChainIssueDetectionAgent:
    """
    Modern LangChain-based issue detection agent with advanced tool integration.
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize the modern issue detection agent."""
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            max_tokens=800,
            api_key=openai_api_key
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.tools = [
            analyze_property_image,
            assess_issue_severity
        ]
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", ISSUE_DETECTION_SYSTEM_PROMPT),
            ("human", "{input}")
        ])
        
        self.analysis_chain = (
            self.analysis_prompt 
            | self.llm 
            | StrOutputParser()
        )
    
    def analyze_issue(
        self, 
        user_text: str, 
        image: Optional[Image.Image] = None
    ) -> AgentResponse:
        """
        Analyze property issue using LangChain with optional image.
        
        Args:
            user_text: User's description of the issue
            image: Optional PIL image for visual analysis
            
        Returns:
            AgentResponse with analysis and recommendations
        """
        if image:
            return self._analyze_with_image(user_text, image)
        else:
            return self._analyze_text_only(user_text)
    
    def clear_memory(self):
        """Clear conversation memory for fresh analysis."""
        self.memory.clear()
    
    def _analyze_with_image(self, user_text: str, image: Image.Image) -> AgentResponse:
        """Analyze issue with image using LangChain Vision API."""
        
        processed_image = preprocess_image(image)
        enhanced_image = enhance_image_for_analysis(processed_image)
        
        cv_issues = detect_image_issues(enhanced_image)
        
        encoded_image = encode_image_for_openai(enhanced_image)
        
        vision_prompt = self._format_image_analysis_input(user_text, cv_issues)
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": ISSUE_DETECTION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            response = self.llm.invoke(messages)
            ai_analysis = response.content if hasattr(response, 'content') else str(response)
            
            additional_notes = []
            if cv_issues["darkness"]:
                additional_notes.append("**Additional Note:** Image appears dark - better lighting recommended for accurate analysis.")
            
            if cv_issues["blur"]:
                additional_notes.append("**Additional Note:** Image appears blurry - clearer photos would help with diagnosis.")
            
            if additional_notes:
                ai_analysis += "\n\n" + "\n\n".join(additional_notes)
            
            follow_ups = random.sample(ISSUE_DETECTION_FOLLOWUPS, 2)
            
            return AgentResponse(
                agent_type=AgentType.ISSUE_DETECTION,
                message=ai_analysis,
                confidence=0.85,
                follow_up_questions=follow_ups
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=AgentType.ISSUE_DETECTION,
                message=f"Error analyzing image: {str(e)}. Please try again or provide a text description.",
                confidence=0.3,
                follow_up_questions=["Could you describe the issue in more detail?"]
            )
    
    def _analyze_text_only(self, user_text: str) -> AgentResponse:
        """Analyze issue using only text with LangChain."""
        
        analysis_input = f"""User describes this property issue: {user_text}

Please provide detailed analysis and recommendations based on the description. 
Note: No image was provided, so ask for more details if needed for accurate diagnosis."""
        
        try:
            ai_analysis = self.analysis_chain.invoke({"input": analysis_input})
            
            ai_analysis += "\n\n**💡 Tip:** For more accurate diagnosis, consider uploading a photo of the issue."
            
            follow_ups = random.sample(ISSUE_DETECTION_FOLLOWUPS, 3)
            
            return AgentResponse(
                agent_type=AgentType.ISSUE_DETECTION,
                message=ai_analysis,
                confidence=0.65,  # Lower confidence without image
                follow_up_questions=follow_ups
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=AgentType.ISSUE_DETECTION,
                message=f"Error analyzing issue: {str(e)}. Please provide more details about the problem.",
                confidence=0.3,
                follow_up_questions=["Can you describe the issue in more detail?"]
            )
    
    def _format_image_analysis_input(self, user_text: str, cv_issues: Dict[str, bool]) -> str:
        """Format input for image analysis using existing prompt template."""
        
        cv_context = []
        if cv_issues.get("darkness", False):
            cv_context.append("Computer vision detected: Image is very dark")
        if cv_issues.get("blur", False):
            cv_context.append("Computer vision detected: Image appears very blurry")
        if cv_issues.get("cracks_detected", False):
            cv_context.append("Computer vision detected: Linear crack-like patterns identified")
        
        enhanced_user_text = user_text or "No additional context provided"
        
        if cv_context:
            enhanced_user_text += f"\n\nComputer Vision Notes: {' | '.join(cv_context)}"
        
        return ISSUE_DETECTION_IMAGE_PROMPT.format(user_text=enhanced_user_text)
    
    def add_to_memory(self, user_input: str, analysis_result: str):
        """Add interaction to LangChain memory."""
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(analysis_result) 