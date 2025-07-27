import { Bot } from 'lucide-react'
import { FC } from 'react'

interface TypingIndicatorProps {
  className?: string
}

const TypingIndicator: FC<TypingIndicatorProps> = () => {
  return (
    <div className="flex justify-start items-start space-x-3 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
        <Bot className="w-4 h-4 text-gray-600" />
      </div>
      
      <div className="max-w-xs lg:max-w-lg">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs font-medium text-gray-700">
            AI Assistant
          </span>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
            Analyzing...
          </span>
        </div>
        
        <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg rounded-bl-sm">
          <div className="flex items-center space-x-1">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-xs text-gray-500 ml-2">AI is thinking...</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator 