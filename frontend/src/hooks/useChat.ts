import { UseChatProps } from '@/types'
import { sendMessage } from '@/utils/api'
import { createUserMessage, prepareConversationHistory } from '@/utils/messageUtils'
import { useState } from 'react'

interface UseChatReturn {
  isLoading: boolean
  sendMessage: (inputMessage: string, uploadedImage?: File | null) => Promise<void>
}

export const useChat = ({ 
  sessionId, 
  location, 
  messages, 
  addMessage, 
  addErrorMessage, 
  setUploadedImage 
}: UseChatProps): UseChatReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const sendChatMessage = async (inputMessage: string, uploadedImage?: File | null): Promise<void> => {
    if (!inputMessage.trim() && !uploadedImage) return

    const userMessage = createUserMessage(inputMessage, uploadedImage || null)
    addMessage(userMessage)
    setIsLoading(true)

    try {
      const conversationHistory = prepareConversationHistory(messages)
      
      const assistantMessage = await sendMessage(
        userMessage,
        location,
        sessionId,
        conversationHistory,
        uploadedImage
      )
      
      addMessage(assistantMessage)
    } catch (error) {
      console.error('Error sending message:', error)
      addErrorMessage(error as Error)
    } finally {
      setIsLoading(false)
      setUploadedImage(null)
    }
  }

  return {
    isLoading,
    sendMessage: sendChatMessage
  }
} 