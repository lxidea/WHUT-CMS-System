'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCategories, getNewsList } from '@/lib/api'
import Header from '@/components/Header'

interface CategoryStats {
  category: string
  count: number
  latest?: string
}

export default function CategoriesPage() {
  const router = useRouter()
  const [categories, setCategories] = useState<string[]>([])
  const [stats, setStats] = useState<CategoryStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const categoriesData = await getCategories()
        const cats = categoriesData.categories || []
        setCategories(cats)

        // Fetch count for each category
        const statsPromises = cats.map(async (category) => {
          const data = await getNewsList({ category, page: 1, page_size: 1 })
          return {
            category,
            count: data.total,
            latest: data.items[0]?.title
          }
        })

        const categoryStats = await Promise.all(statsPromises)
        setStats(categoryStats)
      } catch (error) {
        console.error('Failed to fetch categories:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleCategoryClick = (category: string) => {
    router.push(`/?category=${encodeURIComponent(category)}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            新闻分类
          </h1>
          <p className="text-gray-600 mb-8">
            浏览所有新闻分类，点击分类查看相关新闻
          </p>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
              <p className="mt-4 text-gray-600">加载中...</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {stats.map((stat) => (
                <div
                  key={stat.category}
                  onClick={() => handleCategoryClick(stat.category)}
                  className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 cursor-pointer border border-gray-200 hover:border-blue-500"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                      {stat.category}
                    </h2>
                    <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                      {stat.count} 篇
                    </span>
                  </div>

                  {stat.latest && (
                    <div className="text-sm text-gray-600">
                      <p className="text-gray-500 mb-1">最新文章：</p>
                      <p className="line-clamp-2">{stat.latest}</p>
                    </div>
                  )}

                  <div className="mt-4 flex items-center text-blue-600 text-sm font-medium">
                    <span>查看全部</span>
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              关于分类
            </h3>
            <p className="text-gray-700 text-sm">
              本系统自动从武汉理工大学官网采集新闻，并按照以下分类进行整理：
            </p>
            <ul className="mt-3 space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span><strong>部门亮点资讯</strong>：各部门工作动态和成果展示</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span><strong>学校通知·公告</strong>：学校层面的重要通知和公告</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span><strong>学院·所·中心通知公告</strong>：各学院、研究所、中心的通知</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span><strong>学术讲座·报告·论坛</strong>：学术活动和讲座信息</span>
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}
