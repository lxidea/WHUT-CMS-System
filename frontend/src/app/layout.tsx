import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CMS-WHUT - 武汉理工大学新闻管理系统',
  description: 'Wuhan University of Technology Content Management System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
