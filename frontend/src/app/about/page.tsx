import Header from '@/components/Header'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            关于 CMS-WHUT
          </h1>

          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              项目简介
            </h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              CMS-WHUT（Content Management System for Wuhan University of Technology）是一个为武汉理工大学设计的新闻聚合管理系统。
              该系统自动从学校官网采集新闻信息，并提供便捷的浏览、搜索和分类功能。
            </p>
            <p className="text-gray-700 leading-relaxed">
              系统采用现代化的技术架构，实现了全自动化的新闻采集、存储和展示，为师生提供一个集中的新闻信息平台。
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              主要功能
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="font-semibold text-gray-900">新闻浏览</h3>
                </div>
                <p className="text-sm text-gray-600">
                  查看来自学校官网的最新新闻，支持分页浏览
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <h3 className="font-semibold text-gray-900">搜索功能</h3>
                </div>
                <p className="text-sm text-gray-600">
                  快速搜索新闻标题和内容，找到您需要的信息
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <h3 className="font-semibold text-gray-900">分类筛选</h3>
                </div>
                <p className="text-sm text-gray-600">
                  按照新闻类别进行筛选，精准定位目标信息
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <h3 className="font-semibold text-gray-900">自动更新</h3>
                </div>
                <p className="text-sm text-gray-600">
                  系统每小时自动采集最新新闻，保持信息时效性
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              技术架构
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">前端技术</h3>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm">Next.js 14</span>
                  <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm">TypeScript</span>
                  <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm">Tailwind CSS</span>
                  <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm">React</span>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">后端技术</h3>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded text-sm">FastAPI</span>
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded text-sm">Python</span>
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded text-sm">PostgreSQL</span>
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded text-sm">Redis</span>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">数据采集</h3>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded text-sm">Scrapy</span>
                  <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded text-sm">Celery</span>
                  <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded text-sm">定时任务</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              系统特点
            </h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <strong className="text-gray-900">100% 采集成功率</strong>
                  <p className="text-sm text-gray-600">通过智能HTML解析和多重容错机制，确保新闻采集完整性</p>
                </div>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <strong className="text-gray-900">响应式设计</strong>
                  <p className="text-sm text-gray-600">完美适配桌面端、平板和移动设备，随时随地浏览新闻</p>
                </div>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <strong className="text-gray-900">现代化界面</strong>
                  <p className="text-sm text-gray-600">简洁美观的用户界面，提供流畅的浏览体验</p>
                </div>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <strong className="text-gray-900">高性能</strong>
                  <p className="text-sm text-gray-600">快速响应，页面加载时间小于3秒</p>
                </div>
              </li>
            </ul>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              数据来源
            </h3>
            <p className="text-gray-700 text-sm">
              本系统所有新闻数据均来自武汉理工大学官方网站（
              <a href="http://i.whut.edu.cn" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                i.whut.edu.cn
              </a>
              ），系统仅作为信息聚合展示平台，不修改原始内容。所有新闻版权归武汉理工大学所有。
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
