# Website Pagination & Category Pages Analysis

**Date:** 2024-11-28
**Purpose:** Document pagination structure and category archive pages

---

## Overview

The WHUT news system has **multiple category archive pages** accessible from the homepage. Each category page contains:
1. **Sidebar navigation** - Sub-categories or departments
2. **News list** - Paginated list of articles
3. **Pagination controls** - JavaScript-based pagination

---

## Category Archive Pages

### 1. Comprehensive News (综合新闻)
**URL:** http://news.whut.edu.cn/zhxw/
**Domain:** news.whut.edu.cn (different from main portal!)

**Structure:**
```html
<div class="yw-list grid">
    <div id="slideBox2" class="slideBox2 mb20">
        <div class="bd">
            <ul>
                <li>
                    <a href="./202511/t20251114_1356195.shtml" target="_blank">
                        <div class="image">
                            <img src="./202511/W020251114389721543126.jpg"/>
                        </div>
                        <div class="right_text">
                            <h3>百年理工 口述实录 |蔡志坡：...</h3>
                            <p>【编者按】百年理工，根深叶茂...</p>
                            <div class="bdsharebuttonbox">2025-11-14</div>
                        </div>
                    </a>
                </li>
                <!-- More items -->
            </ul>
        </div>
    </div>
</div>
```

**CSS Selectors:**
```python
# News items
'div.slideBox2 ul li'

# Article link
'div.slideBox2 ul li a::attr(href)'

# Title
'div.slideBox2 ul li h3::text'

# Summary/preview
'div.slideBox2 ul li p::text'

# Date
'div.slideBox2 ul li div.bdsharebuttonbox::text'

# Image
'div.slideBox2 ul li img::attr(src)'
```

**Note:** This page appears to show featured/highlighted news with images.

---

### 2. School Notices (学校通知·公告)
**URL:** http://i.whut.edu.cn/xxtg/
**Domain:** i.whut.edu.cn (main portal)

**Page Structure:**

#### Sidebar Navigation (Left)
```html
<div class="text_list_menu2">
    <ul>
        <li class="left_list_tit2">职能部门</li>
        <li><a href='http://i.whut.edu.cn/xxtg/znbm/dzb/'>党政办</a></li>
        <li><a href='http://i.whut.edu.cn/xxtg/znbm/zzb/'>组织部</a></li>
        <li><a href='http://i.whut.edu.cn/xxtg/znbm/xcb/'>宣传部</a></li>
        <!-- 40+ departments -->
    </ul>
</div>
```

**Department Sub-categories:**
- 党政办 (dzb) - Party & Admin Office
- 组织部 (zzb) - Organization Department
- 宣传部 (xcb) - Publicity Department
- 本科生院 (jwc) - Undergraduate School
- 研究生院 (yjsy) - Graduate School
- 财务处 (jcc) - Finance Office
- And 35+ more departments...

**Each department has its own sub-page:**
- Format: `http://i.whut.edu.cn/xxtg/znbm/[dept]/`
- Example: `http://i.whut.edu.cn/xxtg/znbm/jwc/` (Undergraduate School)

#### Main Content Area (Right)
```html
<div class="text_list_cont">
    <div class="text_list_tit">学校通知·公告&nbsp;&nbsp;通知公告</div>
    <ul class="normal_list2">
        <li>
            <span>
                <i>【<a href="./znbm/jwc/">本科生院</a>】</i>
                <a href="./znbm/jwc/202511/t20251128_622234.shtml"
                   title="【本科生院】关于2025年下半年全国大学英语四、六级考试（笔试）相关事宜的通知">
                    【本科生院】关于2025年下半年全国大学英语四、...
                </a>
            </span>
            <strong>2025-11-28</strong>
        </li>
        <!-- More items -->
    </ul>
</div>
```

**CSS Selectors:**
```python
# Department links (sidebar)
'div.text_list_menu2 ul li a::attr(href)'
'div.text_list_menu2 ul li a::text'

# News items (main content)
'ul.normal_list2 li'

# Department tag in title
'ul.normal_list2 li span i a::text'

# Article link
'ul.normal_list2 li span a:nth-child(2)::attr(href)'

# Full title (from title attribute)
'ul.normal_list2 li span a:nth-child(2)::attr(title)'

# Truncated title (display text)
'ul.normal_list2 li span a:nth-child(2)::text'

# Date
'ul.normal_list2 li strong::text'
```

---

## Pagination Structure

### JavaScript-Based Pagination

**Location:** Bottom of page, implemented in `<script>` tag

**Pagination Logic:**
```javascript
var countPage = 133;      // Total pages
var currentPage = 0;      // Current page (0-indexed)
var prevPage = -1;        // Previous page
var nextPage = 1;         // Next page

// First page URL: index.shtml
// Other pages: index_1.shtml, index_2.shtml, ... index_132.shtml
```

**URL Pattern:**
- **Page 1 (First):** `index.shtml` or just the directory URL
- **Page 2:** `index_1.shtml`
- **Page 3:** `index_2.shtml`
- **Page N:** `index_{N-1}.shtml`

**Note:** Page numbering is 0-indexed in URLs but 1-indexed in display!

**Pagination HTML:**
```javascript
// First page
if(currentPage > 0)
    document.write("<a href=\"index.shtml\">首页</a>&nbsp;");

// Previous page
if(currentPage > 0)
    document.write("<a href=\"index_" + prevPage + ".shtml\">上一页</a>&nbsp;");

// Page number display
document.write("第"+(currentPage+1)+"/"+(countPage)+"页&nbsp;&nbsp;");

// Next page
if(currentPage < (countPage-1))
    document.write("<a href=\"index_" + nextPage + ".shtml\">下一页</a>&nbsp;");

// Last page
if(currentPage < (countPage-1))
    document.write("<a href=\"index_" + (countPage-1) + ".shtml\">尾页</a>&nbsp;");
```

**Pagination Variables Location:**
The variables `countPage` and `currentPage` are defined at the bottom of each page in a `<script>` tag.

**Extraction Strategy:**
```python
import re

# Extract pagination info from page
count_match = re.search(r'var countPage = (\d+);', response.text)
current_match = re.search(r'var currentPage = (\d+);', response.text)

if count_match:
    total_pages = int(count_match.group(1))

if current_match:
    current_page = int(current_match.group(1))
```

---

## Complete Category List

### From Homepage Navigation

```
首页 (Home) - http://i.whut.edu.cn
综合新闻 (Comprehensive News) - http://news.whut.edu.cn/zhxw/
学校通知公告 (School Notices) - http://i.whut.edu.cn/xxtg/
部门新闻 (Department News) - http://i.whut.edu.cn/bmxw/
学院·所·中心通知公告 (College Notices) - http://i.whut.edu.cn/xytg/
学院新闻 (College News) - http://i.whut.edu.cn/xyxw/
学术讲座·报告·论坛 (Academic Lectures) - http://i.whut.edu.cn/lgjz/
教学督导 (Teaching Supervision) - http://i.whut.edu.cn/jxdd/
纪检简报 (Discipline Inspection) - http://i.whut.edu.cn/jjjb/
校报 (School Newspaper) - http://wut.ihwrm.com
媒体理工 (Media Coverage) - http://news.whut.edu.cn/mtlg/
```

### Additional Categories (from news.whut.edu.cn)

```
首页 (Home) - https://news.whut.edu.cn/
综合新闻 (Comprehensive News) - https://news.whut.edu.cn/zhxw/
理工资讯 (WHUT Updates) - https://news.whut.edu.cn/lgzx/
学术动态 (Academic News) - https://news.whut.edu.cn/xsdt/
文化影像 (Culture & Media) - https://news.whut.edu.cn/whyx/
校园生活 (Campus Life) - https://news.whut.edu.cn/xysh/
媒体理工 (Media Coverage) - https://news.whut.edu.cn/mtlg/
```

---

## Spider Implementation Strategy

### Phase 1: Homepage Scraping
```python
def parse(self, response):
    """Parse homepage - get latest from all categories"""
    # Extract from all homepage sections
    # Follow "more" links to category pages
```

### Phase 2: Category Page Scraping
```python
def parse_category(self, response):
    """Parse category list page"""
    # Extract news items
    # Extract pagination info
    # Follow next page if exists
```

### Phase 3: Pagination Handling
```python
def parse_category(self, response):
    # Get current page info
    count_match = re.search(r'var countPage = (\d+);', response.text)
    current_match = re.search(r'var currentPage = (\d+);', response.text)

    if count_match and current_match:
        total_pages = int(count_match.group(1))
        current_page = int(current_match.group(1))

        # Process articles on current page
        for item in response.css('ul.normal_list2 li'):
            # Extract article info
            yield {...}

        # Follow next page
        if current_page < (total_pages - 1):
            next_page = current_page + 1
            if next_page == 0:
                next_url = response.urljoin('index.shtml')
            else:
                next_url = response.urljoin(f'index_{next_page}.shtml')
            yield scrapy.Request(next_url, callback=self.parse_category)
```

### Phase 4: Department Sub-pages
```python
def parse_category_with_departments(self, response):
    """Parse category page with department sidebar"""
    # Extract department links
    dept_links = response.css('div.text_list_menu2 ul li a::attr(href)').getall()

    # Follow each department
    for dept_url in dept_links:
        yield scrapy.Request(
            response.urljoin(dept_url),
            callback=self.parse_department
        )

    # Also process main page
    yield from self.parse_category(response)

def parse_department(self, response):
    """Parse individual department news page"""
    # Same structure as category page
    # Also has pagination
    yield from self.parse_category(response)
```

---

## URL Construction Examples

### School Notices Category
```
Main page:     http://i.whut.edu.cn/xxtg/
Page 2:        http://i.whut.edu.cn/xxtg/index_1.shtml
Page 3:        http://i.whut.edu.cn/xxtg/index_2.shtml
Last (page N): http://i.whut.edu.cn/xxtg/index_{N-1}.shtml
```

### Department Sub-page (Undergraduate School)
```
Main page:     http://i.whut.edu.cn/xxtg/znbm/jwc/
Page 2:        http://i.whut.edu.cn/xxtg/znbm/jwc/index_1.shtml
Page 3:        http://i.whut.edu.cn/xxtg/znbm/jwc/index_2.shtml
```

### College Notices Category
```
Main page:     http://i.whut.edu.cn/xytg/
Page 2:        http://i.whut.edu.cn/xytg/index_1.shtml
```

---

## Scraping Scope Recommendations

### Minimal Scope (Start Here)
1. **Homepage only** - Latest news from all categories
2. **No pagination** - Just the first page of each section
3. **Est. items:** ~50-100 articles

### Medium Scope (Recommended)
1. **Homepage** - All sections
2. **Top 3 categories with pagination:**
   - 综合新闻 (Comprehensive News)
   - 学校通知公告 (School Notices) - first 10 pages
   - 部门新闻 (Department News) - first 10 pages
3. **Est. items:** 500-1000 articles

### Full Scope (Production)
1. **All categories** - All 11 main categories
2. **Full pagination** - All pages (some have 100+ pages!)
3. **All departments** - 40+ department sub-pages
4. **Est. items:** 10,000+ articles
5. **Estimated time:** Several hours for full crawl

---

## Important Notes

### 1. Pagination Complexity
- **0-indexed URLs:** `index_0.shtml` is actually page 2
- **First page exception:** First page is `index.shtml`, not `index_0.shtml`
- **JavaScript variables:** Must parse HTML source to get `countPage`

### 2. Multi-Domain Structure
- `i.whut.edu.cn` - Main portal (notices, departments)
- `news.whut.edu.cn` - News site (comprehensive news, media)
- Both domains must be in `allowed_domains`

### 3. Department Sub-pages
- Each department has own sub-page with pagination
- Total: 40+ department pages × pages per department
- Can quickly lead to thousands of requests

### 4. Rate Limiting Recommendations
```python
# In settings.py
DOWNLOAD_DELAY = 2  # 2 seconds between requests
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # Max 2 parallel requests
AUTOTHROTTLE_ENABLED = True
```

### 5. Deduplication Strategy
- Some articles may appear in multiple categories
- Use `content_hash` for deduplication
- Check `source_url` uniqueness in database

---

## Testing Commands

### Test Category Page
```bash
scrapy shell http://i.whut.edu.cn/xxtg/

# Extract pagination info
import re
count_match = re.search(r'var countPage = (\d+);', response.text)
current_match = re.search(r'var currentPage = (\d+);', response.text)
print(f"Total pages: {count_match.group(1)}")
print(f"Current page: {current_match.group(1)}")

# Extract news items
response.css('ul.normal_list2 li span a:nth-child(2)::attr(title)').getall()
response.css('ul.normal_list2 li strong::text').getall()
```

### Test Department Links
```bash
scrapy shell http://i.whut.edu.cn/xxtg/

# Get all departments
response.css('div.text_list_menu2 ul li a::attr(href)').getall()
response.css('div.text_list_menu2 ul li a::text').getall()
```

### Test Pagination URL Construction
```bash
# In scrapy shell
base_url = response.url
# For page 2
next_url = response.urljoin('index_1.shtml')
print(next_url)
```

---

## Summary

**Key Findings:**
1. ✅ Homepage has 11 main category sections
2. ✅ Each category has its own archive page
3. ✅ Pagination uses JavaScript with pattern `index_{N-1}.shtml`
4. ✅ Some categories have 40+ department sub-pages
5. ✅ Total potential articles: 10,000+
6. ✅ Two domains involved: `i.whut.edu.cn` and `news.whut.edu.cn`

**Recommendations:**
1. Start with **homepage + first page of each category**
2. Add **pagination support** after basic scraping works
3. Add **department pages** in phase 3
4. Use **aggressive rate limiting** to be polite
5. Implement **smart deduplication** to avoid duplicate content

---

**Last Updated:** 2024-11-28
**Status:** Pagination structure fully documented
**Ready for:** Spider implementation with pagination support
