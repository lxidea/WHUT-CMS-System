'use client'

import { useEffect, useState } from 'react'
import { getNewsList } from '@/lib/api'
import NewsList from '@/components/NewsList'
import Header from '@/components/Header'

export default function Home() {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchNews() {
      try {
        const data = await getNewsList({ page: 1, page_size: 20 })
        setNews(data.items)
      } catch (error) {
        console.error('Failed to fetch news:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          最新资讯
        </h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-500 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        ) : (
          <NewsList news={news} />
        )}
      </main>
    </div>
  )
}
