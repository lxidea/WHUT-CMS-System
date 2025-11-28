# Frontend

Next.js-based frontend for CMS-WHUT content management system.

## Features

- Modern React with Next.js 14 (App Router)
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design
- Server-side rendering (SSR) support
- API integration with backend

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   ├── Header.tsx
│   │   └── NewsList.tsx
│   └── lib/              # Utilities
│       └── api.ts        # API client
├── public/               # Static files
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Development

### Local Setup (without Docker)

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

3. Run development server:
```bash
npm run dev
```

4. Open http://localhost:3000

### With Docker Compose

From project root:
```bash
docker-compose up frontend
```

## Build for Production

```bash
npm run build
npm run start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Features to Implement

This is a basic skeleton. You can extend with:

1. **News Detail Page**: View full article
2. **Search**: Full-text search functionality
3. **Categories**: Filter by category
4. **Pagination**: Navigate through news pages
5. **RSS Feed**: Subscribe to updates
6. **Dark Mode**: Theme toggle
7. **Admin Panel**: Manage news (future)

## Adding New Pages

Create files in `src/app/`:

```bash
# News detail page
src/app/news/[id]/page.tsx

# Categories page
src/app/categories/page.tsx
```

## Styling

Using Tailwind CSS utility classes:

```tsx
<div className="bg-white p-4 rounded-lg shadow-md">
  Content
</div>
```

Customize theme in `tailwind.config.js`.

## API Integration

See `src/lib/api.ts` for API client functions.

Example usage:
```tsx
import { getNewsList } from '@/lib/api'

const data = await getNewsList({ page: 1, page_size: 20 })
```
