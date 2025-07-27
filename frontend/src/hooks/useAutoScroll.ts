import { useEffect, useRef, DependencyList } from 'react'

interface UseAutoScrollReturn {
  messagesEndRef: React.RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
}

export const useAutoScroll = (dependencies: DependencyList = []): UseAutoScrollReturn => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, dependencies)

  return {
    messagesEndRef,
    scrollToBottom
  }
} 