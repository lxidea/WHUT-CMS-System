# Critical Project Information

## News Source URLs

### Main Entry Point
**URL:** http://i.whut.edu.cn
**Description:** Primary news system for WHUT campus

**Action Required:**
- Spider must be customized to scrape this URL
- Inspect the website structure before customizing the spider
- Update `spider/whut_spider/spiders/whut_news.py` with correct selectors

### Recommended Next Steps for Spider Customization:

1. **Manual Inspection:**
```bash
# Open in browser and inspect
# Look for:
# - News list page structure
# - Article detail page structure
# - Pagination elements
# - Date format
# - Category/tag structure
```

2. **Test with Scrapy Shell:**
```bash
cd spider
scrapy shell http://i.whut.edu.cn

# In the shell, test selectors:
response.css('selector::text').getall()
response.xpath('//xpath').getall()
```

3. **Update Spider Configuration:**
   - Edit `spider/whut_spider/spiders/whut_news.py`
   - Update `start_urls` to include http://i.whut.edu.cn
   - Update `allowed_domains` to include 'whut.edu.cn'
   - Customize all CSS/XPath selectors

4. **Test Crawl:**
```bash
# Dry run with output
scrapy crawl whut_news -o test_output.json

# Check results
cat test_output.json | jq '.'
```

---

## Server Information

### Development Server (WSL2)
- **Location:** Laptop (local development)
- **OS:** WSL2 on Windows
- **Path:** `~/projects/cms-whut`

### Production Server
- **Type:** Ubuntu 20.04 LTS Server
- **Access:** `ssh myserver`
- **Uptime:** 24/7
- **Network:** Local intranet (testing phase)
- **Future:** Will be exposed via DDNS to internet

---

## Repository Information

**GitHub Repository:** https://github.com/lxidea/WHUT-CMS-System

**Branches:**
- `main` - Production-ready code
- `develop` - Development integration branch
- Feature branches as needed

**Authentication:**
- SSH keys located at `~/.ssh/id_rsa`
- Remote URL: `git@github.com:lxidea/WHUT-CMS-System.git`

---

## Technology Stack Summary

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic v2

### Spider
- **Framework:** Scrapy 2.11
- **Scheduler:** Celery 5.3
- **Queue:** Redis
- **Schedule:** Every hour (configurable)

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5.3
- **Styling:** Tailwind CSS 3.3
- **UI Library:** React 18

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (future)
- **SSL:** Let's Encrypt (future)
- **CI/CD:** GitHub Actions (future)

---

## Environment Configuration

### Development Ports
- Frontend: 3000
- Backend API: 8000
- PostgreSQL: 5432
- Redis: 6379

### Environment Variables
See `.env.example` for all configuration options.

**Critical Variables:**
```env
DATABASE_URL=postgresql://cms_user:cms_password@postgres:5432/cms_whut
REDIS_URL=redis://redis:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Contact & Access

### GitHub Access
- Repository owner: lxidea
- Visibility: Public (assumed, can be changed to private)

### Server Access
- Command: `ssh myserver`
- User: (configured in SSH config)

---

## Important Notes

1. **Spider Customization is CRITICAL**
   - The spider template has placeholder selectors
   - Must be customized for http://i.whut.edu.cn
   - Test thoroughly before deploying

2. **Legal Considerations**
   - Check robots.txt at http://i.whut.edu.cn/robots.txt
   - Respect crawl rate limits
   - Consider contacting university IT department
   - Ensure proper attribution

3. **Data Privacy**
   - Public news only (no student data)
   - Follow university data policies
   - Implement appropriate data retention

4. **Performance**
   - Start with conservative crawl rates
   - Monitor server impact
   - Scale gradually

---

## Quick Reference Commands

### Start Development Environment
```bash
cd ~/projects/cms-whut
docker-compose up -d
```

### Check Service Health
```bash
curl http://localhost:8000/api/health
```

### Run Spider Manually
```bash
docker-compose exec spider scrapy crawl whut_news
```

### View Logs
```bash
docker-compose logs -f [service-name]
```

### Deploy to Production
```bash
# On production server
ssh myserver
cd WHUT-CMS-System
git pull origin main
docker-compose down
docker-compose up -d --build
```

---

## Emergency Contacts & Resources

### Documentation
- Project README: `/README.md`
- Setup Guide: `/docs/SETUP.md`
- Architecture: `/docs/ARCHITECTURE.md`
- Git Workflow: `/docs/GIT_WORKFLOW.md`

### Troubleshooting
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart [service]`
- Rebuild: `docker-compose up -d --build`

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2024-11-28 | Initial project setup | Project kickoff |
| 2024-11-28 | Identified main news URL: http://i.whut.edu.cn | Critical for spider customization |

---

## TODO: Critical Actions Required

- [ ] Inspect http://i.whut.edu.cn and document structure
- [ ] Update spider selectors for WHUT website
- [ ] Test spider with actual WHUT news site
- [ ] Contact university IT about scraping permissions
- [ ] Configure SSH authentication for GitHub (in progress)
- [ ] Set up database migrations
- [ ] Test end-to-end data flow

---

**Last Updated:** 2024-11-28
**Next Review:** When spider customization begins
