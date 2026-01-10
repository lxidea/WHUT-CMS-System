'use client'

import { useRouter, useSearchParams } from 'next/navigation'

interface SourcesListProps {
  sources: string[]
  currentSource: string
}

export default function SourcesList({ sources, currentSource }: SourcesListProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  // Ensure array
  const sourceList = Array.isArray(sources) ? sources : []

  const handleSourceChange = (source: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.delete('page')

    if (source && source !== currentSource) {
      params.set('source', source)
    } else {
      params.delete('source')
    }

    router.push(`/?${params.toString()}`)
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-secondary-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1.581.814L10 14.229l-4.419 2.585A1 1 0 014 16V4z" clipRule="evenodd" />
        </svg>
        信息来源
      </h3>
      <div className="space-y-2">
        {sourceList.map((s) => (
          <button
            key={s}
            onClick={() => handleSourceChange(s)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              currentSource === s
                ? 'bg-secondary-500/20 text-secondary-600 dark:text-secondary-400 border border-secondary-500/30'
                : 'text-gray-600 dark:text-gray-400 hover:bg-white/5 border border-transparent'
            }`}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
