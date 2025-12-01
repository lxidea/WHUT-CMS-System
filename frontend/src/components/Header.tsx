'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

export default function Header() {
  const { user, logout } = useAuth()
  const router = useRouter()

  return (
    <header className="bg-gradient-primary shadow-medium sticky top-0 z-50 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-5">
        <div className="flex items-center justify-between">
          <div className="cursor-pointer" onClick={() => router.push('/')}>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2 hover:scale-105 transition-transform">
              <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
              CMS-WHUT
            </h1>
            <p className="text-sm text-primary-50 ml-9">
              武汉理工大学新闻管理系统
            </p>
          </div>

          <div className="flex items-center gap-6">
            <nav className="flex gap-6">
              <a href="/" className="text-white/90 hover:text-white font-medium transition-colors relative group">
                首页
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white transition-all group-hover:w-full"></span>
              </a>
              {user && (
                <a href="/bookmarks" className="text-white/90 hover:text-white font-medium transition-colors relative group">
                  我的收藏
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white transition-all group-hover:w-full"></span>
                </a>
              )}
              <a href="/about" className="text-white/90 hover:text-white font-medium transition-colors relative group">
                关于
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white transition-all group-hover:w-full"></span>
              </a>
            </nav>

            <div className="flex items-center gap-3 border-l border-white/20 pl-6">
              {user ? (
                <>
                  <a href="/profile" className="text-white/90 hover:text-white transition-colors">
                    <div className="flex items-center gap-2">
                      <div className="w-9 h-9 bg-white/20 text-white rounded-full flex items-center justify-center font-semibold backdrop-blur-sm border border-white/30 hover:bg-white/30 transition-all">
                        {user.username[0].toUpperCase()}
                      </div>
                      <span className="font-medium">{user.username}</span>
                    </div>
                  </a>
                  <button
                    onClick={logout}
                    className="px-4 py-2 text-sm text-white/90 hover:text-white border border-white/30 rounded-lg hover:bg-white/10 transition-all font-medium"
                  >
                    退出
                  </button>
                </>
              ) : (
                <>
                  <a
                    href="/login"
                    className="px-4 py-2 text-sm text-white/90 hover:text-white border border-white/30 rounded-lg hover:bg-white/10 transition-all font-medium"
                  >
                    登录
                  </a>
                  <a
                    href="/register"
                    className="px-5 py-2 text-sm bg-white text-primary-600 rounded-lg hover:bg-white/90 transition-all font-semibold shadow-sm hover:shadow-md"
                  >
                    注册
                  </a>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
