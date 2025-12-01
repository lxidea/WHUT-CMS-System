# WHUT News Website Structure Analysis

**Target URL:** http://i.whut.edu.cn
**Analysis Date:** 2024-11-28
**Purpose:** Understand structure for spider customization

---

## Website Overview

**Title:** 欢迎访问武汉理工大学综合信息系统 (WHUT Comprehensive Information System)

**Technology Stack:**
- HTML: XHTML 1.0 Strict
- Charset: UTF-8
- JavaScript: jQuery 1.4.2
- Features: Image sliders, auto-scrolling news

---

## Main Navigation Menu

Located in `.in_nav ul li` section (lines 143-156):

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

---

## Content Sections & Structures

### 1. 综合新闻 (Comprehensive News)

**Section Location:** `div.media_whut`
**Title Element:** `.tit_box1 h2` containing "综合新闻"
**More Link:** `http://news.whut.edu.cn/zhxw/`

**List Structure:**
```html
<div class="media_whut">
    <div class="tit_box1">
        <h2>综合新闻</h2>
        <a href="..."><img src="./images/more1.gif" /></a>
    </div>
    <ul>
        <li>
            <a href="https://news.whut.edu.cn/zhxw/202511/t20251128_1358589.shtml"
               target="_blank"
               title="【师道大讲堂】学校举行全国"最美教师"姜德生院士事迹报告会">
                【师道大讲堂】学校举行全国"最美教师...
            </a>
            <span>11-28</span>
        </li>
        <!-- More items -->
    </ul>
</div>
```

**CSS Selectors for Comprehensive News:**
- Container: `div.media_whut`
- List items: `div.media_whut ul li`
- Article link: `div.media_whut ul li a`
- Article title: `div.media_whut ul li a::attr(title)` or `::text`
- Article URL: `div.media_whut ul li a::attr(href)`
- Date: `div.media_whut ul li span::text`

**URL Pattern:**
- Format: `https://news.whut.edu.cn/zhxw/YYYYMM/tYYYYMMDD_XXXXXXX.shtml`
- Example: `https://news.whut.edu.cn/zhxw/202511/t20251128_1358589.shtml`

**Sample Items (Lines 389-408):**
- Latest: 11-28 "【师道大讲堂】学校举行全国"最美教师"姜德生院士事迹报告会"
- Approx 10 items visible on homepage

---

### 2. 学校通知·公告 (School Notices & Announcements)

**Section Location:** `div.list_box1` (first occurrence)
**Title Element:** `.tit_box2 h2` containing "学校通知·公告"
**More Link:** `./xxtg/`

**List Structure:**
```html
<div class="list_box1">
    <div class="tit_box2">
        <h2>学校通知·公告</h2>
        <a href="./xxtg/"><img src="./images/more1.gif" /></a>
    </div>
    <ul>
        <li>
            <a href="./xytg/zsdw/wlxxzx/wlzx/202511/t20251122_621235.shtml"
               target="_blank"
               title="【网络中心】关于防范OA邮件及钓鱼邮件攻击的紧急提醒（二）">
                【网络中心】关于防范OA邮件及钓鱼邮件...
            </a>
            <span>11-22</span>
        </li>
        <!-- More items -->
    </ul>
</div>
```

**URL Patterns:**
- School notices: `./xxtg/znbm/[部门]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`
- College notices: `./xytg/zsdw/[部门]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`

**Sample Departments:**
- 网络中心 (wlxxzx/wlzx) - Network Center
- 本科生院 (jwc) - Undergraduate School
- 研究生院 (yjsy) - Graduate School
- 财务处 (jcc) - Finance Office
- 工会 (xgh) - Union

---

### 3. 部门亮点资讯 (Department Highlights)

**Section Location:** `div.list_box1.f10`
**Title Element:** `.tit_box2 h2` containing "部门亮点资讯"
**More Link:** `./bmxw/`

**URL Pattern:**
- Format: `./bmxw/znbm/[部门]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`
- Example: `./bmxw/znbm/xxhb/202511/t20251125_621384.shtml`

---

### 4. 重点关注 (Key Focus)

**Section Location:** `div.bar_list_box`
**Title Element:** `.bar_tit_box1 h2` with link to `./zdgz/`

**CSS Selector:**
- Container: `div.bar_list_box`
- List items: `div.bar_list_box ul li`
- Links: `div.bar_list_box ul li a`

---

### 5. 图片新闻 (Picture News / Slider)

**Section Location:** `div.pic_news`
**Slider ID:** `#main-photo-slider`

**Structure:**
```html
<div class="panel" title="武汉理工大学·中国车谷产业生态合作大会举行">
    <div class="wrapper">
        <a href="https://news.whut.edu.cn/zhxw/202510/t20251018_1351908.shtml" target="_blank">
            <img src="./tpxw/202510/W020251018621530834469.jpg" />
        </a>
        <div class="photo-meta-data">
            <a href="...">武汉理工大学·中国车谷产业生态合作大会举行</a>
        </div>
    </div>
</div>
```

**CSS Selectors:**
- Panels: `div.panel`
- Title: `div.panel::attr(title)`
- Image: `div.panel img::attr(src)`
- Link: `div.panel a::attr(href)`
- Caption: `div.photo-meta-data a::text`

---

### 6. 滚动新闻 (Scrolling News)

**Section Location:** `div.scroll_news`
**ID:** `#news`

**Structure:**
```html
<div id="news">
    <ul>
        <li>
            <a href="./xytg/zsdw/wlxxzx/wlzx/202511/t20251122_621235.shtml"
               target="_blank"
               title="【网络中心】关于防范OA邮件及钓鱼邮件攻击的紧急提醒（二）">
                【网络中心】关于防范OA邮件及钓鱼邮件攻击的紧急提醒（二）
            </a>
            <!-- Multiple links per <li> -->
        </li>
    </ul>
</div>
```

**Note:** Multiple news items per `<li>`, separated by `&nbsp;`

---

## Date Format

**Display Format:** `MM-DD` (e.g., "11-28", "11-27")
**URL Format:** `YYYYMMDD` (e.g., "20251128")

**Parsing Strategy:**
- Extract from URL: `t(\d{8})_` pattern
- Or extract from span and infer year (current year)

---

## Article URL Structures

### Types:

1. **Comprehensive News (External):**
   - Domain: `news.whut.edu.cn`
   - Path: `/zhxw/YYYYMM/tYYYYMMDD_XXXXXXX.shtml`
   - Full URL required

2. **School Notices (Relative):**
   - Path: `./xxtg/znbm/[dept]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`
   - Base: `http://i.whut.edu.cn`

3. **College Notices (Relative):**
   - Path: `./xytg/zsdw/[dept]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`
   - Base: `http://i.whut.edu.cn`

4. **Department News (Relative):**
   - Path: `./bmxw/znbm/[dept]/YYYYMM/tYYYYMMDD_XXXXXX.shtml`
   - Base: `http://i.whut.edu.cn`

---

## Recommended Scraping Strategy

### Phase 1: Homepage News Lists

Start with homepage to get latest news from all categories:

1. **综合新闻 (Comprehensive News)**
   - Selector: `div.media_whut ul li`
   - 10 items, links to external domain

2. **学校通知·公告 (School Notices)**
   - Selector: `div.list_box1:first ul li`
   - 20-25 items, relative paths

3. **部门亮点资讯 (Department News)**
   - Selector: `div.list_box1.f10 ul li`
   - 15-20 items

### Phase 2: Category Pages

Follow "more" links to get complete archives:

- http://news.whut.edu.cn/zhxw/ - Comprehensive news archive
- http://i.whut.edu.cn/xxtg/ - School notices archive
- http://i.whut.edu.cn/bmxw/ - Department news archive

### Phase 3: Article Detail Pages

Parse individual articles (structure TBD - need to inspect article page)

---

## Spider Implementation Checklist

### Start URLs:
```python
start_urls = [
    'http://i.whut.edu.cn',  # Homepage
    'http://news.whut.edu.cn/zhxw/',  # Comprehensive news archive
    'http://i.whut.edu.cn/xxtg/',  # School notices
    'http://i.whut.edu.cn/bmxw/',  # Department news
]
```

### Allowed Domains:
```python
allowed_domains = ['whut.edu.cn', 'i.whut.edu.cn', 'news.whut.edu.cn']
```

### CSS Selectors to Update:

```python
# Homepage - Comprehensive News
'div.media_whut ul li'
'div.media_whut ul li a::attr(href)'
'div.media_whut ul li a::attr(title)'
'div.media_whut ul li span::text'  # Date

# Homepage - School Notices
'div.list_box1 ul li'
'div.list_box1 ul li a::attr(href)'
'div.list_box1 ul li a::attr(title)'
'div.list_box1 ul li span::text'

# Homepage - Department News
'div.list_box1.f10 ul li'
```

---

## Important Notes

1. **Relative URLs:** Many links use relative paths (`./xxtg/...`)
   - Use `response.urljoin()` to convert to absolute URLs

2. **Multiple Domains:**
   - Main portal: `i.whut.edu.cn`
   - News site: `news.whut.edu.cn`
   - Ensure both are in `allowed_domains`

3. **Date Extraction:**
   - Dates are in `<span>` tags: `MM-DD` format
   - Can also extract from URL: `tYYYYMMDD_` pattern
   - Recommended: Extract from URL for full date

4. **Title Truncation:**
   - Display text often truncated with "..."
   - Use `title` attribute for full title

5. **Categories:**
   - Infer from URL path:
     - `/zhxw/` → "综合新闻"
     - `/xxtg/` → "学校通知公告"
     - `/bmxw/` → "部门新闻"
     - `/xytg/` → "学院通知公告"

6. **Department Tags:**
   - Extract from article title: `【部门名】content`
   - Regex: `【(.+?)】`

---

## Next Steps

1. ✅ Homepage structure documented
2. ⏳ Inspect article detail page structure
3. ⏳ Identify pagination structure on archive pages
4. ⏳ Update spider selectors
5. ⏳ Test with scrapy shell

---

## Testing Commands

```bash
# Test homepage
scrapy shell http://i.whut.edu.cn

# In shell:
response.css('div.media_whut ul li a::attr(title)').getall()
response.css('div.media_whut ul li a::attr(href)').getall()
response.css('div.media_whut ul li span::text').getall()

# Test comprehensive news list
response.css('div.list_box1 ul li a::attr(title)').getall()

# Test URL joining
response.urljoin('./xxtg/znbm/jwc/202511/t20251128_622234.shtml')
```

---

**Last Updated:** 2024-11-28
**Status:** Homepage analysis complete, article detail page pending

---

## Article Detail Page Structure

**Sample URL:** https://news.whut.edu.cn/zhxw/202511/t20251128_1358589.shtml

### Page Metadata (Hidden divs, lines 203-212)

```html
<div id="WebsiteId" style="display:none;">208</div>
<div id="ColumnId" style="display:none;">8885</div>
<div id="ColumnName" style="display:none;">综合新闻</div>
<div id="NewsArticleID" style="display:none;">1358589</div>
<div id="NewsArticleTitle" style="display:none;">【师道大讲堂】学校举行...</div>
<div id="NewsArticleSource" style="display:none;">教师工作部、宣传部</div>
<div id="NewsArticleAuthor" style="display:none;"></div>
<div id="NewsArticlePubDay" style="display:none;">2025-11-28</div>
```

### HTML Structure

```html
<div class="content index">
    <!-- Breadcrumb -->
    <div class="wz">
        <a href="../../" title="首页">首页</a>&nbsp;&gt;&nbsp;
        <a href="../" title="综合新闻">综合新闻</a>
    </div>
    
    <!-- Article Title & Metadata -->
    <div class="xl-tie">
        <h2>【师道大讲堂】学校举行全国"最美教师"姜德生院士事迹报告会</h2>
        <p>
            <span>发布：2025-11-28 08:36</span>
            <span>来源：教师工作部、宣传部</span>
        </p>
    </div>
    
    <!-- Article Content -->
    <div class="con-box">
        <div class="neir">
            <div class="view TRS_UEDITOR trs_paper_default trs_web">
                <!-- Article paragraphs -->
                <p>新闻网讯 11月27日下午，学校...</p>
                <p><img src="./W020251128323318642282.jpg" /></p>
                <p>...</p>
                <!-- Credits at end -->
                <p style="text-align: right;">
                    文字：袁霞；编辑：谢昕恬；审核：郭永琪、关帅锋、房海宁
                </p>
            </div>
            
            <!-- Attachments (if any) -->
            <div class="apendix"></div>
        </div>
    </div>
</div>
```

### CSS Selectors for Article Page

```python
# Title
'div.xl-tie h2::text'

# Publish Date & Time
'div.xl-tie p span:nth-child(1)::text'  # "发布：2025-11-28 08:36"

# Source/Department
'div.xl-tie p span:nth-child(2)::text'  # "来源：教师工作部、宣传部"

# Breadcrumb/Category
'div.wz a.CurrChnlCls::text'

# Main Content
'div.neir div.view p'  # All paragraphs
'div.neir div.view'    # Entire content block (recommended)

# Images in content
'div.neir div.view img::attr(src)'

# Credits (at end of article)
'div.neir div.view p[style*="text-align: right"]::text'

# Metadata (hidden but useful)
'div#NewsArticleID::text'
'div#NewsArticleTitle::text'
'div#NewsArticleSource::text'
'div#NewsArticleAuthor::text'
'div#NewsArticlePubDay::text'
```

### Date & Time Parsing

**Display Format:** "发布：2025-11-28 08:36"

**Extraction:**
```python
import re
date_str = response.css('div.xl-tie p span:nth-child(1)::text').get()
# Extract: "发布：2025-11-28 08:36"
date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', date_str)
if date_match:
    published_at = datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M')
```

### Source/Author Extraction

**Format:** "来源：教师工作部、宣传部"

**Extraction:**
```python
source_str = response.css('div.xl-tie p span:nth-child(2)::text').get()
# Extract: "来源：教师工作部、宣传部"
source = source_str.replace('来源：', '').strip()
```

### Content Extraction

**Recommendation:** Extract entire content block and clean HTML

```python
# Get all content HTML
content_html = response.css('div.neir div.view').get()

# Or get text only (loses formatting)
paragraphs = response.css('div.neir div.view p::text').getall()
content = '\n\n'.join(paragraphs)

# Extract summary (first paragraph without images)
summary = response.css('div.neir div.view p:not(:has(img))::text').get()
```

### Image Extraction

**Image URLs:** Relative paths like `./W020251128323318642282.jpg`

**Full URL construction:**
```python
img_urls = response.css('div.neir div.view img::attr(src)').getall()
# Convert to absolute URLs
images = [response.urljoin(img) for img in img_urls]
```

### Category Extraction

**Options:**
1. From breadcrumb: `div.wz a.CurrChnlCls::text`
2. From hidden metadata: `div#ColumnName::text`
3. From URL path: `/zhxw/` → "综合新闻"

---

## Complete Spider Selector Reference

### Homepage List Items

```python
# Comprehensive News
response.css('div.media_whut ul li a::attr(href)').getall()
response.css('div.media_whut ul li a::attr(title)').getall()
response.css('div.media_whut ul li span::text').getall()

# School Notices
response.css('div.list_box1:nth-child(1) ul li a::attr(href)').getall()
response.css('div.list_box1:nth-child(1) ul li a::attr(title)').getall()
response.css('div.list_box1:nth-child(1) ul li span::text').getall()
```

### Article Detail Page

```python
# Title
title = response.css('div.xl-tie h2::text').get()

# Date
date_text = response.css('div.xl-tie p span:contains("发布")::text').get()
# Parse: "发布：2025-11-28 08:36"

# Source
source_text = response.css('div.xl-tie p span:contains("来源")::text').get()
# Parse: "来源：教师工作部、宣传部"

# Category
category = response.css('div.wz a.CurrChnlCls')[-1].css('::text').get()

# Content
content = response.css('div.neir div.view').get()
# Or just text:
content_text = '\n\n'.join(response.css('div.neir div.view p::text').getall())

# Images
images = [response.urljoin(img) for img in response.css('div.neir div.view img::attr(src)').getall()]

# Summary (first paragraph)
summary = response.css('div.neir div.view p:not(:has(img))::text').get()
```

---

## Sample Scraped Data Structure

```json
{
    "title": "【师道大讲堂】学校举行全国"最美教师"姜德生院士事迹报告会",
    "content": "新闻网讯 11月27日下午，学校在会议中心301报告厅举行...",
    "summary": "新闻网讯 11月27日下午，学校在会议中心301报告厅举行师道大讲堂暨全国"最美教师"姜德生院士事迹报告会...",
    "source_url": "https://news.whut.edu.cn/zhxw/202511/t20251128_1358589.shtml",
    "source_name": "武汉理工大学新闻经纬",
    "published_at": "2025-11-28T08:36:00",
    "author": "教师工作部、宣传部",
    "images": [
        "https://news.whut.edu.cn/zhxw/202511/W020251128323318642282.jpg",
        "https://news.whut.edu.cn/zhxw/202511/W020251128323318751382.jpg"
    ],
    "attachments": [],
    "category": "综合新闻",
    "tags": ["师道大讲堂", "最美教师"]
}
```

---

## Implementation Priority

### Phase 1: Basic Scraping (Start Here)
1. ✅ Homepage news list extraction
2. ⏳ Article detail page extraction
3. ⏳ Date/source parsing
4. ⏳ Content cleaning

### Phase 2: Enhancement
1. Image downloading (optional)
2. Archive page pagination
3. Multiple categories
4. Attachment handling

### Phase 3: Robustness
1. Error handling
2. Retry logic
3. Data validation
4. Deduplication verification

---

**Analysis Complete!** ✅
**Last Updated:** 2024-11-28
**Ready for spider implementation**
