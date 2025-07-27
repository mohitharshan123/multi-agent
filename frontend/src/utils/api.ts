import { Message, ConversationHistoryItem } from '@/types'

const getBackendUrl = (): string => {
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
}

const createAssistantMessage = (data: any): Message => ({
  id: Date.now().toString(),
  content: data.message,
  role: 'assistant',
  timestamp: new Date(),
  agentType: data.agent_type,
  confidence: data.confidence,
  isEmergency: data.is_emergency,
  followUpQuestions: data.follow_up_questions
})

const buildFormData = (
  userMessage: Message,
  uploadedImage: File | null,
  location: string | undefined,
  sessionId: string,
  conversationHistory: ConversationHistoryItem[]
): FormData => {
  const formData = new FormData()
  formData.append('message', userMessage.content)
  formData.append('location', location || '')
  formData.append('session_id', sessionId)
  formData.append('conversation_history', JSON.stringify(conversationHistory))
  
  if (uploadedImage) {
    formData.append('file', uploadedImage)
  }
  
  return formData
}

export const sendMessage = async (
  userMessage: Message,
  location: string | undefined,
  sessionId: string,
  conversationHistory: ConversationHistoryItem[],
  uploadedImage?: File | null
): Promise<Message> => {
  const formData = buildFormData(userMessage, uploadedImage || null, location, sessionId, conversationHistory)

  const response = await fetch(`${getBackendUrl()}/api/chat`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const data = await response.json()
  return createAssistantMessage(data)
} 