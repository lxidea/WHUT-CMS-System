'use client'

import { useState } from 'react'
import Link from 'next/link'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { NewsItem } from '@/lib/types'

dayjs.locale('zh-cn')

interface FeaturedNewsProps {
  items: NewsItem[]
}

export default function FeaturedNews({ items }: FeaturedNewsProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  if (items.length === 0) {
    return null
  }

  const mainItem = items[activeIndex] || items[0]
  const highlights = items.slice(0, 4)

  return (
    <div className="space-y-4">
      {/* Hero Card */}
      <Link href={`/news/${mainItem.id}`}>
        <article className="group relative rounded-2xl border border-white/10 bg-white/5 overflow-hidden transition-all duration-300 hover:bg-white/[0.07] hover:border-white/20 cursor-pointer">
          <div className="p-6 md:p-8 min-h-[260px] flex flex-col justify-end relative">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 to-secondary-600/20 dark:from-primary-500/10 dark:to-secondary-500/10" />

            {/* Decorative circles */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-primary-500/5 rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-secondary-500/5 rounded-full translate-y-1/2 -translate-x-1/2" />

            <div className="relative z-10">
              {mainItem.category && (
                <span className="inline-block text-xs bg-white/10 backdrop-blur-sm px-3 py-1 rounded-full font-medium mb-3 text-gray-200 dark:text-gray-300">
                  {mainItem.category}
                </span>
              )}

              <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3 leading-tight group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-3">
                {mainItem.title}
              </h2>

              {mainItem.summary && (
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                  {mainItem.summary.replace('[图片公告] 详见附图', '').trim() || mainItem.title}
                </p>
              )}

              <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                <span>{mainItem.source_name}</span>
                {mainItem.published_at && (
                  <>
                    <span className="w-1 h-1 rounded-full bg-gray-400 dark:bg-gray-600" />
                    <span>{dayjs(mainItem.published_at).format('MM月DD日')}</span>
                  </>
                )}
              </div>
            </div>

            {/* Arrow */}
            <div className="absolute bottom-6 right-6 p-2.5 rounded-full bg-white/10 backdrop-blur-sm opacity-0 group-hover:opacity-100 translate-x-2 group-hover:translate-x-0 transition-all duration-300">
              <svg className="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </div>
        </article>
      </Link>

      {/* Mini highlights (3 items) */}
      {highlights.length > 1 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {highlights.slice(1, 4).map((item, index) => (
            <Link key={item.id} href={`/news/${item.id}`}>
              <article
                className={`group p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
                  activeIndex === index + 1
                    ? 'border-primary-500/50 bg-primary-500/5'
                    : 'border-white/10 bg-white/5 hover:bg-white/[0.07] hover:border-white/20'
                }`}
                onMouseEnter={() => setActiveIndex(index + 1)}
              >
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500/20 to-secondary-500/20 flex items-center justify-center text-xs font-bold text-primary-600 dark:text-primary-400">
                    {index + 2}
                  </span>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
                      {item.title}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {item.category || item.source_name}
                    </p>
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
