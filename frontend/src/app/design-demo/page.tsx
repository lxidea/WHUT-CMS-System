'use client'

import { useState } from 'react'
import dayjs from 'dayjs'

// Sample news data for demonstration
const sampleNews = [
  {
    id: 1,
    title: '【图书馆】关于我校部分IP被ScienceDirect和Wiley数据库封禁的公告',
    summary: '请全体师生务必遵守学校相关规定，合理使用数字资源。一经发现违规行为，图书馆将依据《图书馆数字资源使用管理办法》进行处理...',
    category: '学校通知·公告',
    published_at: '2025-11-28T00:00:00',
    view_count: 156,
    source_name: '武汉理工大学'
  },
  {
    id: 2,
    title: '武汉理工大学国家卓越工程师学院2025年"东风跃迁班"选拔通知',
    summary: '为贯彻落实习近平总书记在中央人才工作会议上的重要讲话精神，落实教育部等部委关于卓越工程师培养的指导意见...',
    category: '学院通知',
    published_at: '2025-11-28T00:00:00',
    view_count: 243,
    source_name: '武汉理工大学'
  },
  {
    id: 3,
    title: '【新材所】材料复合新技术全国重点实验室第八届研究生学术成果墙报展',
    summary: '11月26日，材料复合新技术全国重点实验室第八届研究生学术成果墙报展示会在西46号楼广场成功举办...',
    category: '学术活动',
    published_at: '2025-11-27T00:00:00',
    view_count: 89,
    source_name: '武汉理工大学'
  },
  {
    id: 4,
    title: '【本科生院】关于2025年下半年全国大学英语四、六级考试相关事宜的通知',
    summary: '根据教育部教育考试院统一安排，2025年下半年全国大学英语四、六级考试（笔试）将于2025年12月13日举行...',
    category: '考试通知',
    published_at: '2025-11-27T00:00:00',
    view_count: 421,
    source_name: '武汉理工大学'
  }
]

export default function DesignDemo() {
  const [activeLayout, setActiveLayout] = useState<string>('current')

  const layouts = [
    { id: 'current', name: '当前设计', description: '简洁卡片式' },
    { id: 'magazine', name: '杂志风格', description: '大图网格布局' },
    { id: 'glassmorphism', name: '毛玻璃风格', description: '现代透明效果' },
    { id: 'timeline', name: '时间线', description: '垂直时间轴' },
    { id: 'bento', name: '模块化', description: 'Bento Box 网格' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">设计风格预览</h1>
              <p className="text-gray-600 mt-1">选择您喜欢的布局风格</p>
            </div>
            <a
              href="/"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              返回首页
            </a>
          </div>
        </div>
      </div>

      {/* Layout Selector */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-wrap gap-3 mb-8">
          {layouts.map((layout) => (
            <button
              key={layout.id}
              onClick={() => setActiveLayout(layout.id)}
              className={`px-6 py-3 rounded-xl transition-all duration-300 ${
                activeLayout === layout.id
                  ? 'bg-blue-600 text-white shadow-lg scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 shadow'
              }`}
            >
              <div className="font-semibold">{layout.name}</div>
              <div className="text-xs opacity-80">{layout.description}</div>
            </button>
          ))}
        </div>

        {/* Demo Container */}
        <div className="bg-white rounded-2xl shadow-xl p-8 min-h-[600px]">
          {activeLayout === 'current' && <CurrentLayout news={sampleNews} />}
          {activeLayout === 'magazine' && <MagazineLayout news={sampleNews} />}
          {activeLayout === 'glassmorphism' && <GlassmorphismLayout news={sampleNews} />}
          {activeLayout === 'timeline' && <TimelineLayout news={sampleNews} />}
          {activeLayout === 'bento' && <BentoLayout news={sampleNews} />}
        </div>
      </div>
    </div>
  )
}

// Current Layout (existing design)
function CurrentLayout({ news }: { news: any[] }) {
  return (
    <div className="grid gap-6">
      {news.map((item) => (
        <article
          key={item.id}
          className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 p-6 border border-gray-100"
        >
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-1 rounded-full font-medium">
              {item.category}
            </span>
            <span className="text-xs text-gray-500">{item.source_name}</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors cursor-pointer">
            {item.title}
          </h2>
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">{item.summary}</p>
          <div className="flex items-center gap-5 text-xs text-gray-500">
            <span>📅 {dayjs(item.published_at).format('YYYY-MM-DD')}</span>
            <span>👁️ {item.view_count} 浏览</span>
          </div>
        </article>
      ))}
    </div>
  )
}

// Magazine Layout
function MagazineLayout({ news }: { news: any[] }) {
  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Featured Article - Large */}
      <article className="col-span-12 lg:col-span-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl overflow-hidden shadow-2xl hover:shadow-3xl transition-all duration-500 cursor-pointer group relative h-96">
        <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-all" />
        <div className="absolute inset-0 p-8 flex flex-col justify-end text-white">
          <span className="inline-block w-fit bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium mb-4">
            {news[0].category}
          </span>
          <h2 className="text-4xl font-bold mb-4 group-hover:scale-105 transition-transform origin-left">
            {news[0].title}
          </h2>
          <p className="text-white/90 mb-4 line-clamp-2">{news[0].summary}</p>
          <div className="flex items-center gap-4 text-sm text-white/80">
            <span>📅 {dayjs(news[0].published_at).format('MM-DD')}</span>
            <span>👁️ {news[0].view_count}</span>
          </div>
        </div>
      </article>

      {/* Side Articles - Medium */}
      <div className="col-span-12 lg:col-span-4 grid gap-6">
        {news.slice(1, 3).map((item) => (
          <article
            key={item.id}
            className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer border border-gray-200 hover:border-blue-300"
          >
            <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
              {item.category}
            </span>
            <h3 className="text-lg font-bold mt-3 mb-2 line-clamp-2">{item.title}</h3>
            <p className="text-gray-600 text-sm line-clamp-2 mb-3">{item.summary}</p>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span>{dayjs(item.published_at).format('MM-DD')}</span>
              <span>👁️ {item.view_count}</span>
            </div>
          </article>
        ))}
      </div>

      {/* Bottom Row - Small Cards */}
      {news.slice(3).map((item) => (
        <article
          key={item.id}
          className="col-span-12 sm:col-span-6 lg:col-span-3 bg-white rounded-xl p-5 shadow hover:shadow-lg transition-all cursor-pointer border border-gray-100"
        >
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded font-medium">
            {item.category}
          </span>
          <h4 className="font-bold mt-2 mb-2 line-clamp-2 text-sm">{item.title}</h4>
          <div className="text-xs text-gray-500">
            <span>{dayjs(item.published_at).format('MM-DD')}</span>
          </div>
        </article>
      ))}
    </div>
  )
}

// Glassmorphism Layout
function GlassmorphismLayout({ news }: { news: any[] }) {
  return (
    <div className="relative">
      {/* Background Blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      <div className="absolute top-40 right-1/4 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />

      <div className="relative grid gap-6">
        {news.map((item, index) => (
          <article
            key={item.id}
            className="backdrop-blur-xl bg-white/60 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 p-6 border border-white/40 hover:bg-white/70 cursor-pointer"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs backdrop-blur-sm bg-white/80 text-blue-700 px-3 py-1.5 rounded-full font-semibold shadow-sm">
                    {item.category}
                  </span>
                  <span className="text-xs text-gray-600">{item.source_name}</span>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors">
                  {item.title}
                </h2>
                <p className="text-gray-700 text-sm mb-4 line-clamp-2 leading-relaxed">
                  {item.summary}
                </p>
                <div className="flex items-center gap-5 text-xs text-gray-600">
                  <span className="flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" />
                    </svg>
                    {dayjs(item.published_at).format('YYYY-MM-DD')}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                    {item.view_count} 浏览
                  </span>
                </div>
              </div>
              <div className="w-24 h-24 rounded-xl backdrop-blur-sm bg-gradient-to-br from-blue-400/20 to-purple-400/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-12 h-12 text-blue-500/60" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}

// Timeline Layout
function TimelineLayout({ news }: { news: any[] }) {
  return (
    <div className="relative pl-12">
      {/* Timeline Line */}
      <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 to-pink-400" />

      <div className="space-y-8">
        {news.map((item, index) => (
          <div key={item.id} className="relative">
            {/* Timeline Dot */}
            <div className="absolute -left-[2.6rem] top-6 w-5 h-5 rounded-full bg-white border-4 border-blue-500 shadow-lg z-10" />

            {/* Date Badge */}
            <div className="absolute -left-[5.5rem] top-5 text-right">
              <div className="text-xs font-bold text-gray-700">
                {dayjs(item.published_at).format('MM-DD')}
              </div>
              <div className="text-xs text-gray-500">
                {dayjs(item.published_at).format('YYYY')}
              </div>
            </div>

            {/* Card */}
            <article className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 ml-4 border-l-4 border-blue-500">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs bg-blue-500 text-white px-3 py-1 rounded-full font-medium">
                  {item.category}
                </span>
                <span className="text-xs text-gray-500">• {item.source_name}</span>
                <span className="text-xs text-gray-400 ml-auto">👁️ {item.view_count}</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2 hover:text-blue-600 cursor-pointer transition-colors">
                {item.title}
              </h3>
              <p className="text-gray-600 text-sm line-clamp-2">{item.summary}</p>
            </article>
          </div>
        ))}
      </div>
    </div>
  )
}

// Bento Box Layout
function BentoLayout({ news }: { news: any[] }) {
  const bentoSizes = ['large', 'medium', 'medium', 'small']

  return (
    <div className="grid grid-cols-12 gap-4 auto-rows-[200px]">
      {news.map((item, index) => {
        const size = bentoSizes[index % bentoSizes.length]

        let gridClass = ''
        if (size === 'large') {
          gridClass = 'col-span-12 md:col-span-8 row-span-2'
        } else if (size === 'medium') {
          gridClass = 'col-span-12 md:col-span-4 row-span-2'
        } else {
          gridClass = 'col-span-12 md:col-span-6 row-span-1'
        }

        const colors = [
          'from-blue-500 to-blue-600',
          'from-purple-500 to-purple-600',
          'from-pink-500 to-pink-600',
          'from-orange-500 to-orange-600',
        ]
        const colorClass = colors[index % colors.length]

        return (
          <article
            key={item.id}
            className={`${gridClass} bg-gradient-to-br ${colorClass} rounded-3xl p-6 overflow-hidden relative group cursor-pointer hover:scale-[1.02] transition-all duration-300 shadow-xl hover:shadow-2xl`}
          >
            <div className="relative z-10 h-full flex flex-col justify-between text-white">
              <div>
                <span className="inline-block bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium mb-3">
                  {item.category}
                </span>
                <h3 className={`font-bold mb-2 group-hover:scale-105 transition-transform origin-left ${
                  size === 'large' ? 'text-2xl' : size === 'medium' ? 'text-lg' : 'text-base'
                }`}>
                  {item.title}
                </h3>
                {size !== 'small' && (
                  <p className="text-white/90 text-sm line-clamp-2 mb-3">{item.summary}</p>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-white/80">
                <span>{dayjs(item.published_at).format('MM-DD')}</span>
                <span>👁️ {item.view_count}</span>
              </div>
            </div>

            {/* Decorative Background */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-white rounded-full translate-y-1/2 -translate-x-1/2" />
            </div>
          </article>
        )
      })}
    </div>
  )
}
