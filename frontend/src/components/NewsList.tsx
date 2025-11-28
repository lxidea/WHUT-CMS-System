import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

interface News {
  id: number
  title: string
  summary?: string
  category?: string
  published_at?: string
  view_count: number
  source_name: string
}

interface NewsListProps {
  news: News[]
}

export default function NewsList({ news }: NewsListProps) {
  if (news.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">暂无新闻</p>
      </div>
    )
  }

  return (
    <div className="grid gap-6">
      {news.map((item) => (
        <article
          key={item.id}
          className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {item.category && (
                  <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                    {item.category}
                  </span>
                )}
                <span className="text-xs text-gray-500">
                  {item.source_name}
                </span>
              </div>

              <h2 className="text-xl font-semibold text-gray-900 mb-2 hover:text-primary-600 cursor-pointer">
                <a href={`/news/${item.id}`}>{item.title}</a>
              </h2>

              {item.summary && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {item.summary}
                </p>
              )}

              <div className="flex items-center gap-4 text-xs text-gray-500">
                {item.published_at && (
                  <span>
                    {dayjs(item.published_at).format('YYYY-MM-DD HH:mm')}
                  </span>
                )}
                <span>{item.view_count} 浏览</span>
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}
