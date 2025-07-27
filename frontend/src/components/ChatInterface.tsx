import { useAutoScroll, useChat, useImageUpload, useMessages } from '@/hooks'
import classNames from 'classnames'
import { Image as ImageIcon, MapPin, Send, Upload, X } from 'lucide-react'
import { FC, useState } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

interface ChatInterfaceProps {
  sessionId: string
}

const ChatInterface: FC<ChatInterfaceProps> = ({ sessionId }) => {
  const [inputMessage, setInputMessage] = useState('')
  const [location, setLocation] = useState('')

  const { messages, addMessage, addErrorMessage } = useMessages()
  const { 
    uploadedImage, 
    setUploadedImage, 
    removeImage, 
    getRootProps, 
    getInputProps, 
    isDragActive 
  } = useImageUpload()
  
  const { isLoading, sendMessage } = useChat({
    sessionId,
    location,
    messages,
    addMessage,
    addErrorMessage,
    setUploadedImage
  })

  const { messagesEndRef } = useAutoScroll([messages])

  const handleSendMessage = () => {
    sendMessage(inputMessage, uploadedImage)
    setInputMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[calc(100vh-200px)] flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">💬 Chat Assistant</h2>
        <div className="flex items-center space-x-2">
          <MapPin className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Your location (optional)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-2 py-1 w-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>

      {uploadedImage && (
        <div className="mx-4 mb-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ImageIcon className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-blue-900">{uploadedImage.name}</p>
                <p className="text-xs text-blue-600">
                  {(uploadedImage.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeImage}
              className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-3">
          <div
            {...getRootProps()}
            className={classNames(
              'flex-shrink-0 w-12 h-12 border-2 border-dashed rounded-lg flex items-center justify-center cursor-pointer transition-colors',
              {
                'border-blue-400 bg-blue-50': isDragActive,
                'border-gray-300 hover:border-gray-400': !isDragActive,
              }
            )}
          >
            <input {...getInputProps()} />
            <Upload className="w-5 h-5 text-gray-400" />
          </div>

          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Describe your property issue or ask a tenancy question..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              disabled={isLoading}
            />
          </div>

          <button
            onClick={handleSendMessage}
            disabled={(!inputMessage.trim() && !uploadedImage) || isLoading}
            className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-2">
          💡 Tip: Upload images for visual analysis or ask about tenancy laws. The backend intelligently routes your requests to the appropriate agent.
        </p>
      </div>
    </div>
  )
}

export default ChatInterface 