# Web Crawler — System Design Brainstorm

> Snapshot of the Confluence page [Web Crawler — System Design Brainstorm](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/6291457), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

# References

https://www.hellointerview.com/learn/system-design/problem-breakdowns/web-crawler 

https://browserbeam.com/blog/build-web-crawler/ 

https://www.systemdesignhandbook.com/guides/design-a-web-crawler-system-design/ 

https://arxiv.org/html/2602.24262v4 

‌

## 1. What is a Web Crawler?

A web crawler is a program that automatically visits web pages, downloads their content, extracts useful information, and follows links to discover additional pages.

### Core process

1. Start with a set of **seed URLs**.
2. Add them to a **URL frontier/queue**.
3. Fetch a URL.
4. Extract the page's text/content.
5. Extract links from the page.
6. Add newly discovered URLs to the queue.
7. Repeat until there are no more URLs to crawl.

---

# 2. Requirements

### Functional

* Crawl the web starting from seed URLs.
* Download web pages.
* Extract and store text/content.
* Discover and crawl linked URLs.
* Avoid crawling the same URL repeatedly.

### Non-functional

* **Scalable:** support a very large number of URLs.
* **Fault tolerant:** failures should not cause progress to be lost.
* **Polite:** respect `robots.txt` and avoid overwhelming websites.
* **Efficient:** process URLs concurrently.

### Out of scope

* JavaScript/dynamic content.
* Authentication/login-required pages.
* Images, videos and other non-text content.
* Processing the extracted text (e.g. training an ML model).

---

# 3. Basic Architecture

```
Seed URLs
    ↓
URL Frontier / Queue
    ↓
Crawler Workers
    ↓
Fetch Web Page
    ↓
Extract Text + Links
    ↓              ↓
Store Content      New URLs
                      ↓
                 URL Frontier
```

### Main components

**URL Frontier / Queue**

* Stores URLs waiting to be crawled.
* Allows many crawler workers to process URLs concurrently.
* Examples: SQS, Kafka, Redis.

**Crawler Workers**

* Take URLs from the queue.
* Fetch pages.
* Extract text and links.
* Store the results.
* Add discovered URLs back to the queue.

**Storage**

* Stores raw HTML and/or extracted text.
* Object storage such as S3 is suitable for large amounts of data.

**Metadata Database**

* Stores information about URLs and crawl state.
* Example fields:

    * URL
    * crawl status
    * last crawl time
    * content location
    * content hash
    * crawl depth
    

---

# 4. Fault Tolerance

A crawler can fail for many reasons:

* Website is unavailable.
* Network timeout.
* DNS failure.
* Crawler crashes.
* Page is too large.
* Parsing fails.

### Solution: Pipeline the system

Instead of having one worker do everything:

```
URL Queue
    ↓
Fetcher
    ↓
Raw HTML Storage
    ↓
Parsing Queue
    ↓
Parser
    ↓
Extracted Text Storage
```

This means a failure in one stage does not require repeating the entire process.

For example, if parsing fails, we can retry parsing the HTML already stored rather than downloading the webpage again.

### Queues

Messages should contain a **URL/ID**, not the actual HTML.

The queue handles task coordination, while large data is stored in object storage.

### Retries

* Retry temporary failures.
* Use **exponential backoff** to avoid repeatedly hitting a failing server.
* Use a **dead-letter queue (DLQ)** for URLs that repeatedly fail.
* If a worker crashes, another worker should be able to process the URL again.

---

# 5. Politeness & robots.txt

A crawler should not overload websites.

### robots.txt

Before crawling a domain, check its `robots.txt`.

It can specify which paths crawlers are allowed/disallowed from accessing.

Example:

```
User-agent: *
Disallow: /private/
Crawl-delay: 10
```

The crawler should:

* Respect disallowed paths.
* Respect crawl delays where applicable.
* Avoid sending too many requests to one domain.

### Rate limiting

Use **per-domain rate limiting** rather than one global limit.

For example:

```
example.com → max 1 request/second
site2.com   → max 1 request/second
site3.com   → max 1 request/second
```

This allows thousands of domains to be crawled concurrently while remaining polite to each individual domain.

A distributed rate limiter/lock (e.g. Redis) can coordinate multiple crawler workers.

---

# 6. URL Deduplication

The same URL can be discovered many times.

Example:

```
<https://example.com>
<https://example.com/>
<https://example.com>
```

Before adding a URL to the queue, check whether it has already been seen.

### URL-level deduplication

Maintain a database/index of discovered URLs.

```
if URL already exists:
    skip
else:
    add URL
```

This prevents unnecessary crawling.

---

# 7. Content Deduplication

Different URLs can return identical content.

Example:

```
example.com/page
example.org/page
```

Both could contain exactly the same page.

After downloading a page:

1. Calculate a hash of its content.
2. Check whether that hash already exists.
3. If it does, the content has already been processed.
4. Otherwise, store it.

```
HTML
 ↓
Hash
 ↓
Already exists? ── Yes → Skip duplicate processing
       │
       No
       ↓
Store + Parse
```

This can significantly reduce unnecessary processing.

---

# 8. Crawler Traps

A **crawler trap** is a website structure that causes the crawler to continuously discover new pages without making useful progress.

Examples:

* Pages linking to themselves.
* Infinite URL parameters.
* Calendar pages generating unlimited dates.
* Sites generating millions of similar URLs.

### Solutions

* Set a maximum crawl depth.
* Limit the number of URLs crawled per domain.
* Detect repeated URL patterns.
* Deduplicate URLs.
* Set limits on page size and crawl time.

---

# 9. Scaling

A single crawler cannot process billions of pages efficiently.

Use **multiple crawler workers** running in parallel:

```
              ┌→ Crawler 1 ─→ Web
URL Queue ────┼→ Crawler 2 ─→ Web
              ├→ Crawler 3 ─→ Web
              └→ Crawler N ─→ Web
```

The queue distributes work between workers.

### Key principle

The crawler is primarily **I/O-bound**, because it spends much of its time waiting for:

* DNS responses
* Network connections
* Web servers
* HTTP responses

Therefore, each worker can maintain many concurrent connections.

### Horizontal scaling

Instead of making one crawler extremely powerful:

```
1 huge crawler
```

use:

```
Many crawler workers
```

This allows throughput to increase as the number of workers increases.

---

# 10. DNS

DNS can become a bottleneck at large scale because every domain needs to be resolved to an IP address.

### Optimisations

* Cache DNS responses.
* Reuse DNS results for multiple URLs on the same domain.
* Use multiple DNS providers if necessary.
* Monitor DNS latency and failures.

---

# 11. Storage

Separate **large content** from **metadata**.

### Object storage

Use something like S3 for:

* Raw HTML
* Extracted text

### Metadata database

Store:

* URL
* URL status
* crawl timestamps
* content hash
* storage location
* crawl depth
* domain information

This avoids putting large HTML documents directly into the database or queue.

---

# 12. Recommended Overall Architecture

```
                       ┌──────────────┐
                       │  Seed URLs   │
                       └──────┬───────┘
                              ↓
                    ┌──────────────────┐
                    │   URL Frontier   │
                    │      Queue       │
                    └────────┬─────────┘
                             ↓
              ┌────────────────────────────┐
              │      Crawler Workers       │
              │                            │
              │ • DNS lookup/cache         │
              │ • robots.txt check         │
              │ • rate limiting            │
              │ • fetch webpage             │
              └────────────┬───────────────┘
                           ↓
                    ┌──────────────┐
                    │  Raw HTML    │
                    │    Storage   │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Parsing Queue │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Parser       │
                    │              │
                    │ • Extract text│
                    │ • Extract URLs│
                    └──────┬───────┘
                           ↓
              ┌─────────────────────────┐
              │ Extracted Text Storage  │
              └─────────────────────────┘

          ┌──────────────────────────────┐
          │      Metadata Database       │
          │                              │
          │ URL • status • hash          │
          │ crawl time • depth • domain │
          └──────────────────────────────┘

          ┌──────────────────────────────┐
          │ Redis / Rate Limiter / Cache │
          │                              │
          │ • Domain locks               │
          │ • Rate limiting              │
          │ • DNS caching                │
          └──────────────────────────────┘
```

# 13. Key Design Principles to Remember

If explaining this system in a presentation/interview, the most important points are:

1. **Queue the URLs** so crawling can be distributed across many workers.
2. **Separate fetching and parsing** so each stage can scale and fail independently.
3. **Store large HTML/text in object storage**, not in the queue.
4. **Use a metadata database** to track crawl state.
5. **Deduplicate URLs** before crawling them.
6. **Hash content** to detect duplicate pages.
7. **Respect robots.txt and rate-limit per domain** to be polite.
8. **Retry failed requests** with exponential backoff and a DLQ.
9. **Use multiple crawler workers** for horizontal scalability.
10. **Cache DNS results** because DNS can become a bottleneck.
11. **Limit crawl depth/domain activity** to protect against crawler traps.
12. **Monitor the queues and workers** so failures and bottlenecks can be detected.

The **core architecture you actually want to understand** is:

> **URL queue → crawler workers → fetch HTML → store HTML → parse → store text + discover URLs → deduplicate → put new URLs back into queue**

Then your major design concerns are **scalability, fault tolerance, politeness, and deduplication**.

# Expanding on that Design

The basic architecture is the foundation. Our version should behave more like a **mini search-engine crawler**, with intelligent scheduling, adaptive crawling, strong deduplication, and the ability to continuously discover new parts of the web.

The biggest conceptual shift is:

> **Don't think of it as a scraper. Think of it as a distributed system whose job is to continuously discover, prioritise, and understand the web.**

### 1. Don't use a fixed crawl depth

The original suggestion of “crawl to depth 15–20” is simple, but it unnecessarily limits discovery.

Instead, give URLs a **priority score**.

For example:

```
Priority =
    domain importance
  + link popularity
  + freshness
  + depth
  + historical success rate
  - crawl cost
```

Then your frontier becomes a **priority queue**, rather than FIFO.

That means the crawler can decide:

> “This URL is highly likely to lead to valuable new content, so crawl it first.”

This is much more interesting than blindly following links.

---

### 2. Build a continuously expanding frontier

Instead of:

```
Seeds → Crawl → Finish
```

build:

```
Seeds
  ↓
Discover URLs
  ↓
Normalise URLs
  ↓
Deduplicate
  ↓
Score URLs
  ↓
Priority Frontier
  ↓
Crawl
  ↓
Discover MORE URLs
  └───────────────↺
```

Every page becomes a source of new knowledge about the web.

You can also maintain different queues:

```
HIGH PRIORITY
News / important domains / highly connected pages

NORMAL
General web pages

LOW PRIORITY
Low-confidence or low-value pages
```

This lets you maximise **useful coverage**, rather than simply maximising request count.

---

### 3. Crawl the web intelligently, not uniformly

One of the biggest opportunities is **adaptive crawling**.

Suppose your crawler notices:

```
Wikipedia
→ thousands of useful links
→ high success rate
→ frequently updated
→ highly connected
```

versus:

```
random-site.com
→ 80% broken URLs
→ duplicate content
→ almost no outbound links
```

Your crawler shouldn't treat them identically.

Track domain-level statistics:

```
Domain
├── pages discovered
├── pages successfully crawled
├── average response time
├── failure rate
├── duplicate rate
├── average content value
├── last crawl time
└── link discovery rate
```

Then dynamically adjust how aggressively you crawl each domain.

---

# 4. Make the crawler self-optimising

This is where I'd try to differentiate your project.

Instead of hard-coding:

> “crawl every domain at X rate”

let the system learn which domains are productive.

For example:

```
Domain A
1000 URLs → 900 useful pages
→ increase priority

Domain B
1000 URLs → 20 useful pages
→ decrease priority
```

You could call this a **crawl efficiency score**.

Something like:

```
crawl_efficiency =
    useful_pages / requests
```

Then use that metric to influence scheduling.

You don't even need machine learning. A simple scoring algorithm would already demonstrate sophisticated system design.

---

# 5. Use multiple types of deduplication

Don't stop at:

> “Have I seen this URL?”

You can have several layers.

### URL deduplication

Normalise:

```
HTTP vs HTTPS
trailing /
www vs non-www
URL fragments
tracking parameters
case sensitivity
```

Then check whether the canonical URL has already been crawled.

### Content deduplication

Hash the downloaded content:

```
SHA-256(content)
```

If the hash already exists:

```
duplicate → don't parse/store again
```

### Near-duplicate detection

This is where it gets really interesting.

Two pages might differ by:

```
ads
navigation
timestamps
recommendations
```

but contain essentially the same content.

You could eventually use:

* SimHash
* MinHash
* locality-sensitive hashing
* embeddings

to detect **near-duplicate pages**.

That's a legitimately interesting extension.

---

# 6. Build a web graph

This is one of the coolest additions.

Instead of thinking of pages independently:

```
Page A
Page B
Page C
```

store their relationships:

```
A ─────→ B
│
├──────→ C
│
└──────→ D
```

Now your crawler is building a **graph of the web**.

Store:

```
Page
 ├── URL
 ├── domain
 ├── content hash
 └── discovered_at

Link
 ├── source_page
 └── destination_page
```

This allows you to calculate things like:

* most connected domains
* highly referenced pages
* communities of websites
* authority scores
* link structure
* discovery paths

And suddenly your project isn't merely:

> “I made a web scraper.”

It's:

> **“I built a distributed web discovery and indexing system.”**

Much stronger.

---

# 7. Add a crawler trap detector

Instead of only saying:

> “Stop at depth 20.”

detect suspicious behaviour.

For example:

```
example.com/calendar?date=2026-01-01
example.com/calendar?date=2026-01-02
example.com/calendar?date=2026-01-03
...
```

Your crawler can detect:

* rapidly increasing URLs
* repeated URL patterns
* extremely deep paths
* huge numbers of parameters
* low content diversity
* repeated templates

Then automatically reduce the priority or block that pattern.

That's much more intelligent than a simple depth limit.

---

# 8. Make crawling incremental

The original system assumes a one-time crawl.

A much better system could continuously maintain the web index.

Store:

```
last_crawled
last_modified
crawl_frequency
content_hash
```

Then determine:

> “When should I crawl this URL again?”

A frequently changing news page might be crawled every few minutes.

A static documentation page might be crawled once a month.

So you get:

```
URL Scheduler
      ↓
How likely is this page to have changed?
      ↓
Schedule next crawl
```

This is basically how you turn a crawler into a **living web index**.

---

# 9. HTTP should work for you

You can also make the crawler much more efficient by properly using HTTP.

For example:

### HEAD requests

Check metadata before downloading a huge resource.

### ETags

If a server provides:

```
ETag: "abc123"
```

save it.

Next crawl:

```
If-None-Match: "abc123"
```

If nothing changed, the server can respond:

```
304 Not Modified
```

You don't need to download the entire page again.

### Last-Modified

Similarly:

```
If-Modified-Since
```

can prevent unnecessary downloads.

These optimisations become **massive** at web scale.

---

# 10. Don't let one domain dominate the crawler

Imagine your crawler discovers:

```
Wikipedia → 50 million URLs
```

If you simply dump those URLs into your frontier, Wikipedia could consume your entire crawler.

You need **fair scheduling**.

Conceptually:

```
              Frontier
                  ↓
        ┌──────────────────┐
        │ Domain Scheduler │
        └──────────────────┘
          ↓      ↓      ↓
       site A  site B  site C
```

Each domain gets an appropriate amount of crawl capacity.

This also makes your politeness system much easier to reason about.

---

# 11. Use backpressure

This is another very important distributed-systems concept.

Imagine:

```
Crawler → 50,000 pages/sec
             ↓
         Parser
         5,000/sec
```

Your queue explodes.

Instead, monitor queue depth:

```
Parser queue ↑↑
      ↓
Reduce crawler throughput
```

If the parser catches up:

```
Parser queue ↓
      ↓
Increase crawler throughput
```

That's **backpressure**.

Your pipeline becomes self-regulating rather than simply throwing more workers at every problem.

---

# 12. Give yourself observability

If this is an actual university project, this could make the demo **so much better**.

Have a dashboard showing:

```
┌─────────────────────────────────────┐
│          CRAWLER STATUS             │
├─────────────────────────────────────┤
│ Pages crawled       4,821,391       │
│ URLs discovered     18,293,442      │
│ Success rate        94.2%           │
│ Duplicate rate      31.7%           │
│ Pages/sec            1,240          │
│ Active domains       84,201         │
│ Queue depth          293,821        │
│ Failed requests      281,293        │
└─────────────────────────────────────┘
```

Then visualise the web graph.

Even if your actual crawl is relatively small, the **engineering architecture** demonstrates that it could scale.

# 13. The architecture I'd actually aim for

I'd evolve the basic design into:

```
                         ┌───────────────┐
                         │   Seed URLs   │
                         └───────┬───────┘
                                 ↓
                       ┌───────────────────┐
                       │ URL Normalisation │
                       └─────────┬─────────┘
                                 ↓
                       ┌───────────────────┐
                       │ Deduplication     │
                       └─────────┬─────────┘
                                 ↓
                       ┌───────────────────┐
                       │ Priority Frontier │
                       └─────────┬─────────┘
                                 ↓
                    ┌────────────────────────┐
                    │   Domain Scheduler     │
                    │                        │
                    │ robots.txt             │
                    │ rate limiting          │
                    │ fairness               │
                    └────────────┬───────────┘
                                 ↓
              ┌──────────────────────────────────┐
              │          Crawler Workers         │
              │                                  │
              │ DNS → HTTP → HTML → validation  │
              └────────────────┬─────────────────┘
                               ↓
                    ┌──────────────────┐
                    │   Raw Storage     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Parsing Workers   │
                    └───────┬──────────┘
                            ↓
             ┌─────────────────────────────┐
             │ Text + Metadata + Web Graph │
             └─────────────┬───────────────┘
                           ↓
                  ┌───────────────────┐
                  │ Content Dedup     │
                  │ Near-Dedup        │
                  └───────────────────┘
                           ↓
                 New URLs discovered
                           │
                           └──────────────→ Frontier ↺

              ┌─────────────────────────────┐
              │   Monitoring / Dashboard   │
              └─────────────────────────────┘
```

### 3 Design Levels

**MVP**

* URL frontier
* crawler workers
* HTML fetching
* text extraction
* URL discovery
* URL deduplication
* robots.txt
* basic rate limiting
* storage

**Advanced** 

* distributed workers
* priority queue
* domain scheduler
* retries + DLQ
* content hashing
* DNS caching
* crawl-depth/trap detection
* monitoring
* backpressure

**Exceptional**

* adaptive crawl prioritisation
* incremental recrawling
* ETag/Last-Modified support
* near-duplicate detection
* web graph
* crawl efficiency scoring
* intelligent domain scheduling
* dynamic frontier prioritisation
* visual crawler dashboard

**That last level is where I'd aim if you want this project to stand out.**

And importantly, you don't need to implement _every_ advanced idea. A smaller system with **3–4 genuinely well-designed intelligent components** will look much more impressive than 20 buzzwords slapped onto an architecture.
