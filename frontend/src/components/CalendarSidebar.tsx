'use client'

import { useEffect, useState } from 'react'
import { getCalendarSummary } from '@/lib/api'
import { CalendarSummary } from '@/lib/types'
import MonthlyCalendar from './MonthlyCalendar'

type ViewMode = 'compact' | 'monthly'

export default function CalendarSidebar() {
  const [calendar, setCalendar] = useState<CalendarSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('compact')

  useEffect(() => {
    async function fetchCalendar() {
      try {
        setLoading(true)
        const data = await getCalendarSummary()
        setCalendar(data)
        setError(null)
      } catch (err) {
        setError('无法加载校历信息')
        console.error('Failed to fetch calendar:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCalendar()
    const interval = setInterval(fetchCalendar, 3600000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (error || !calendar?.current_semester) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h2>
        <p className="text-gray-500 text-sm">
          {error || '暂无学期信息'}
        </p>
      </div>
    )
  }

  const { current_semester, current_week, upcoming_holidays, upcoming_exams } = calendar

  if (viewMode === 'monthly') {
    return (
      <div>
        <div className="mb-4 flex justify-end">
          <button
            onClick={() => setViewMode('compact')}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
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
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          学期校历
        </h2>
        <button
          onClick={() => setViewMode('monthly')}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          title="切换到月历视图"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
        </button>
      </div>

      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">当前学期</h3>
        <p className="text-lg font-bold text-gray-900">{current_semester.name}</p>
        <p className="text-sm text-gray-500 mt-1">
          {current_semester.academic_year} 学年 第{current_semester.semester_number}学期
        </p>
      </div>

      {current_week ? (
        <div className="mb-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-blue-800">本周</h3>
            <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
              第 {current_week.week_number} 周
            </span>
          </div>
          <p className="text-sm text-blue-700">
            {formatDate(current_week.start_date)} - {formatDate(current_week.end_date)}
          </p>
          {current_week.notes && (
            <p className="text-sm text-blue-600 mt-2 italic">{current_week.notes}</p>
          )}
          {current_week.is_holiday && (
            <span className="inline-block mt-2 bg-red-100 text-red-700 text-xs px-2 py-1 rounded">
              假期
            </span>
          )}
          {current_week.is_exam_week && (
            <span className="inline-block mt-2 bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded">
              考试周
            </span>
          )}
        </div>
      ) : (
        <div className="mb-6">
          <p className="text-sm text-gray-500">学期尚未开始或已结束</p>
        </div>
      )}

      {upcoming_holidays.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-3 flex items-center">
            <svg className="w-4 h-4 mr-1 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
            即将到来的假期
          </h3>
          <div className="space-y-2">
            {upcoming_holidays.map((holiday) => (
              <div key={holiday.id} className="bg-red-50 rounded p-3 border border-red-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-red-800">第 {holiday.week_number} 周</span>
                  <span className="text-xs text-red-600">
                    {formatDate(holiday.start_date)}
                  </span>
                </div>
                {holiday.notes && (
                  <p className="text-sm text-red-700">{holiday.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {upcoming_exams.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3 flex items-center">
            <svg className="w-4 h-4 mr-1 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            即将到来的考试
          </h3>
          <div className="space-y-2">
            {upcoming_exams.map((exam) => (
              <div key={exam.id} className="bg-yellow-50 rounded p-3 border border-yellow-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-yellow-800">第 {exam.week_number} 周</span>
                  <span className="text-xs text-yellow-600">
                    {formatDate(exam.start_date)}
                  </span>
                </div>
                {exam.notes && (
                  <p className="text-sm text-yellow-700">{exam.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-400 text-center">
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
