'use client'

import { useState } from 'react'
import { CalendarSummary } from '@/lib/types'
import MonthlyCalendar from './MonthlyCalendar'

type ViewMode = 'compact' | 'monthly'

interface CalendarSidebarProps {
  calendarSummary: CalendarSummary | null
  calendarMonthly?: any
  loading?: boolean
  error?: string | null
}

export default function CalendarSidebar({
  calendarSummary,
  calendarMonthly,
  loading = false,
  error = null,
}: CalendarSidebarProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('compact')

  if (loading) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-xl shadow-soft dark:shadow-dark-soft p-5 border border-gray-100 dark:border-surface-700">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-surface-700 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-surface-700 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-surface-700 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (error || !calendarSummary?.current_semester) {
    return (
      <div className="bg-white dark:bg-surface-800 rounded-xl shadow-soft dark:shadow-dark-soft p-5 border border-gray-100 dark:border-surface-700">
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          {error || '暂无学期信息'}
        </p>
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
            切换到紧凑视图
          </button>
        </div>
        <MonthlyCalendar />
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-surface-800 rounded-xl shadow-soft dark:shadow-dark-soft p-5 border border-gray-100 dark:border-surface-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center">
          <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h2>
        <button
          onClick={() => setViewMode('monthly')}
          className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
          title="切换到月历视图"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
        </button>
      </div>

      <div className="mb-5">
        <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1.5 uppercase tracking-wide">当前学期</h3>
        <p className="text-base font-bold text-gray-900 dark:text-gray-100">{current_semester.name}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          {current_semester.academic_year} 学年 第{current_semester.semester_number}学期
        </p>
      </div>

      {current_week ? (
        <div className="mb-5 bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-primary-800 dark:text-primary-300">本周</h3>
            <span className="bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-full">
              第 {current_week.week_number} 周
            </span>
          </div>
          <p className="text-sm text-primary-700 dark:text-primary-300">
            {formatDate(current_week.start_date)} - {formatDate(current_week.end_date)}
          </p>
          {current_week.notes && (
            <p className="text-sm text-primary-600 dark:text-primary-400 mt-2 italic">{current_week.notes}</p>
          )}
          {current_week.is_holiday && (
            <span className="inline-block mt-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs px-2 py-1 rounded">
              假期
            </span>
          )}
          {current_week.is_exam_week && (
            <span className="inline-block mt-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs px-2 py-1 rounded">
              考试周
            </span>
          )}
        </div>
      ) : (
        <div className="mb-5">
          <p className="text-sm text-gray-500 dark:text-gray-400">学期尚未开始或已结束</p>
        </div>
      )}

      {upcoming_holidays.length > 0 && (
        <div className="mb-5">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2.5 flex items-center uppercase tracking-wide">
            <svg className="w-4 h-4 mr-1.5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
            即将到来的假期
          </h3>
          <div className="space-y-2">
            {upcoming_holidays.map((holiday) => (
              <div key={holiday.id} className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-red-800 dark:text-red-300">第 {holiday.week_number} 周</span>
                  <span className="text-xs text-red-600 dark:text-red-400">
                    {formatDate(holiday.start_date)}
                  </span>
                </div>
                {holiday.notes && (
                  <p className="text-sm text-red-700 dark:text-red-300">{holiday.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {upcoming_exams.length > 0 && (
        <div className="mb-4">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2.5 flex items-center uppercase tracking-wide">
            <svg className="w-4 h-4 mr-1.5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            即将到来的考试
          </h3>
          <div className="space-y-2">
            {upcoming_exams.map((exam) => (
              <div key={exam.id} className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-yellow-800 dark:text-yellow-300">第 {exam.week_number} 周</span>
                  <span className="text-xs text-yellow-600 dark:text-yellow-400">
                    {formatDate(exam.start_date)}
                  </span>
                </div>
                {exam.notes && (
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">{exam.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pt-4 border-t border-gray-100 dark:border-surface-700">
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
          数据来源: 武汉理工大学综合信息系统
        </p>
      </div>
    </div>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}
