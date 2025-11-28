// Type definitions for API responses

export interface NewsItem {
  id: number
  title: string
  content: string
  summary?: string
  source_url: string
  source_name: string
  published_at?: string
  author?: string
  images: string[]
  attachments: Array<{
    name: string
    url: string
  }>
  category?: string
  tags: string[]
  is_published: boolean
  is_featured: boolean
  view_count: number
  created_at: string
  updated_at?: string
}

export interface NewsListResponse {
  total: number
  items: NewsItem[]
  page: number
  page_size: number
}

export interface CategoryResponse {
  categories: string[]
}
