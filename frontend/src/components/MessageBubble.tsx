import type { Message } from '@/types'
import { formatContent, formatTimestamp, getAgentColor, getAgentIcon, getAgentName } from '@/utils/agent'
import classNames from 'classnames'
import { Clock, User } from 'lucide-react'
import { FC } from 'react'

interface MessageBubbleProps {
  message: Message
}

const MessageBubble: FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end items-start space-x-2 animate-slide-up">
        <div className="max-w-xs lg:max-w-md">
          {(message.image || message.imageUrl) && (
            <div className="mb-2">
              <img
                src={message.imageUrl || URL.createObjectURL(message.image!)}
                alt="Uploaded image"
                className="max-w-full h-32 object-cover rounded-lg border"
              />
            </div>
          )}

          {message.content && (
              <div className="bg-blue-600 text-white p-3 rounded-lg rounded-br-sm">
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            </div>
          )}
          
          
          <div className="flex items-center justify-end space-x-1 mt-1">
            <Clock className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-500">
              {formatTimestamp(message.timestamp)}
            </span>
          </div>
        </div>
        
        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <User className="w-4 h-4 text-blue-600" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start items-start space-x-3 animate-slide-up">
      <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
        {getAgentIcon(message.agentType)}
      </div>
      
      <div className="max-w-xs lg:max-w-lg">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs font-medium text-gray-700">
            {getAgentName(message.agentType)}
          </span>
          {message.confidence !== undefined && (
            <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
              {Math.round(message.confidence * 100)}% confident
            </span>
          )}
          {message.isEmergency && (
            <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">
              Emergency
            </span>
          )}

        </div>
        
        <div className={classNames(
          'p-3 rounded-lg rounded-bl-sm',
          {
            'bg-red-50 border border-red-200': message.isError,
            'bg-red-50 border border-red-300': message.isEmergency && !message.isError,
            [getAgentColor(message.agentType)]: !message.isError && !message.isEmergency,
          }
        )}>
          <div 
            className="text-sm text-gray-800 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
          />
        </div>
        
        {(message.followUpQuestions && message.followUpQuestions.length > 0) && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-medium text-gray-600">Follow-up questions:</p>
            {message.followUpQuestions.map((question, index) => (
              <div 
                key={index}
                className="text-xs bg-blue-50 border border-blue-200 rounded-lg p-2 text-blue-800"
              >
                {index + 1}. {question}
              </div>
            ))}
          </div>
        )}
        
        <div className="flex items-center space-x-1 mt-1">
          <Clock className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-500">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble 