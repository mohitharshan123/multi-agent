#!/usr/bin/env python3
"""
Visualize the LangGraph Real Estate Multi-Agent Workflow
"""

import os
import tempfile
import subprocess
import platform

os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-visualization'

try:
    from agents.langgraph_workflow import RealEstateWorkflow
    
    def open_image(file_path: str):
        """Open image """
        subprocess.run(["open", file_path])
    
    def visualize_workflow():
        """Create and visualize the LangGraph workflow"""
        workflow = RealEstateWorkflow('sk-test-key-for-visualization')
        graph = workflow.app.get_graph()
        
        graph_image = graph.draw_mermaid_png()
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(graph_image)
            tmp_path = tmp.name
        
        open_image(tmp_path)
        return workflow, graph
    
    if __name__ == "__main__":
        workflow, graph = visualize_workflow()

except ImportError as e:
    print(f"Import error: {e}")

except Exception as e:
    print(f"Error: {e}")

