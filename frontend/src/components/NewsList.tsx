'use client'

import { useState } from 'react'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { useAuth } from '@/contexts/AuthContext'
import { addBookmark, removeBookmark } from '@/lib/api'

dayjs.locale('zh-cn')

interface News {
  id: number
  title: string
  summary?: string
  category?: string
  publisher?: string
  department?: string
  published_at?: string
  view_count: number
  source_name: string
}

interface NewsListProps {
  news: News[]
  bookmarkedIds?: number[]
  onBookmarkChange?: () => void
}

export default function NewsList({ news, bookmarkedIds = [], onBookmarkChange }: NewsListProps) {
  const { user, token } = useAuth()
  const [loading, setLoading] = useState<number | null>(null)

  const handleBookmark = async (newsId: number, isBookmarked: boolean) => {
    if (!token) {
      alert('请先登录')
      return
    }

    setLoading(newsId)
    try {
      if (isBookmarked) {
        await removeBookmark(newsId, token)
      } else {
        await addBookmark(newsId, token)
      }
      onBookmarkChange?.()
    } catch (error: any) {
      alert(error.message || '操作失败')
    } finally {
      setLoading(null)
    }
  }

  if (news.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">暂无新闻</p>
      </div>
    )
  }

  return (
    <div className="relative pl-0 md:pl-12">
      {/* Animated Background Blobs for Glassmorphism */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob" />
      <div className="absolute top-40 right-1/4 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000" />
      <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-4000" />

      {/* Timeline Line - Hidden on mobile */}
      <div className="hidden md:block absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 to-pink-400 opacity-30" />

      <div className="relative space-y-8">
        {news.map((item, index) => {
          const isBookmarked = bookmarkedIds.includes(item.id)

          return (
            <div key={item.id} className="relative">
              {/* Timeline Dot - Hidden on mobile */}
              <div className="hidden md:block absolute -left-[2.6rem] top-8 w-5 h-5 rounded-full bg-white border-4 border-blue-500 shadow-lg z-10 animate-pulse-slow" />

              {/* Date Badge - Hidden on mobile */}
              <div className="hidden md:block absolute -left-[5.5rem] top-7 text-right">
                {item.published_at && (
                  <>
                    <div className="text-xs font-bold text-gray-700">
                      {dayjs(item.published_at).format('MM-DD')}
                    </div>
                    <div className="text-xs text-gray-500">
                      {dayjs(item.published_at).format('YYYY')}
                    </div>
                  </>
                )}
              </div>

              {/* Glassmorphism Card */}
              <article
                className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 p-6 border border-white/50 hover:bg-white/80 cursor-pointer md:ml-4 md:border-l-4 md:border-l-blue-500 animate-slide-up group"
                style={{ animationDelay: `${index * 100}ms` }}
                onClick={() => window.location.href = `/news/${item.id}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-3 flex-wrap">
                      {item.category && (
                        <span className="text-xs backdrop-blur-sm bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1.5 rounded-full font-semibold shadow-md">
                          {item.category}
                        </span>
                      )}
                      {item.publisher && (
                        <span className="text-xs backdrop-blur-sm bg-gradient-to-r from-green-500 to-teal-500 text-white px-3 py-1.5 rounded-full font-semibold shadow-md">
                          📢 {item.publisher}
                        </span>
                      )}
                      <span className="text-xs text-gray-600 flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
                        </svg>
                        {item.source_name}
                      </span>
                      {/* Mobile date display */}
                      {item.published_at && (
                        <span className="md:hidden text-xs text-gray-500 flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" />
                          </svg>
                          {dayjs(item.published_at).format('YYYY-MM-DD')}
                        </span>
                      )}
                    </div>

                    <h2 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
                      {item.title}
                    </h2>

                    {item.summary && (
                      <p className="text-gray-700 text-sm mb-4 line-clamp-2 leading-relaxed">
                        {item.summary}
                      </p>
                    )}

                    <div className="flex items-center gap-5 text-xs text-gray-600">
                      <span className="flex items-center gap-1.5">
                        <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                        </svg>
                        {item.view_count} 浏览
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-3 items-center">
                    {/* Decorative Icon */}
                    <div className="w-20 h-20 rounded-xl backdrop-blur-sm bg-gradient-to-br from-blue-400/20 to-purple-400/20 hidden lg:flex items-center justify-center flex-shrink-0 shadow-inner">
                      <svg className="w-10 h-10 text-blue-500/60" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
                      </svg>
                    </div>

                    {/* Bookmark Button */}
                    {user && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleBookmark(item.id, isBookmarked)
                        }}
                        disabled={loading === item.id}
                        className={`flex-shrink-0 p-3 rounded-full backdrop-blur-sm transition-all duration-200 ${
                          isBookmarked
                            ? 'text-yellow-500 hover:text-yellow-600 bg-yellow-100/80 hover:bg-yellow-200/80 shadow-md'
                            : 'text-gray-400 hover:text-blue-600 bg-white/50 hover:bg-blue-50/80'
                        } ${loading === item.id ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}`}
                        title={isBookmarked ? '取消收藏' : '收藏'}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5"
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
                </div>
              </article>
            </div>
          )
        })}
      </div>
    </div>
  )
}
