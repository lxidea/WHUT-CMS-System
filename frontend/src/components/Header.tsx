export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-primary-600">
              CMS-WHUT
            </h1>
            <p className="text-sm text-gray-600">
              武汉理工大学新闻管理系统
            </p>
          </div>

          <nav className="flex gap-6">
            <a href="/" className="text-gray-700 hover:text-primary-600">
              首页
            </a>
            <a href="/categories" className="text-gray-700 hover:text-primary-600">
              分类
            </a>
            <a href="/about" className="text-gray-700 hover:text-primary-600">
              关于
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
