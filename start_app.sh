#!/bin/bash

echo "🏠 Multi-Agent Real Estate Assistant - LangGraph Implementation"
echo "=============================================================="

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set."
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

echo "✅ OpenAI API key configured"

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

cd "$(dirname "$0")"
source venv/bin/activate

# Start LangChain/LangGraph backend server
echo "🚀 Starting LangGraph Backend (LangChain + LangGraph)..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend development server
echo "🌐 Starting React frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ LangGraph application started successfully!"
echo ""
echo "🔗 Access Points:"
echo "   🖥️  Frontend:              http://localhost:5173"
echo "   🚀 LangGraph Backend:      http://localhost:8000"
echo "      • API Docs:             http://localhost:8000/docs"
echo "      • Health Check:         http://localhost:8000/api/health"
echo "      • Workflow Graph:       http://localhost:8000/api/workflow/graph"
echo "      • Agent Status:         http://localhost:8000/api/agents/status"
echo ""
echo "🎯 LangGraph Features:"
echo "   • State-based workflow management"
echo "   • Advanced conversation memory"
echo "   • Tool integration framework"
echo "   • Visual workflow monitoring"
echo "   • Production-ready error handling"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for processes
wait 