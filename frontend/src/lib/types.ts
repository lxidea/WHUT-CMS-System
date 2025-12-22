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

// Calendar types
export interface SemesterWeek {
  id: number
  semester_id: number
  week_number: number
  start_date: string
  end_date: string
  notes?: string
  is_holiday: boolean
  is_exam_week: boolean
  is_current: boolean
}

export interface Semester {
  id: number
  name: string
  academic_year: string
  semester_number: number
  start_date: string
  end_date: string
  is_current: boolean
  is_active: boolean
  current_week: number
  calendar_image_url?: string
  calendar_source_url?: string
  created_at: string
  updated_at?: string
}

export interface SemesterWithWeeks extends Semester {
  weeks: SemesterWeek[]
}

export interface CalendarSummary {
  current_semester: Semester | null
  current_week: SemesterWeek | null
  upcoming_holidays: SemesterWeek[]
  upcoming_exams: SemesterWeek[]
}
