import { FC } from 'react'
import ChatInterface from '@/components/ChatInterface'
import Header from '@/components/Header'

const App: FC = () => {
  const sessionId = `session_${Math.random().toString(36).slice(2, 11)}`

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <ChatInterface sessionId={sessionId} />
      </div>
    </div>
  )
}

export default App
