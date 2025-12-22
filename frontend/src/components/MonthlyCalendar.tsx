'use client'

import { useEffect, useState } from 'react'
import { getMonthlyCalendar } from '@/lib/api'

interface DayInfo {
  date: string
  day: number
  weekday: number
  is_today: boolean
  week_info: {
    week_number: number
    is_holiday: boolean
    is_exam_week: boolean
    notes: string | null
  } | null
}

interface MonthlyCalendarData {
  year: number
  month: number
  month_name: string
  semester: {
    id: number
    name: string
    academic_year: string
  } | null
  days: DayInfo[]
}

export default function MonthlyCalendar() {
  const [calendar, setCalendar] = useState<MonthlyCalendarData | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentDate, setCurrentDate] = useState(new Date())

  useEffect(() => {
    async function fetchCalendar() {
      try {
        setLoading(true)
        const data = await getMonthlyCalendar(
          currentDate.getFullYear(),
          currentDate.getMonth() + 1
        )
        setCalendar(data)
      } catch (err) {
        console.error('Failed to fetch monthly calendar:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCalendar()
  }, [currentDate])

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1)
    } else {
      newDate.setMonth(newDate.getMonth() + 1)
    }
    setCurrentDate(newDate)
  }

  if (loading || !calendar) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-1">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="grid grid-cols-8 gap-1">
                <div className="h-16 bg-gray-200 rounded"></div>
                {[...Array(7)].map((_, j) => (
                  <div key={j} className="h-16 bg-gray-100 rounded"></div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Get the first day of the month to calculate padding
  const firstDayOfMonth = new Date(calendar.year, calendar.month - 1, 1).getDay()
  // Convert to Monday-based (0=Monday, 6=Sunday)
  const paddingDays = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1

  const weekDays = ['一', '二', '三', '四', '五', '六', '日']

  // Group days into rows of 7 with padding
  const allCells = [...Array(paddingDays).fill(null), ...calendar.days]
  const rows: Array<{ weekNumber: number | null; cells: Array<DayInfo | null> }> = []

  for (let i = 0; i < allCells.length; i += 7) {
    const rowCells = allCells.slice(i, i + 7)
    // Get week number from first non-null cell in this row
    const weekNumber = rowCells.find(cell => cell?.week_info)?.week_info?.week_number || null
    rows.push({ weekNumber, cells: rowCells })
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            {calendar.year}年{calendar.month}月
          </h2>
          {calendar.semester && (
            <p className="text-sm text-gray-600 mt-1">{calendar.semester.name}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="上个月"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            今天
          </button>
          <button
            onClick={() => navigateMonth('next')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="下个月"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Week day headers */}
      <div className="grid grid-cols-8 gap-2 mb-2">
        <div className="text-center text-xs font-semibold text-gray-500 py-2">
          周
        </div>
        {weekDays.map((day) => (
          <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="space-y-1">
        {rows.map((row, rowIndex) => (
          <div key={rowIndex} className="grid grid-cols-8 gap-1">
            {/* Week number column */}
            <div className="flex items-center justify-center">
              {row.weekNumber && (
                <div
                  className={`
                    text-xs font-semibold px-1.5 py-0.5 rounded
                    ${row.cells.some(cell => cell?.week_info?.is_holiday)
                      ? 'bg-red-500 text-white'
                      : row.cells.some(cell => cell?.week_info?.is_exam_week)
                        ? 'bg-yellow-500 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }
                  `}
                >
                  {row.weekNumber}
                </div>
              )}
            </div>

            {/* Day cells */}
            {row.cells.map((day, cellIndex) => {
              if (!day) {
                return <div key={`empty-${cellIndex}`} className="h-16"></div>
              }

              const isHoliday = day.week_info?.is_holiday
              const isExam = day.week_info?.is_exam_week

              return (
                <div
                  key={day.date}
                  className={`
                    h-16 p-1.5 rounded border transition-all flex flex-col
                    ${day.is_today
                      ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                      : isHoliday
                        ? 'border-red-200 bg-red-50'
                        : isExam
                          ? 'border-yellow-200 bg-yellow-50'
                          : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  {/* Day number */}
                  <div className={`text-sm font-semibold leading-none ${day.is_today ? 'text-blue-600' : 'text-gray-800'}`}>
                    {day.day}
                  </div>

                  {/* Notes */}
                  {day.week_info?.notes && (
                    <div className={`
                      text-xs line-clamp-2 mt-1 flex-1
                      ${isHoliday ? 'text-red-700' : isExam ? 'text-yellow-700' : 'text-gray-600'}
                    `}>
                      {day.week_info.notes}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-4 pt-3 border-t border-gray-200 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-blue-500 bg-blue-50"></div>
          <span className="text-gray-600">今天</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-red-200 bg-red-50"></div>
          <span className="text-gray-600">假期</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border-2 border-yellow-200 bg-yellow-50"></div>
          <span className="text-gray-600">考试周</span>
        </div>
      </div>
    </div>
  )
}
