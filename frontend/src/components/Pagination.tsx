interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  // Generate array of page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    const maxVisiblePages = 7 // Maximum number of page buttons to show

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Always show first page
      pages.push(1)

      if (currentPage <= 3) {
        // Near the start: show 1, 2, 3, 4, ..., last
        for (let i = 2; i <= 4; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        // Near the end: show 1, ..., last-3, last-2, last-1, last
        pages.push('...')
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // In the middle: show 1, ..., current-1, current, current+1, ..., last
        pages.push('...')
        pages.push(currentPage - 1)
        pages.push(currentPage)
        pages.push(currentPage + 1)
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const pageNumbers = getPageNumbers()

  return (
    <div className="mt-8 flex justify-center items-center gap-2 flex-wrap">
      {/* First Page Button */}
      {totalPages > 1 && currentPage !== 1 && (
        <button
          onClick={() => onPageChange(1)}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/70 border border-white/50 hover:bg-white/90 hover:shadow-md font-medium transition-all duration-200 text-gray-700"
          title="首页 (1)"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      )}

      {/* Previous Button */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/70 border border-white/50 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/90 hover:shadow-md font-medium transition-all duration-200 text-gray-700"
        title="上一页"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Page Numbers */}
      {pageNumbers.map((page, index) => {
        if (page === '...') {
          return (
            <span
              key={`ellipsis-${index}`}
              className="px-3 py-2 text-gray-500 font-medium"
            >
              ...
            </span>
          )
        }

        const pageNum = page as number
        const isActive = pageNum === currentPage

        return (
          <button
            key={pageNum}
            onClick={() => onPageChange(pageNum)}
            className={`min-w-[40px] px-4 py-2 rounded-lg backdrop-blur-sm font-medium transition-all duration-200 ${
              isActive
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg scale-105 border border-blue-400'
                : 'bg-white/70 border border-white/50 text-gray-700 hover:bg-white/90 hover:shadow-md hover:scale-105'
            }`}
          >
            {pageNum}
          </button>
        )
      })}

      {/* Next Button */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/70 border border-white/50 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/90 hover:shadow-md font-medium transition-all duration-200 text-gray-700"
        title="下一页"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Last Page Button */}
      {totalPages > 1 && currentPage !== totalPages && (
        <button
          onClick={() => onPageChange(totalPages)}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/70 border border-white/50 hover:bg-white/90 hover:shadow-md font-medium transition-all duration-200 text-gray-700"
          title={`末页 (${totalPages})`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        </button>
      )}
    </div>
  )
}
