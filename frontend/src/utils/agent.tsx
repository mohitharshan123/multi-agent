import { AlertTriangle, Bot, Navigation, Scale, Wrench } from 'lucide-react'
import { ReactElement } from 'react'

type AgentType = 'issue_detection' | 'tenancy_faq' | 'router' | 'system' | 'default'

const agentColorMap: Record<AgentType, string> = {
    'issue_detection': 'border-green-200 bg-green-50',
    'tenancy_faq': 'border-blue-200 bg-blue-50',
    'router': 'border-purple-200 bg-purple-50',
    'system': 'border-gray-200 bg-gray-50',
    'default': 'border-gray-200 bg-gray-50'
}

const agentIconMap: Record<AgentType, () => ReactElement> = {
    'issue_detection': () => <Wrench className="w-4 h-4 text-green-600" />,
    'tenancy_faq': () => <Scale className="w-4 h-4 text-blue-600" />,
    'router': () => <Navigation className="w-4 h-4 text-purple-600" />,
    'system': () => <AlertTriangle className="w-4 h-4 text-red-600" />,
    'default': () => <Bot className="w-4 h-4 text-gray-600" />
}

const agentNameMap: Record<AgentType, string> = {
    'issue_detection': 'Issue Detection Agent',
    'tenancy_faq': 'Tenancy FAQ Agent',
    'router': 'Smart Router',
    'system': 'System',
    'default': 'AI Assistant'
}

export const getAgentColor = (type: string | undefined): string => {
    const agentType = (type as AgentType) || 'default'
    return agentColorMap[agentType] || agentColorMap['default']
}

export const getAgentIcon = (agentType: string | undefined): ReactElement => {
    const type = (agentType as AgentType) || 'default'
    const iconFunction = agentIconMap[type] || agentIconMap['default']
    return iconFunction()
}

export const getAgentName = (agentType: string | undefined): string => {
    const type = (agentType as AgentType) || 'default'
    return agentNameMap[type] || agentNameMap['default']
}

export const formatTimestamp = (timestamp: Date | string): string => {
    return new Date(timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    })
}

export const formatContent = (content: string | undefined): string => {
    if (!content) {
        return ''
    }
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded text-sm">$1</code>')
        .replace(/\n/g, '<br/>')
}