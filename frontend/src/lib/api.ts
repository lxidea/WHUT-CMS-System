const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface NewsListParams {
  page?: number
  page_size?: number
  category?: string
  publisher?: string
  department?: string
  search?: string
  featured_only?: boolean
}

export async function getNewsList(params: NewsListParams = {}) {
  const queryParams = new URLSearchParams()

  if (params.page) queryParams.append('page', params.page.toString())
  if (params.page_size) queryParams.append('page_size', params.page_size.toString())
  if (params.category) queryParams.append('category', params.category)
  if (params.publisher) queryParams.append('publisher', params.publisher)
  if (params.department) queryParams.append('department', params.department)
  if (params.search) queryParams.append('search', params.search)
  if (params.featured_only) queryParams.append('featured_only', 'true')

  const response = await fetch(`${API_URL}/api/news/?${queryParams}`)

  if (!response.ok) {
    throw new Error('Failed to fetch news')
  }

  return response.json()
}

export async function getNewsById(id: number) {
  const response = await fetch(`${API_URL}/api/news/${id}`)

  if (!response.ok) {
    throw new Error('Failed to fetch news item')
  }

  return response.json()
}

export async function getCategories() {
  const response = await fetch(`${API_URL}/api/news/categories/list`)

  if (!response.ok) {
    throw new Error('Failed to fetch categories')
  }

  return response.json()
}

export async function getPublishers() {
  const response = await fetch(`${API_URL}/api/news/publishers/list`)

  if (!response.ok) {
    throw new Error('Failed to fetch publishers')
  }

  return response.json()
}

export async function getDepartments() {
  const response = await fetch(`${API_URL}/api/news/departments/list`)

  if (!response.ok) {
    throw new Error('Failed to fetch departments')
  }

  return response.json()
}

// Bookmark API functions
export async function addBookmark(newsId: number, token: string) {
  const response = await fetch(`${API_URL}/api/auth/bookmarks/${newsId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add bookmark')
  }

  return response.json()
}

export async function removeBookmark(newsId: number, token: string) {
  const response = await fetch(`${API_URL}/api/auth/bookmarks/${newsId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to remove bookmark')
  }

  return response.json()
}

export async function getBookmarks(token: string) {
  const response = await fetch(`${API_URL}/api/auth/bookmarks`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    throw new Error('Failed to fetch bookmarks')
  }

  return response.json()
}

// Calendar API functions
export async function getCalendarSummary() {
  const response = await fetch(`${API_URL}/api/calendar/summary`)

  if (!response.ok) {
    throw new Error('Failed to fetch calendar summary')
  }

  return response.json()
}

export async function getCurrentSemester() {
  const response = await fetch(`${API_URL}/api/calendar/semesters/current`)

  if (!response.ok) {
    throw new Error('Failed to fetch current semester')
  }

  return response.json()
}

export async function getSemesters() {
  const response = await fetch(`${API_URL}/api/calendar/semesters`)

  if (!response.ok) {
    throw new Error('Failed to fetch semesters')
  }

  return response.json()
}

export async function getMonthlyCalendar(year?: number, month?: number) {
  const params = new URLSearchParams()
  if (year) params.append('year', year.toString())
  if (month) params.append('month', month.toString())

  const response = await fetch(`${API_URL}/api/calendar/monthly?${params}`)

  if (!response.ok) {
    throw new Error('Failed to fetch monthly calendar')
  }

  return response.json()
}
