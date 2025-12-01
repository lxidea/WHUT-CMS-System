'use client'

import { useEffect, useState } from 'react'
import { getNewsList } from '@/lib/api'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

interface SidebarProps {
  categories: string[]
  selectedCategory: string
  onCategoryChange: (category: string) => void
}

interface PopularNews {
  id: number
  title: string
  view_count: number
  published_at?: string
}

export default function Sidebar({ categories, selectedCategory, onCategoryChange }: SidebarProps) {
  const [popularNews, setPopularNews] = useState<PopularNews[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchPopularNews() {
      try {
        const data = await getNewsList({ page: 1, page_size: 5 })
        // Sort by view count to get most popular
        const sorted = [...data.items].sort((a, b) => b.view_count - a.view_count)
        setPopularNews(sorted.slice(0, 5))
      } catch (error) {
        console.error('Failed to fetch popular news:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchPopularNews()
  }, [])

  return (
    <aside className="space-y-6">
      {/* Categories */}
      <div className="bg-white rounded-xl shadow-soft p-6 border border-gray-100">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
          </svg>
          新闻分类
        </h3>
        <div className="space-y-2">
          <button
            onClick={() => onCategoryChange('')}
            className={`w-full text-left px-4 py-2.5 rounded-lg transition-all font-medium ${
              selectedCategory === ''
                ? 'bg-gradient-primary text-white shadow-sm'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            全部分类
          </button>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => onCategoryChange(category)}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition-all font-medium ${
                selectedCategory === category
                  ? 'bg-gradient-primary text-white shadow-sm'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Popular News */}
      <div className="bg-white rounded-xl shadow-soft p-6 border border-gray-100">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          热门新闻
        </h3>
        {loading ? (
          <div className="text-center py-4">
            <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-primary-600 border-r-transparent"></div>
          </div>
        ) : (
          <div className="space-y-3">
            {popularNews.map((news, index) => (
              <a
                key={news.id}
                href={`/news/${news.id}`}
                className="block group"
              >
                <div className="flex gap-3">
                  <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    index === 0
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white'
                      : index === 1
                      ? 'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
                      : index === 2
                      ? 'bg-gradient-to-r from-orange-400 to-orange-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {index + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2 mb-1">
                      {news.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>{news.view_count} 浏览</span>
                    </div>
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Quick Info */}
      <div className="bg-gradient-primary rounded-xl shadow-soft p-6 text-white">
        <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          关于系统
        </h3>
        <p className="text-sm text-white/90 leading-relaxed">
          武汉理工大学新闻管理系统自动爬取并整理学校官网新闻，为您提供最新的校园资讯。
        </p>
      </div>
    </aside>
  )
}
