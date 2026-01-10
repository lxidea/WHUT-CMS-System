'use client'

import { useState } from 'react'
import { CalendarSummary } from '@/lib/types'
import MonthlyCalendar from '@/components/MonthlyCalendar'

type ViewMode = 'compact' | 'monthly'

interface CalendarPanelProps {
  calendarSummary: CalendarSummary | null
  loading?: boolean
}

export default function CalendarPanel({
  calendarSummary,
  loading = false,
}: CalendarPanelProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('compact')

  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="animate-pulse">
          <div className="h-6 bg-white/10 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-white/10 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-white/10 rounded w-2/3 mb-4"></div>
          <div className="h-20 bg-white/10 rounded"></div>
        </div>
      </div>
    )
  }

  if (!calendarSummary?.current_semester) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
          <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">暂无学期信息</p>
      </div>
    )
  }

  const { current_semester, current_week, upcoming_holidays, upcoming_exams } = calendarSummary

  if (viewMode === 'monthly') {
    return (
      <div>
        <div className="mb-4 flex justify-end">
          <button
            onClick={() => setViewMode('compact')}
            className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            紧凑视图
          </button>
        </div>
        <MonthlyCalendar />
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h3>
        <button
          onClick={() => setViewMode('monthly')}
          className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
          title="月历视图"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
        </button>
      </div>

      {/* Semester info */}
      <div className="mb-4">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{current_semester.name}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {current_semester.academic_year} 学年 第{current_semester.semester_number}学期
        </p>
      </div>

      {/* Current week highlight */}
      {current_week && (
        <div className="mb-4 bg-primary-500/10 rounded-xl p-4 border border-primary-500/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-primary-700 dark:text-primary-300">本周</span>
            <span className="bg-primary-500 text-white text-xs font-bold px-2.5 py-1 rounded-full">
              第 {current_week.week_number} 周
            </span>
          </div>
          <p className="text-xs text-primary-600 dark:text-primary-400">
            {formatDate(current_week.start_date)} - {formatDate(current_week.end_date)}
          </p>
          {current_week.notes && (
            <p className="text-xs text-primary-600 dark:text-primary-400 mt-1 italic">{current_week.notes}</p>
          )}
          <div className="flex gap-2 mt-2">
            {current_week.is_holiday && (
              <span className="bg-red-500/10 text-red-600 dark:text-red-400 text-xs px-2 py-0.5 rounded">假期</span>
            )}
            {current_week.is_exam_week && (
              <span className="bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 text-xs px-2 py-0.5 rounded">考试周</span>
            )}
          </div>
        </div>
      )}

      {/* Upcoming events */}
      {(upcoming_holidays.length > 0 || upcoming_exams.length > 0) && (
        <div className="space-y-3">
          {upcoming_holidays.slice(0, 2).map((holiday) => (
            <div key={holiday.id} className="flex items-center gap-3 text-sm">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-gray-600 dark:text-gray-300">
                第{holiday.week_number}周 {holiday.notes || '假期'}
              </span>
            </div>
          ))}
          {upcoming_exams.slice(0, 2).map((exam) => (
            <div key={exam.id} className="flex items-center gap-3 text-sm">
              <span className="w-2 h-2 rounded-full bg-yellow-500" />
              <span className="text-gray-600 dark:text-gray-300">
                第{exam.week_number}周 {exam.notes || '考试周'}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-white/10">
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
          数据来源: 武汉理工大学
        </p>
      </div>
    </div>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
