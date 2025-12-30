'use client'

import { useState } from 'react'
import Link from 'next/link'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

interface FeaturedNews {
  id: number
  title: string
  summary?: string
  category?: string
  published_at?: string
  source_name: string
}

interface HeroSectionProps {
  featuredNews: FeaturedNews[]
}

export default function HeroSection({ featuredNews }: HeroSectionProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  if (featuredNews.length === 0) {
    return null
  }

  // Take top 5 news for featured section
  const displayNews = featuredNews.slice(0, 5)
  const mainNews = displayNews[0]
  const sideNews = displayNews.slice(1, 5)

  return (
    <div className="mb-8">
      {/* Section Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-6 bg-gradient-to-b from-primary-500 to-secondary-500 rounded-full" />
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          Latest News
        </h2>
        <div className="flex-1 h-px bg-gradient-to-r from-gray-200 dark:from-gray-700 to-transparent" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Featured Article */}
        <div className="lg:col-span-2">
          <Link href={`/news/${mainNews.id}`}>
            <article
              className="group relative p-6 md:p-8 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-600 dark:from-primary-600 dark:to-secondary-700 text-white overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-[1.01] cursor-pointer h-full min-h-[280px] flex flex-col justify-end"
              onMouseEnter={() => setHoveredIndex(0)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Decorative Elements */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />

              {/* Content */}
              <div className="relative z-10">
                {mainNews.category && (
                  <span className="inline-block text-xs bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full font-medium mb-4">
                    {mainNews.category}
                  </span>
                )}

                <h3 className="text-2xl md:text-3xl font-bold mb-4 leading-tight group-hover:text-white/90 transition-colors line-clamp-3">
                  {mainNews.title}
                </h3>

                {mainNews.summary && (
                  <p className="text-white/80 text-sm md:text-base mb-4 line-clamp-2">
                    {mainNews.summary.replace('[图片公告] 详见附图', '').trim() || mainNews.title}
                  </p>
                )}

                <div className="flex items-center gap-3 text-white/60 text-sm">
                  <span>{mainNews.source_name}</span>
                  {mainNews.published_at && (
                    <>
                      <span className="w-1 h-1 rounded-full bg-white/40" />
                      <span>{dayjs(mainNews.published_at).format('MM月DD日')}</span>
                    </>
                  )}
                </div>
              </div>

              {/* Hover Arrow */}
              <div className={`absolute bottom-6 right-6 p-3 rounded-full bg-white/10 backdrop-blur-sm transition-all duration-300 ${hoveredIndex === 0 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2'}`}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </article>
          </Link>
        </div>

        {/* Side News List */}
        <div className="lg:col-span-1 flex flex-col gap-3">
          {sideNews.map((news, index) => (
            <Link key={news.id} href={`/news/${news.id}`}>
              <article
                className="group p-4 rounded-xl bg-white dark:bg-surface-800 border border-gray-100 dark:border-surface-700 hover:border-primary-200 dark:hover:border-primary-700 hover:shadow-md transition-all duration-200 cursor-pointer"
                onMouseEnter={() => setHoveredIndex(index + 1)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <div className="flex items-start gap-3">
                  {/* Number Badge */}
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                      {index + 2}
                    </span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-800 dark:text-gray-200 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2 mb-1">
                      {news.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                      {news.category && (
                        <>
                          <span className="text-primary-500 dark:text-primary-400">{news.category}</span>
                          <span className="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600" />
                        </>
                      )}
                      {news.published_at && (
                        <span>{dayjs(news.published_at).format('MM-DD')}</span>
                      )}
                    </div>
                  </div>

                  {/* Hover Arrow */}
                  <div className={`flex-shrink-0 transition-all duration-200 ${hoveredIndex === index + 1 ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-1'}`}>
                    <svg className="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
