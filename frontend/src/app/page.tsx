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
import HeroSection from '@/components/HeroSection'

function HomeContent() {
  const searchParams = useSearchParams()
  const { token } = useAuth()
  const [news, setNews] = useState([])
  const [featuredNews, setFeaturedNews] = useState([])
  const [categories, setCategories] = useState<string[]>([])
  const [bookmarkedIds, setBookmarkedIds] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedSource, setSelectedSource] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 12

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

  // Fetch featured news for hero section
  useEffect(() => {
    async function fetchFeaturedNews() {
      try {
        // Get latest news with images for the hero section
        const data = await getNewsList({ page: 1, page_size: 5 })
        // Filter to get items with images preferably
        const withImages = data.items.filter((item: any) => item.images && item.images.length > 0)
        const featured = withImages.length >= 3 ? withImages.slice(0, 5) : data.items.slice(0, 5)
        setFeaturedNews(featured)
      } catch (error) {
        console.error('Failed to fetch featured news:', error)
      }
    }
    fetchFeaturedNews()
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
        if (selectedSource) params.source_name = selectedSource
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
  }, [page, selectedCategory, selectedSource, searchQuery])

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setPage(1)
  }

  const handleSourceChange = (source: string) => {
    setSelectedSource(source)
    setPage(1)
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setPage(1)
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 transition-colors">
      <Header />
      <main className="container mx-auto px-4 py-6">
        {/* Hero Section */}
        {!selectedCategory && !searchQuery && page === 1 && featuredNews.length > 0 && (
          <HeroSection featuredNews={featuredNews} />
        )}

        {/* Search and Filter Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} />
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

            {/* Results Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {selectedCategory || searchQuery ? '搜索结果' : '最新资讯'}
              </h2>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                共 {total} 条
                {selectedCategory && ` · ${selectedCategory}`}
                {searchQuery && ` · "${searchQuery}"`}
              </span>
            </div>

            {loading ? (
              <div className="text-center py-16">
                <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary-500 border-r-transparent"></div>
                <p className="mt-4 text-gray-500 dark:text-gray-400">加载中...</p>
              </div>
            ) : (
              <>
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
            <div className="sticky top-20">
              <Sidebar
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={handleCategoryChange}
                selectedSource={selectedSource}
                onSourceChange={handleSourceChange}
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
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
        <Header />
        <div className="text-center py-16">
          <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary-500 border-r-transparent"></div>
          <p className="mt-4 text-gray-500 dark:text-gray-400">加载中...</p>
        </div>
      </div>
    }>
      <HomeContent />
    </Suspense>
  )
}
