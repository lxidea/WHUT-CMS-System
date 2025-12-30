'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getNewsById, getBookmarks, addBookmark, removeBookmark } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { NewsItem } from '@/lib/types'
import Header from '@/components/Header'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

export default function NewsDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user, token } = useAuth()
  const [news, setNews] = useState<NewsItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [bookmarkLoading, setBookmarkLoading] = useState(false)

  useEffect(() => {
    async function fetchNews() {
      try {
        const id = parseInt(params.id as string)
        if (isNaN(id)) {
          setError('无效的新闻 ID')
          setLoading(false)
          return
        }

        const data = await getNewsById(id)
        setNews(data)
      } catch (error) {
        console.error('Failed to fetch news:', error)
        setError('加载新闻失败')
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [params.id])

  useEffect(() => {
    async function checkBookmark() {
      if (!token || !news) return

      try {
        const bookmarks = await getBookmarks(token)
        setIsBookmarked(bookmarks.some((b: any) => b.id === news.id))
      } catch (error) {
        console.error('Failed to check bookmark status:', error)
      }
    }

    checkBookmark()
  }, [token, news])

  const handleBookmark = async () => {
    if (!token || !news) {
      alert('请先登录')
      return
    }

    setBookmarkLoading(true)
    try {
      if (isBookmarked) {
        await removeBookmark(news.id, token)
        setIsBookmarked(false)
      } else {
        await addBookmark(news.id, token)
        setIsBookmarked(true)
      }
    } catch (error: any) {
      alert(error.message || '操作失败')
    } finally {
      setBookmarkLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-16">
            <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary-500 border-r-transparent"></div>
            <p className="mt-4 text-gray-500 dark:text-gray-400">加载中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !news) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-16">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="text-red-600 dark:text-red-400 text-lg mb-4">{error || '新闻不存在'}</p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              返回首页
            </button>
          </div>
        </div>
      </div>
    )
  }

  const isImagePost = news.content.startsWith('[图片公告]')

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 transition-colors">
      <Header />
      <main className="container mx-auto px-4 py-8 animate-fade-in">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.back()}
            className="mb-6 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center gap-2 font-medium transition-all hover:gap-3 group"
          >
            <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回
          </button>

          <article className="bg-white dark:bg-surface-800 rounded-2xl shadow-soft dark:shadow-dark-soft hover:shadow-medium dark:hover:shadow-dark-medium transition-shadow p-6 md:p-10 border border-gray-100 dark:border-surface-700 animate-slide-up">
            {/* Header */}
            <header className="mb-8 pb-8 border-b border-gray-100 dark:border-surface-700">
              <div className="flex items-start justify-between mb-6 gap-4">
                <div className="flex items-center gap-3 flex-wrap">
                  {news.category && (
                    <span className="text-sm bg-gradient-mixed text-white px-4 py-1.5 rounded-full font-medium shadow-sm">
                      {news.category}
                    </span>
                  )}
                  {isImagePost && (
                    <span className="text-sm bg-gradient-to-r from-yellow-400 to-orange-400 text-white px-4 py-1.5 rounded-full font-medium shadow-sm">
                      图片公告
                    </span>
                  )}
                </div>

                {user && (
                  <button
                    onClick={handleBookmark}
                    disabled={bookmarkLoading}
                    className={`flex-shrink-0 p-3 rounded-full transition-all duration-200 ${
                      isBookmarked
                        ? 'text-yellow-500 hover:text-yellow-600 bg-yellow-50 dark:bg-yellow-500/10 hover:bg-yellow-100 dark:hover:bg-yellow-500/20 shadow-sm'
                        : 'text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-500/10'
                    } ${bookmarkLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}`}
                    title={isBookmarked ? '取消收藏' : '收藏'}
                  >
                    <svg
                      className="h-6 w-6"
                      fill={isBookmarked ? 'currentColor' : 'none'}
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                      />
                    </svg>
                  </button>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6 leading-tight">
                {news.title}
              </h1>

              <div className="flex flex-wrap gap-4 md:gap-6 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="font-medium">{dayjs(news.published_at || news.created_at).format('YYYY年MM月DD日')}</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span className="font-medium">{news.view_count} 浏览</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                  <span className="font-medium">{news.source_name}</span>
                </div>
              </div>
            </header>

            {/* Content */}
            <div className="prose prose-lg dark:prose-invert max-w-none">
              {isImagePost ? (
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-l-4 border-yellow-400 p-5 mb-8 rounded-r-lg">
                  <div className="flex gap-3">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-yellow-800 dark:text-yellow-300 font-medium">
                        这是一条图片公告，原文包含图片内容。
                      </p>
                    </div>
                  </div>
                </div>
              ) : null}

              <div className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap text-base">
                {news.content}
              </div>
            </div>

            {/* Footer */}
            <footer className="mt-10 pt-8 border-t border-gray-100 dark:border-surface-700">
              <a
                href={news.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-mixed text-white rounded-xl hover:opacity-90 transition-all shadow-md hover:shadow-lg font-medium"
              >
                <span>查看原文</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </footer>
          </article>
        </div>
      </main>
    </div>
  )
}
