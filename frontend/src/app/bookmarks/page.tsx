'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { getBookmarks } from '@/lib/api'
import NewsList from '@/components/NewsList'
import Header from '@/components/Header'

export default function BookmarksPage() {
  const { user, token, isLoading } = useAuth()
  const router = useRouter()
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    async function fetchBookmarks() {
      if (!token) return

      setLoading(true)
      try {
        const bookmarks = await getBookmarks(token)
        setNews(bookmarks)
      } catch (error) {
        console.error('Failed to fetch bookmarks:', error)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchBookmarks()
    }
  }, [token])

  const handleBookmarkChange = async () => {
    if (!token) return
    try {
      const bookmarks = await getBookmarks(token)
      setNews(bookmarks)
    } catch (error) {
      console.error('Failed to refresh bookmarks:', error)
    }
  }

  if (isLoading || loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        </div>
      </>
    )
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              我的收藏
            </h1>
            <p className="text-gray-600">
              共 {news.length} 条收藏
            </p>
          </div>

          {news.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-sm">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">暂无收藏</h3>
              <p className="mt-1 text-sm text-gray-500">
                浏览新闻时点击星标图标添加收藏
              </p>
              <div className="mt-6">
                <button
                  onClick={() => router.push('/')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                >
                  浏览新闻
                </button>
              </div>
            </div>
          ) : (
            <NewsList
              news={news}
              bookmarkedIds={news.map((n: any) => n.id)}
              onBookmarkChange={handleBookmarkChange}
            />
          )}
        </div>
      </div>
    </>
  )
}
