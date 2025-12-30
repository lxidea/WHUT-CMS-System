'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import { useRouter } from 'next/navigation'

export default function Header() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const router = useRouter()

  return (
    <header className="bg-gradient-mixed dark:bg-gradient-dark shadow-medium dark:shadow-dark-medium sticky top-0 z-50 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="cursor-pointer" onClick={() => router.push('/')}>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2 hover:scale-105 transition-transform">
              <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
              CMS-WHUT
            </h1>
            <p className="text-sm text-white/70 ml-9">
              武汉理工大学新闻管理系统
            </p>
          </div>

          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-5">
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

            <div className="flex items-center gap-3 border-l border-white/20 pl-4">
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-all text-white"
                title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
              >
                {theme === 'dark' ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>

              {user ? (
                <>
                  <a href="/profile" className="text-white/90 hover:text-white transition-colors">
                    <div className="flex items-center gap-2">
                      <div className="w-9 h-9 bg-white/20 text-white rounded-full flex items-center justify-center font-semibold backdrop-blur-sm border border-white/30 hover:bg-white/30 transition-all">
                        {user.username[0].toUpperCase()}
                      </div>
                      <span className="font-medium hidden sm:inline">{user.username}</span>
                    </div>
                  </a>
                  <button
                    onClick={logout}
                    className="px-4 py-2 text-sm text-white/90 hover:text-white border border-white/30 rounded-lg hover:bg-white/10 transition-all font-medium hidden sm:block"
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
                    className="px-4 py-2 text-sm bg-white text-primary-600 dark:text-secondary-600 rounded-lg hover:bg-white/90 transition-all font-semibold shadow-sm hover:shadow-md hidden sm:block"
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
