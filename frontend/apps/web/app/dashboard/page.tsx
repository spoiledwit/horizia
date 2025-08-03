import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'
import { authOptions } from '@/lib/auth'
import { DynamicDashboard } from '@/components/dynamic-dashboard'
import { AskPulseChat } from '@/components/ask-pulse-chat'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard - Horizia'
}

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="fixed inset-0 overflow-hidden">
      <div className="h-full flex flex-col bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 flex-shrink-0">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">Horizia</h1>
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium">{session.user?.username || 'User'}</span>
              <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-medium">
                {session.user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 flex-shrink-0 flex flex-col">
          <div className="p-4 space-y-2 flex-1">
            <a href="/dashboard" className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg flex items-center gap-3 hover:bg-blue-700 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Dashboard
            </a>
            <a href="/integrations" className="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg flex items-center gap-3 hover:bg-gray-200 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              Integrations
            </a>
          </div>
          <div className="p-4 border-t border-gray-200">
            <form action="/api/auth/signout" method="POST">
              <button type="submit" className="w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-3 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </form>
          </div>
        </aside>

        {/* Main Content - Dynamic Dashboard */}
        <DynamicDashboard />
      </div>
      
      {/* Ask Pulse Chat */}
      <AskPulseChat />
      </div>
    </div>
  )
}