# Project Problem Statement: Automated Target-Market Mapping & Job Acquisition Engine

## 1. Background & Context

The global tech recruitment landscape is highly fragmented. For senior technical professionals specializing in enterprise-grade frontend frameworks like Angular, finding roles that offer a high degree of architectural maturity, strong engineering cultures, and premium compensation requires navigating an immense amount of market noise.

Major job boards (e.g., LinkedIn, Indeed, Naukri) are flooded with generic listings, irrelevant technology stacks (e.g., React or Vue roles mislabeled under generic "Frontend" tags), and high volumes of listings from traditional IT outsourcing firms or domestic startups that do not align with specific geographic, cultural, or financial goals. For a candidate with over 8 years of experience specializing in complex data systems, high-performance streaming (RxJS), and specific regulated verticals like Healthcare and Energy, manual searching is highly inefficient and structurally inadequate.

## 2. Core Problem Statement

How can we build an automated, programmatic engineering pipeline that dynamically discovers, filters, scores, and aggregates high-yield senior frontend job listings across **three distinct company categories** — each with its own priority, filtering rules, and output segmentation?

The current job-seeking workflow relies on manual, non-deterministic search patterns that fail to filter at source based on company origin, engineering tier, or granular architectural stack alignment. This results in hundreds of hours wasted evaluating low-alignment roles. There is an immediate need for an automated data extraction and NLP-driven scoring orchestrator to map the market and surface high-probability targets.

## 3. Three-Category Company Architecture

The engine organizes all target companies into **three top-level categories**, each driving a separate output segment and scraping priority:

### Category 1: Main Companies (Primary Target)
Foreign-headquartered product companies, GCCs, premium consultancies, global remote boards, and talent networks that connect to international roles. These are the **highest-priority** targets.

| Sub-Tier | Examples |
|---|---|
| Tier 1: Healthcare & Energy Domain Matches | GE HealthCare, Philips, Novartis, IQVIA, Baker Hughes, SLB |
| Tier 2: Big Tech & SaaS (Foreign HQ) | Microsoft, Intuit, SAP Labs, Adobe, Broadcom |
| Tier 3: Premium Digital Consultancies | Thoughtworks, Deloitte, PwC, Publicis Sapient |
| Tier 4: FinTech & Product GCCs | JPMorgan Chase, Goldman Sachs, Visa, S&P Global |
| Tier 5: Global Remote Boards | We Work Remotely, Remote OK, Wellfound |
| Tier 6: Global Talent Networks | Uplers, Turing, Toptal, Andela, BairesDev, Optimum |

### Category 2: Indian Product Companies (Secondary Target)
High-growth domestic unicorns and Indian-origin product companies. These offer strong engineering cultures and scale, but with different compensation structures than foreign GCCs.

| Sub-Tier | Examples |
|---|---|
| Tier 7: Domestic Unicorns & Product | Flipkart, Swiggy, Cred, Razorpay, Zerodha, PhonePe, Groww, Zepto, Paytm |

### Category 3: Service-Based Companies (Background Market Intelligence)
Traditional IT service firms. These are scraped for **market intelligence only** — to track which enterprise clients are outsourcing Angular migrations, spot emerging demand patterns, and understand the broader market pulse. They are **not** primary application targets.

| Sub-Tier | Examples |
|---|---|
| Tier 8: Traditional IT Service Firms | TCS, Infosys, Wipro, HCLTech, Cognizant, Accenture, Capgemini, Tech Mahindra |

> **Dynamic Lists**: All category and company lists are designed to be dynamically extensible. New companies can be added to any category at any time by simply updating the configuration, with no code changes required.

## 4. Technical Challenges & Obstacles

To solve this problem, the engine must overcome several distinct technical barriers:

- **JavaScript-Heavy Client Rendering**: Modern corporate career portals (specifically Workday, Lever, and Greenhouse) dynamically render job listings via client-side JavaScript. Traditional static HTTP scraping (e.g., standard `requests` or BeautifulSoup alone) returns blank or incomplete DOM trees.

- **Aggressive Anti-Bot Mechanisms**: High-value corporate portals employ rate-limiting, IP fingerprinting, and User-Agent tracking to block automated scraping, requiring sophisticated stealth and execution pacing.

- **Lack of Uniform Data Structures**: Job descriptions lack standard schemas. Key indicators like required years of experience, specific architectural patterns (NgRx, Signals), and testing requirements are buried deep within unformatted blocks of text.

- **Category-Aware Filtering**: The system must apply different filtering and scoring rules per category — strict gatekeeping for Category 1, relaxed geographic rules for Category 2 (all Indian cities accepted), and background-only data collection for Category 3.

## 5. System Objectives & Scope

The system will explicitly design and execute a modular data pipeline to address these challenges across five core boundaries:

1. **Automated JS-capable Extraction**: Use asynchronous browser automation (Playwright) backed by rotating identities and exponential backoff architectures to extract raw text data from JavaScript-rendered career nodes across all three company categories.

2. **Category-Aware Pipeline Routing**: Route each company's listings through category-specific filter chains — strict boundary gatekeeping for Category 1, relaxed domestic filters for Category 2, and minimal filtering for Category 3 (background intelligence).

3. **Strict Boundary Gatekeeping (Category 1)**: Implement automated filters that immediately terminate pipeline processing for any role failing basic geographic (Bengaluru/Hyderabad/Global Remote) or seniority (Senior/Lead/8+ YOE) benchmarks.

4. **Semantic Competency Matrix**: Execute a multi-category weighted keyword tallying algorithm that maps descriptions against five critical execution pillars: Core Stack, Modern Angular Features, State Management, Testing/Quality, and Scale/Enterprise Experience Markers.

5. **Segmented Actionable Synthesis**: Generate brief semantic justifications ("Why It Matches") and export clean, prioritized, schema-validated tabular records into **separate output files per category** (CSV/JSON) for immediate consumption.

## 6. Success Metrics

The performance and validity of the engine will be evaluated based on the following engineering targets:

| Metric | Target | Scope |
|---|---|---|
| **Precision Rate** | ≥ 90% | At least 90% of the roles exported to the Category 1 CSV must strictly match the target profile (8+ YOE, Foreign HQ Product/GCC/Premium Consultancy, Modern Angular stack) |
| **Category Isolation** | 100% | No company from one category should appear in another category's output file |
| **Data Completeness** | 100% | All extracted rows must capture the company tier tag, category label, and direct application link |
| **Dynamic Extensibility** | Yes | Adding a new company to any category requires only a config change — zero code modifications |
| **Background Intelligence** | Captured | Category 3 listings are stored separately for market trend analysis without polluting the primary output |