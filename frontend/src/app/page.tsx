'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { getNewsList, getCategories, getBookmarks } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import NewsList from '@/components/NewsList'
import Header from '@/components/Header'
import CategoryFilter from '@/components/CategoryFilter'
import SearchBar from '@/components/SearchBar'
import Sidebar from '@/components/Sidebar'
import Pagination from '@/components/Pagination'

function HomeContent() {
  const searchParams = useSearchParams()
  const { token } = useAuth()
  const [news, setNews] = useState([])
  const [categories, setCategories] = useState<string[]>([])
  const [bookmarkedIds, setBookmarkedIds] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 20

  // Handle URL query parameters
  useEffect(() => {
    const categoryParam = searchParams.get('category')
    if (categoryParam) {
      setSelectedCategory(categoryParam)
    }
  }, [searchParams])

  useEffect(() => {
    async function fetchCategories() {
      try {
        const data = await getCategories()
        setCategories(data.categories || [])
      } catch (error) {
        console.error('Failed to fetch categories:', error)
      }
    }
    fetchCategories()
  }, [])

  useEffect(() => {
    async function fetchBookmarks() {
      if (!token) {
        setBookmarkedIds([])
        return
      }
      try {
        const bookmarks = await getBookmarks(token)
        setBookmarkedIds(bookmarks.map((b: any) => b.id))
      } catch (error) {
        console.error('Failed to fetch bookmarks:', error)
      }
    }
    fetchBookmarks()
  }, [token])

  useEffect(() => {
    async function fetchNews() {
      setLoading(true)
      try {
        const params: any = { page, page_size: pageSize }
        if (selectedCategory) params.category = selectedCategory
        if (searchQuery) params.search = searchQuery

        const data = await getNewsList(params)
        setNews(data.items)
        setTotal(data.total)
      } catch (error) {
        console.error('Failed to fetch news:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [page, selectedCategory, searchQuery])

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setPage(1)
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setPage(1)
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-primary-50/20">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            最新资讯
          </h1>

          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} />
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Content - Left Column */}
          <div className="lg:col-span-8">
            {/* Mobile Category Filter */}
            <div className="lg:hidden mb-6">
              <CategoryFilter
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={handleCategoryChange}
              />
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
                <p className="mt-4 text-gray-600">加载中...</p>
              </div>
            ) : (
              <>
                <div className="mb-4 text-sm text-gray-600 font-medium">
                  共 {total} 条新闻
                  {selectedCategory && ` · 分类: ${selectedCategory}`}
                  {searchQuery && ` · 搜索: ${searchQuery}`}
                </div>
                <NewsList
                  news={news}
                  bookmarkedIds={bookmarkedIds}
                  onBookmarkChange={async () => {
                    if (token) {
                      const bookmarks = await getBookmarks(token)
                      setBookmarkedIds(bookmarks.map((b: any) => b.id))
                    }
                  }}
                />

                {totalPages > 1 && (
                  <Pagination
                    currentPage={page}
                    totalPages={totalPages}
                    onPageChange={setPage}
                  />
                )}
              </>
            )}
          </div>

          {/* Sidebar - Right Column */}
          <div className="lg:col-span-4">
            <div className="sticky top-24">
              <Sidebar
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={handleCategoryChange}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="text-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    }>
      <HomeContent />
    </Suspense>
  )
}
