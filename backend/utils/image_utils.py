import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import Tuple, Optional

def preprocess_image(image: Image.Image, max_size: Tuple[int, int] = (1024, 1024)) -> Image.Image:
    """
    Preprocess image for AI analysis by resizing and optimizing.
    
    Args:
        image: PIL Image object
        max_size: Maximum dimensions (width, height)
    
    Returns:
        Preprocessed PIL Image
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    return image

def enhance_image_for_analysis(image: Image.Image) -> Image.Image:
    """
    Enhance image quality for better issue detection.
    
    Args:
        image: PIL Image object
    
    Returns:
        Enhanced PIL Image
    """
    # Convert PIL to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    
    lab = cv2.merge((l_channel, a, b))
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Convert back to PIL
    enhanced_pil = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    
    return enhanced_pil

def encode_image_for_openai(image: Image.Image) -> str:
    """
    Encode image to base64 string for OpenAI API.
    
    Args:
        image: PIL Image object
    
    Returns:
        Base64 encoded string
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded_string

def detect_image_issues(image: Image.Image) -> dict:
    """
    Basic computer vision analysis to detect obvious issues.
    
    Args:
        image: PIL Image object
    
    Returns:
        Dictionary with detected issues
    """
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    issues = {
        "darkness": False,
        "blur": False,
        "moisture_indicators": False,
        "cracks_detected": False
    }
    
    # Check for darkness
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    issues["darkness"] = mean_brightness < 50
    
    # Check for blur
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
   
    if laplacian_var > 1:       
        issues["blur"] = laplacian_var < 100
    else:
        issues["blur"] = False
    
    edges = cv2.Canny(gray, 50, 150)
    
    # Use Hough Line Transform to detect actual lines (potential cracks)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)
    
    edge_density = np.sum(edges > 0) / edges.size
    
    if lines is not None and len(lines) > 3 and edge_density < 0.15:
        # Additional check: lines should be somewhat vertical or horizontal (typical crack patterns)
        linear_cracks = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calculate angle
            angle = np.arctan2(abs(y2 - y1), abs(x2 - x1)) * 180 / np.pi
            # Count lines that are roughly vertical (0-30° or 60-90°) or horizontal (80-90°)
            if angle < 30 or angle > 60:
                linear_cracks += 1
        
        issues["cracks_detected"] = linear_cracks > 2
    else:
        issues["cracks_detected"] = False
    
    return issues 