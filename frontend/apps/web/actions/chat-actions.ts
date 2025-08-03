'use server'

import { getApiClient } from '@/lib/api'
import { authOptions } from '@/lib/auth'
import { getServerSession } from 'next-auth'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatResponse {
  success: boolean
  response?: string
  function_calls?: number
  error?: string
}

export async function sendChatMessage(
  message: string,
  conversationHistory: ChatMessage[] = []
): Promise<ChatResponse> {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session) {
      return {
        success: false,
        error: 'Authentication required'
      }
    }

    const apiClient = await getApiClient(session)

    const response = await apiClient.chat.chatMessageCreate({
      message,
      conversation_history: conversationHistory
    })

    return {
      success: true,
      response: response.response,
      function_calls: response.function_calls
    }
  } catch (error: any) {
    console.error('Error sending chat message:', error)
    
    // Try to extract error message from API response
    let errorMessage = 'Failed to send message'
    if (error?.body?.error) {
      errorMessage = error.body.error
    } else if (error?.message) {
      errorMessage = error.message
    }

    return {
      success: false,
      error: errorMessage
    }
  }
}