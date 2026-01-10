'use client'

import { useRouter, useSearchParams } from 'next/navigation'

interface ClientPaginationProps {
  currentPage: number
  totalPages: number
}

export default function ClientPagination({ currentPage, totalPages }: ClientPaginationProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  if (totalPages <= 1) return null

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString())
    if (page > 1) {
      params.set('page', page.toString())
    } else {
      params.delete('page')
    }
    router.push(`/?${params.toString()}`)
  }

  // Calculate visible page numbers
  const getVisiblePages = () => {
    const delta = 2
    const range = []
    const rangeWithDots = []

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
        range.push(i)
      }
    }

    let prev = 0
    for (const i of range) {
      if (prev && i - prev !== 1) {
        rangeWithDots.push(-1) // -1 represents dots
      }
      rangeWithDots.push(i)
      prev = i
    }

    return rangeWithDots
  }

  const visiblePages = getVisiblePages()

  return (
    <nav className="flex items-center justify-center gap-1">
      {/* Previous button */}
      <button
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`p-2 rounded-lg transition-all ${
          currentPage === 1
            ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'text-gray-600 dark:text-gray-400 hover:bg-white/10 hover:text-primary-500'
        }`}
        aria-label="上一页"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Page numbers */}
      {visiblePages.map((pageNum, index) => (
        pageNum === -1 ? (
          <span key={`dots-${index}`} className="px-2 text-gray-400 dark:text-gray-600">
            ...
          </span>
        ) : (
          <button
            key={pageNum}
            onClick={() => handlePageChange(pageNum)}
            className={`min-w-[40px] h-10 rounded-lg font-medium transition-all ${
              pageNum === currentPage
                ? 'bg-primary-500 text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:bg-white/10'
            }`}
          >
            {pageNum}
          </button>
        )
      ))}

      {/* Next button */}
      <button
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={`p-2 rounded-lg transition-all ${
          currentPage === totalPages
            ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'text-gray-600 dark:text-gray-400 hover:bg-white/10 hover:text-primary-500'
        }`}
        aria-label="下一页"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </nav>
  )
}
