export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  agentType?: string;
  isEmergency?: boolean;
  confidence?: number;
  followUpQuestions?: string[];
  hasImage?: boolean;
  imageUrl?: string;
  image?: File;
  isError?: boolean;
}

export interface ConversationHistoryItem {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  agent_type: string;
  is_emergency: boolean;
  confidence: number;
  follow_up_questions: string[];
}

export interface UseChatProps {
  sessionId: string;
  location?: string;
  messages: Message[];
  addMessage: (message: Message) => void;
  addErrorMessage: (error: Error) => void;
  setUploadedImage: (image: File | null) => void;
}

export interface UseMessagesReturn {
  messages: Message[];
  addMessage: (message: Message) => void;
  addErrorMessage: (error: Error) => void;
  clearMessages: () => void;
}

export interface UseImageUploadReturn {
  uploadedImage: File | null;
  setUploadedImage: (image: File | null) => void;
  handleImageUpload: (acceptedFiles: File[]) => void;
}

export interface ChatInterfaceProps {
  className?: string;
}

export interface MessageBubbleProps {
  message: Message;
}

export interface HeaderProps {
  className?: string;
}

export interface TypingIndicatorProps {
  className?: string;
}

export type MessageRole = 'user' | 'assistant';
export type AgentType = string;

export interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
}

export interface ImportMeta {
  readonly env: ImportMetaEnv;
} 