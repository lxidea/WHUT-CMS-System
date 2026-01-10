'use client'

import Link from 'next/link'
import { NewsItem } from '@/lib/types'

interface TopNewsListProps {
  items: NewsItem[]
  loading?: boolean
}

export default function TopNewsList({ items, loading = false }: TopNewsListProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-5 w-5 bg-white/10 rounded animate-pulse" />
          <div className="h-5 w-20 bg-white/10 rounded animate-pulse" />
        </div>
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <div className="w-6 h-6 rounded-full bg-white/10" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-white/10 rounded w-full" />
                <div className="h-3 bg-white/10 rounded w-1/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" />
        </svg>
        热门资讯
      </h3>
      <div className="space-y-3">
        {items.slice(0, 6).map((news, index) => (
          <Link
            key={news.id}
            href={`/news/${news.id}`}
            className="group flex gap-3 items-start"
          >
            <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-transform group-hover:scale-110 ${
              index === 0
                ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white shadow-sm shadow-yellow-500/30'
                : index === 1
                ? 'bg-gradient-to-r from-gray-300 to-gray-400 text-white'
                : index === 2
                ? 'bg-gradient-to-r from-orange-300 to-orange-400 text-white'
                : 'bg-white/10 text-gray-500 dark:text-gray-400'
            }`}>
              {index + 1}
            </span>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium text-gray-800 dark:text-gray-200 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2 mb-1">
                {news.title}
              </h4>
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>{news.view_count}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
