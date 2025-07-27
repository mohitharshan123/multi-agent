import { Bot, Building2, Shield } from 'lucide-react'
import { FC } from 'react'

interface HeaderProps {
  className?: string
}

const Header: FC<HeaderProps> = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl">
              <Building2 className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Multi-Agent Real Estate Assistant
              </h1>
              <p className="text-gray-600 text-sm">
                Property Issues • Tenancy Laws • Emergency Detection • Image Analysis
              </p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-gray-700">
              <Bot className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium">Specialized Agents</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <Shield className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium">Emergency Detection</span>
            </div>
          </div>
        </div>
        
        <div className="mt-4 flex items-center space-x-4 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>System Online</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>AI Models Ready</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>Multi-Modal Support</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 