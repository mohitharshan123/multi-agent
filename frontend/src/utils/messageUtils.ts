import type { Message, ConversationHistoryItem } from '@/types'

export const prepareConversationHistory = (messages: Message[]): ConversationHistoryItem[] => {
  return messages.map(msg => ({
    role: msg.role,
    content: msg.content
  }))
}

export const createUserMessage = (content: string, uploadedImage: File | null = null): Message => {
  const message: Message = {
    id: Date.now().toString(),
    role: 'user',
    content,
    timestamp: new Date(),
    hasImage: !!uploadedImage
  }
  
  if (uploadedImage) {
    message.imageUrl = URL.createObjectURL(uploadedImage)
  }
  
  return message
}

export const createErrorMessage = (error: Error): Message => {
  return {
    id: `${Date.now().toString()}_error`,
    role: 'assistant',
    agentType: 'system',
    content: `Sorry, I encountered an error: ${error.message}. Please make sure the backend server is running and try again.`,
    timestamp: new Date(),
    confidence: 0.0
  }
}

export const createWelcomeMessage = (welcomeText: string): Message => {
  return {
    id: 'welcome',
    role: 'assistant',
    agentType: 'router',
    content: welcomeText,
    timestamp: new Date(),
    confidence: 1.0
  }
} 