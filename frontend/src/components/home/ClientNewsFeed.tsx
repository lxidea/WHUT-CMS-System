'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { useAuth } from '@/contexts/AuthContext'
import { addBookmark, removeBookmark, getBookmarks } from '@/lib/api'
import { NewsItem } from '@/lib/types'

dayjs.locale('zh-cn')

interface ClientNewsFeedProps {
  items: NewsItem[]
}

export default function ClientNewsFeed({ items }: ClientNewsFeedProps) {
  const { user, token } = useAuth()
  const [bookmarkLoading, setBookmarkLoading] = useState<number | null>(null)
  const [bookmarkedIds, setBookmarkedIds] = useState<number[]>([])

  // Fetch bookmarks when token changes
  const fetchBookmarks = useCallback(async () => {
    if (!token) {
      setBookmarkedIds([])
      return
    }
    try {
      const bookmarks = await getBookmarks(token)
      setBookmarkedIds(bookmarks.map((b: any) => b.id))
    } catch (err) {
      console.error('Failed to fetch bookmarks:', err)
    }
  }, [token])

  useEffect(() => {
    fetchBookmarks()
  }, [fetchBookmarks])

  const handleBookmark = async (e: React.MouseEvent, newsId: number, isBookmarked: boolean) => {
    e.preventDefault()
    e.stopPropagation()

    if (!token) {
      alert('请先登录')
      return
    }

    setBookmarkLoading(newsId)
    try {
      if (isBookmarked) {
        await removeBookmark(newsId, token)
      } else {
        await addBookmark(newsId, token)
      }
      await fetchBookmarks()
    } catch (error: any) {
      alert(error.message || '操作失败')
    } finally {
      setBookmarkLoading(null)
    }
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-16 rounded-2xl border border-white/10 bg-white/5">
        <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
          <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-lg">暂无新闻</p>
        <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">稍后再来看看吧</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {items.map((item, index) => {
        const isBookmarked = bookmarkedIds.includes(item.id)

        return (
          <Link key={item.id} href={`/news/${item.id}`}>
            <article
              className="group rounded-2xl border border-white/10 bg-white/5 p-5 transition-all duration-300 hover:bg-white/[0.07] hover:border-white/20 cursor-pointer"
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <div className="flex items-start gap-4">
                {/* Left indicator */}
                <div className="flex-shrink-0 hidden sm:block">
                  <div className="w-1 h-12 rounded-full bg-gradient-to-b from-primary-400 to-secondary-500 dark:from-primary-500 dark:to-secondary-600 group-hover:h-16 transition-all duration-300" />
                </div>

                {/* Main Content */}
                <div className="flex-1 min-w-0">
                  {/* Top Row: Category & Date */}
                  <div className="flex items-center gap-3 mb-2 flex-wrap text-xs">
                    {item.category && (
                      <span className="text-primary-600 dark:text-primary-400 font-medium bg-primary-500/10 px-2.5 py-0.5 rounded-full">
                        {item.category}
                      </span>
                    )}
                    <span className="text-gray-400 dark:text-gray-500 flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {item.published_at ? dayjs(item.published_at).format('YYYY-MM-DD') : '未知日期'}
                    </span>
                    <span className="text-gray-400 dark:text-gray-500">
                      {item.source_name}
                    </span>
                  </div>

                  {/* Title */}
                  <h2 className="text-base md:text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
                    {item.title}
                  </h2>

                  {/* Summary */}
                  {item.summary && !item.summary.includes('[图片公告]') && (
                    <p className="text-gray-500 dark:text-gray-400 text-sm line-clamp-2 leading-relaxed mb-3">
                      {item.summary}
                    </p>
                  )}

                  {/* Bottom Row: Views */}
                  <div className="flex items-center gap-4 text-xs text-gray-400 dark:text-gray-500">
                    <span className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {item.view_count} 浏览
                    </span>
                  </div>
                </div>

                {/* Right: Bookmark & Arrow */}
                <div className="flex-shrink-0 flex flex-col items-center gap-2">
                  {user && (
                    <button
                      onClick={(e) => handleBookmark(e, item.id, isBookmarked)}
                      disabled={bookmarkLoading === item.id}
                      className={`p-2 rounded-full transition-all duration-200 ${
                        isBookmarked
                          ? 'text-yellow-500 bg-yellow-500/10'
                          : 'text-gray-400 dark:text-gray-600 hover:text-primary-500 dark:hover:text-primary-400 hover:bg-primary-500/10'
                      } ${bookmarkLoading === item.id ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}`}
                      title={isBookmarked ? '取消收藏' : '收藏'}
                    >
                      <svg
                        className="w-5 h-5"
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

                  {/* Arrow indicator */}
                  <div className="text-gray-400 dark:text-gray-600 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-all duration-200 group-hover:translate-x-1">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </article>
          </Link>
        )
      })}
    </div>
  )
}
