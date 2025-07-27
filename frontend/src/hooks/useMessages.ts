import { WELCOME_MESSAGE } from '@/constants'
import type { Message } from '@/types'
import { createErrorMessage, createWelcomeMessage } from '@/utils/messageUtils'
import { useEffect, useState } from 'react'

interface UseMessagesReturn {
  messages: Message[]
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
  addMessage: (message: Message) => void
  addErrorMessage: (error: Error) => void
}

export const useMessages = (): UseMessagesReturn => {
  const [messages, setMessages] = useState<Message[]>([])

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([createWelcomeMessage(WELCOME_MESSAGE)])
    }
  }, [messages.length])

  const addMessage = (message: Message): void => {
    setMessages(prev => [...prev, message])
  }

  const addErrorMessage = (error: Error): void => {
    setMessages(prev => [...prev, createErrorMessage(error)])
  }

  return {
    messages,
    setMessages,
    addMessage,
    addErrorMessage
  }
} 