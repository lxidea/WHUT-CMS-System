# CMS-WHUT Frontend

Modern news portal frontend for Wuhan University of Technology built with Next.js 14, TypeScript, and Tailwind CSS.

## ✨ Features

- ✅ **News Listing**: Browse all news with pagination (20 per page)
- ✅ **Category Filtering**: Filter by 4 categories (部门亮点资讯, 学校通知·公告, 学院通知公告, 学术讲座)
- ✅ **Search Functionality**: Search news by title and content
- ✅ **Article Detail Pages**: View full article content with metadata
- ✅ **Image-Only Post Handling**: Special display for image-based announcements
- ✅ **Responsive Design**: Mobile-first responsive layout
- ✅ **Clean UI**: Modern, accessible interface with Chinese font optimization

## 🚀 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Native Fetch API
- **Date Handling**: Day.js with Chinese locale

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (news listing)
│   │   ├── news/[id]/page.tsx # Article detail page
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── Header.tsx         # Site header
│   │   ├── NewsList.tsx       # News list component
│   │   ├── CategoryFilter.tsx # Category filter buttons
│   │   └── SearchBar.tsx      # Search input component
│   └── lib/
│       ├── api.ts             # API client functions
│       └── types.ts           # TypeScript type definitions
├── public/                    # Static assets
└── package.json
```

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Backend API running at http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at **http://localhost:3000**

## 🌐 Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📄 Pages

### Home Page (`/`)
- News listing with pagination
- Category filter buttons
- Search bar
- Total news count
- Responsive grid layout

### Article Detail Page (`/news/[id]`)
- Full article content
- Metadata (date, views, source)
- Category badge
- Special indicator for image posts
- Back navigation
- Link to original source

## 🧩 Components

### Header
Site branding and navigation with responsive layout

### NewsList
Displays news cards with title, summary, category, date, views

### CategoryFilter
Filter buttons with active state styling

### SearchBar
Search input with submit and clear functionality

## 🔌 API Integration

Functions in `src/lib/api.ts`:

```typescript
getNewsList({ page, page_size, category?, search? })
getNewsById(id)
getCategories()
```

## 🎨 Styling

- Tailwind CSS with blue primary color
- Responsive breakpoints (sm, md, lg, xl)
- Custom prose styles for articles
- Optimized Chinese font stack

## 🚀 Integration with Backend

```bash
# Terminal 1: Start backend
cd ../backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
npm run dev
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:3000 | xargs kill -9
```

### API Connection Issues
- Verify backend: `curl http://localhost:8000/api/health`
- Check CORS settings in backend
- Verify NEXT_PUBLIC_API_URL

### Build Errors
```bash
rm -rf .next node_modules package-lock.json
npm install
```

## 📱 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers
