import { Suspense } from 'react'
import Header from '@/components/Header'
import {
  FeaturedNews,
  TopNewsList,
  CalendarPanel,
  ClientFilters,
  ClientPagination,
  ClientNewsFeed,
  SourcesList,
} from '@/components/home'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SearchParams {
  q?: string
  category?: string
  source?: string
  page?: string
}

interface HomePageProps {
  searchParams: Promise<SearchParams>
}

async function fetchHomeData(searchParams: SearchParams) {
  const search = searchParams.q || ''
  const category = searchParams.category || ''
  const source = searchParams.source || ''
  const page = parseInt(searchParams.page || '1', 10)
  const pageSize = 12

  // Build query params for news list
  const newsParams = new URLSearchParams()
  newsParams.append('page', page.toString())
  newsParams.append('page_size', pageSize.toString())
  if (search) newsParams.append('search', search)
  if (category) newsParams.append('category', category)
  if (source) newsParams.append('source_name', source)

  // Fetch all data in parallel
  const [newsRes, categoriesRes, sourcesRes, calendarRes, featuredRes, popularRes] = await Promise.all([
    fetch(`${API_URL}/api/news/?${newsParams}`, { next: { revalidate: 60 } }),
    fetch(`${API_URL}/api/news/categories/list`, { next: { revalidate: 300 } }),
    fetch(`${API_URL}/api/news/sources/list`, { next: { revalidate: 300 } }),
    fetch(`${API_URL}/api/calendar/summary`, { next: { revalidate: 300 } }).catch(() => null),
    fetch(`${API_URL}/api/news/?featured_only=true&page_size=4`, { next: { revalidate: 120 } }),
    fetch(`${API_URL}/api/news/?page_size=6`, { next: { revalidate: 120 } }), // Popular - will use view_count sort when available
  ])

  const [newsData, categories, sources, calendarSummary, featuredData, popularData] = await Promise.all([
    newsRes.ok ? newsRes.json() : { items: [], total: 0 },
    categoriesRes.ok ? categoriesRes.json() : [],
    sourcesRes.ok ? sourcesRes.json() : [],
    calendarRes?.ok ? calendarRes.json() : null,
    featuredRes.ok ? featuredRes.json() : { items: [] },
    popularRes.ok ? popularRes.json() : { items: [] },
  ])

  return {
    newsItems: newsData.items || [],
    total: newsData.total || 0,
    categories: categories || [],
    sources: sources || [],
    calendarSummary,
    featuredItems: featuredData.items || [],
    popularItems: popularData.items || [],
    search,
    category,
    source,
    page,
    pageSize,
  }
}

function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <Header />
      <main className="container mx-auto px-4 py-6">
        {/* Hero skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
          <div className="md:col-span-8">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-8 h-[320px] animate-pulse">
              <div className="h-5 w-20 bg-white/10 rounded-full mb-4" />
              <div className="h-8 bg-white/10 rounded w-3/4 mb-3" />
              <div className="h-4 bg-white/10 rounded w-full mb-2" />
              <div className="h-4 bg-white/10 rounded w-2/3" />
            </div>
          </div>
          <div className="md:col-span-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 animate-pulse">
              <div className="h-5 w-24 bg-white/10 rounded mb-4" />
              <div className="space-y-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="flex gap-3">
                    <div className="w-6 h-6 rounded-full bg-white/10" />
                    <div className="flex-1">
                      <div className="h-4 bg-white/10 rounded w-full mb-1" />
                      <div className="h-3 bg-white/10 rounded w-1/3" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Filter skeleton */}
        <div className="mb-6">
          <div className="h-12 bg-white/5 border border-white/10 rounded-xl mb-4 animate-pulse" />
          <div className="flex gap-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-8 w-16 bg-white/5 border border-white/10 rounded-full animate-pulse" />
            ))}
          </div>
        </div>

        {/* Content skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          <div className="md:col-span-8 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-white/10 bg-white/5 p-5 animate-pulse">
                <div className="flex gap-4">
                  <div className="w-1 h-12 rounded-full bg-white/10" />
                  <div className="flex-1 space-y-2">
                    <div className="flex gap-2">
                      <div className="h-5 w-16 bg-white/10 rounded-full" />
                      <div className="h-5 w-24 bg-white/10 rounded" />
                    </div>
                    <div className="h-5 bg-white/10 rounded w-3/4" />
                    <div className="h-4 bg-white/10 rounded w-full" />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="md:col-span-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 animate-pulse">
              <div className="h-5 w-24 bg-white/10 rounded mb-4" />
              <div className="space-y-2">
                <div className="h-4 bg-white/10 rounded w-full" />
                <div className="h-4 bg-white/10 rounded w-2/3" />
                <div className="h-20 bg-white/10 rounded mt-4" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

async function HomeContent({ searchParams }: { searchParams: SearchParams }) {
  const data = await fetchHomeData(searchParams)
  const {
    newsItems,
    total,
    categories,
    sources,
    calendarSummary,
    featuredItems,
    popularItems,
    search,
    category,
    source,
    page,
    pageSize,
  } = data

  const totalPages = Math.ceil(total / pageSize)
  const showHero = !category && !search && page === 1

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 transition-colors">
      <Header />
      <main className="container mx-auto px-4 py-6">
        {/* Top Block: Featured + Top News */}
        {showHero && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
            {/* Featured Hero - Left */}
            <div className="md:col-span-8">
              <FeaturedNews items={featuredItems} />
            </div>

            {/* Top/Hot News - Right */}
            <div className="md:col-span-4">
              <TopNewsList items={popularItems} loading={false} />
            </div>
          </div>
        )}

        {/* Controls Row: Search + Category Chips + Source Dropdown */}
        <div className="mb-6">
          <ClientFilters categories={categories} sources={sources} />
        </div>

        {/* Main Block: News Feed + Calendar Sidebar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* News Feed - Left */}
          <div className="md:col-span-8">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {category || search ? '搜索结果' : '最新资讯'}
              </h2>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                共 {total} 条
              </span>
            </div>

            <ClientNewsFeed items={newsItems} />

            {totalPages > 1 && (
              <div className="mt-6">
                <ClientPagination currentPage={page} totalPages={totalPages} />
              </div>
            )}
          </div>

          {/* Calendar + Sources - Right */}
          <div className="md:col-span-4">
            <div className="sticky top-20 space-y-6">
              <CalendarPanel
                calendarSummary={calendarSummary}
                loading={false}
              />

              {/* Sources list (if many sources) */}
              {Array.isArray(sources) && sources.length > 2 && (
                <SourcesList sources={sources} currentSource={source} />
              )}

              {/* Quick Info */}
              <div className="rounded-2xl bg-gradient-to-br from-primary-500/20 to-secondary-500/20 border border-white/10 p-5">
                <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  关于系统
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  武汉理工大学新闻管理系统自动爬取并整理学校官网新闻，为您提供最新的校园资讯。
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default async function Home({ searchParams }: HomePageProps) {
  const params = await searchParams
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <HomeContent searchParams={params} />
    </Suspense>
  )
}
