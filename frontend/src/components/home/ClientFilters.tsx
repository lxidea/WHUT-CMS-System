'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

interface ClientFiltersProps {
  categories: string[]
  sources: string[]
}

export default function ClientFilters({ categories, sources }: ClientFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  // Ensure arrays
  const categoryList = Array.isArray(categories) ? categories : []
  const sourceList = Array.isArray(sources) ? sources : []

  // Get current filter values from URL
  const currentSearch = searchParams.get('q') || ''
  const currentCategory = searchParams.get('category') || ''
  const currentSource = searchParams.get('source') || ''

  const [localSearch, setLocalSearch] = useState(currentSearch)
  const [showSourceDropdown, setShowSourceDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Sync local search with URL param
  useEffect(() => {
    setLocalSearch(currentSearch)
  }, [currentSearch])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowSourceDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Build URL with updated params
  const buildUrl = useCallback((updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams.toString())

    // Reset page when filters change
    if ('q' in updates || 'category' in updates || 'source' in updates) {
      params.delete('page')
    }

    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })

    return `/?${params.toString()}`
  }, [searchParams])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    router.push(buildUrl({ q: localSearch }))
  }

  const handleSearchClear = () => {
    setLocalSearch('')
    router.push(buildUrl({ q: '' }))
  }

  const handleCategoryChange = (category: string) => {
    router.push(buildUrl({ category }))
  }

  const handleSourceChange = (source: string) => {
    setShowSourceDropdown(false)
    router.push(buildUrl({ source }))
  }

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <form onSubmit={handleSearchSubmit} className="relative">
        <input
          type="text"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          placeholder="搜索新闻..."
          className="w-full px-4 py-3 pl-11 rounded-xl border border-white/10 bg-white/5 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
        />
        <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {localSearch && (
          <button
            type="button"
            onClick={handleSearchClear}
            className="absolute right-12 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg bg-primary-500/20 text-primary-600 dark:text-primary-400 hover:bg-primary-500/30 transition-colors text-sm font-medium"
        >
          搜索
        </button>
      </form>

      {/* Category Chips + Source Dropdown */}
      <div className="flex flex-wrap items-center gap-2">
        {/* All category chip */}
        <button
          onClick={() => handleCategoryChange('')}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
            currentCategory === ''
              ? 'bg-primary-500 text-white shadow-sm'
              : 'bg-white/5 border border-white/10 text-gray-600 dark:text-gray-300 hover:bg-white/10 hover:border-white/20'
          }`}
        >
          全部
        </button>

        {/* Category chips */}
        {categoryList.map((cat) => (
          <button
            key={cat}
            onClick={() => handleCategoryChange(cat)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
              currentCategory === cat
                ? 'bg-primary-500 text-white shadow-sm'
                : 'bg-white/5 border border-white/10 text-gray-600 dark:text-gray-300 hover:bg-white/10 hover:border-white/20'
            }`}
          >
            {cat}
          </button>
        ))}

        {/* Source dropdown */}
        {sourceList.length > 1 && (
          <div className="relative ml-auto" ref={dropdownRef}>
            <button
              onClick={() => setShowSourceDropdown(!showSourceDropdown)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                currentSource
                  ? 'bg-secondary-500 text-white shadow-sm'
                  : 'bg-white/5 border border-white/10 text-gray-600 dark:text-gray-300 hover:bg-white/10 hover:border-white/20'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
              {currentSource || '来源'}
              <svg className={`w-4 h-4 transition-transform ${showSourceDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showSourceDropdown && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-white/10 bg-surface-800/95 backdrop-blur-sm shadow-xl z-50 py-2">
                <button
                  onClick={() => handleSourceChange('')}
                  className={`w-full text-left px-4 py-2 text-sm transition-colors ${
                    currentSource === ''
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-gray-300 hover:bg-white/5'
                  }`}
                >
                  全部来源
                </button>
                {sourceList.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSourceChange(s)}
                    className={`w-full text-left px-4 py-2 text-sm transition-colors ${
                      currentSource === s
                        ? 'bg-primary-500/20 text-primary-400'
                        : 'text-gray-300 hover:bg-white/5'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Active filters indicator */}
      {(currentSearch || currentCategory || currentSource) && (
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <span>筛选:</span>
          {currentSearch && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 border border-white/10">
              &ldquo;{currentSearch}&rdquo;
              <button onClick={handleSearchClear} className="hover:text-red-400">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {currentCategory && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400">
              {currentCategory}
              <button onClick={() => handleCategoryChange('')} className="hover:text-red-400">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {currentSource && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary-500/10 border border-secondary-500/20 text-secondary-400">
              {currentSource}
              <button onClick={() => handleSourceChange('')} className="hover:text-red-400">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  )
}
