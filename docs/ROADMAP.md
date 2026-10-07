# Roadmap

## V1 Status

The first version establishes the complete local tracking workflow.

Completed functionality includes:

- Amazon Brazil product tracking
- ASIN extraction
- support for `/dp/{ASIN}` URLs
- support for `/gp/product/{ASIN}` URLs
- title parsing
- price parsing
- rating parsing
- product image extraction and display
- SQLite persistence
- `Product` and `ProductSnapshot` models
- historical observations
- manual refresh
- price-history visualization with Matplotlib
- product removal
- PySide6 desktop GUI

V1 is considered feature-complete for its intended scope.

---

# V2 Goals

V2 should focus on extensibility, reliability, and active monitoring rather than simply adding more isolated features.

## 1. Final UI and UX polish

Before expanding the product significantly:

- refine spacing and alignment
- improve list-item presentation
- improve empty states
- improve loading feedback
- prevent controls from appearing active when no product is selected
- improve chart formatting
- review error dialogs and destructive-action confirmation
- create final portfolio screenshots

This should remain polish rather than a major GUI rewrite.

---

## 2. Provider abstraction

This is the most important architectural change before adding several marketplaces.

Current Amazon-specific logic should evolve toward a common provider interface.

Conceptually:

```text
ProductProvider
 ├── AmazonProvider
 ├── AliExpressProvider
 ├── ShopeeProvider
 ├── MercadoLivreProvider
 └── TemuProvider
```

Provider responsibilities may include:

- determining whether a URL is supported
- extracting the marketplace product ID
- fetching the page or data source
- parsing product metadata
- returning common domain objects

The service layer should not need marketplace-specific branching throughout the application.

### Recommended approach

Add only one new provider first.

Suggested order:

1. refactor Amazon behind the provider abstraction
2. add one additional marketplace
3. validate that GUI, service, repository, and database require minimal changes
4. only then add more providers

Possible marketplaces:

- AliExpress
- Shopee
- Mercado Livre
- Temu

---

## 3. Target price

Add user-defined target prices.

This introduces a new concept that is different from both `Product` and `ProductSnapshot`.

A possible model:

```python
ProductWatch(
    product_id=...,
    target_price=Decimal("90.00"),
    enabled=True,
)
```

Conceptually:

```text
Product
= marketplace item

ProductSnapshot
= observed marketplace state

ProductWatch
= how the user wants to monitor the product
```

This separation prevents user preferences from being mixed with marketplace data.

---

## 4. Background refresh

Target prices become significantly more useful when refreshes do not require manual interaction.

Possible approaches:

- `QThread`
- `QRunnable`
- `QThreadPool`
- scheduled refresh logic

Network operations should eventually move off the GUI thread.

Goals:

- prevent interface freezing
- refresh products periodically
- keep the GUI responsive
- support target-price monitoring

---

## 5. Notifications

Once target prices and background refresh exist:

```text
new snapshot
 ↓
current price <= target price?
 ↓
yes
 ↓
notify user
```

Potential notification mechanisms:

- desktop notification
- in-app notification
- optional email integration later

V2 does not need multiple notification systems initially.

---

## 6. Availability hardening

Availability is currently represented as unknown when the normal HTTP response does not expose reliable information.

V2 should investigate, in order:

1. static HTML
2. embedded structured data
3. embedded JSON/page state
4. internal public-facing page endpoints when appropriate
5. browser automation only when necessary

The application should continue preferring `None` over unreliable guesses.

---

## 7. Shipping fee

Shipping information is already represented in the snapshot model but is not reliably populated.

Potential goals:

- extract shipping fee when available
- distinguish free shipping from unknown shipping
- eventually calculate total effective purchase cost

```text
effective cost
= product price + shipping fee
```

---

## 8. Image cache

Current behavior may download the product image repeatedly.

Add a local cache such as:

```text
data/cache/
└── amazon/
    └── <ASIN>.jpg
```

Possible flow:

```text
image requested
 ↓
cached?
 ├── yes → load local file
 └── no  → download → save → load
```

Do not store large image BLOBs in SQLite unless a later requirement justifies it.

---

## 9. Snapshot deduplication

Repeated refreshes can currently produce identical snapshots.

Possible strategies:

- always preserve observations but enforce a minimum interval
- skip insertion when tracked values are unchanged
- store every observation but aggregate only for visualization

The decision should be based on what the tracker wants an observation to mean.

---

## 10. Error handling and resilience

Harden expected failure paths:

- invalid URLs
- unsupported providers
- HTTP timeout
- HTTP 403 / 429
- missing HTML elements
- malformed product pages
- product removed from marketplace
- image download failure
- database errors

The GUI should present useful errors rather than raw tracebacks.

---

## 11. Logging

Replace temporary debugging `print()` calls with structured logging.

Potential levels:

```text
DEBUG
INFO
WARNING
ERROR
```

Useful events include:

- product added
- product refreshed
- parser field missing
- HTTP failure
- provider selected
- database operation failure

---

## 12. Testing

Expand beyond ASIN tests.

### Parser tests

Use saved HTML fixtures so tests do not depend on live Amazon pages.

Example:

```text
tests/
└── fixtures/
    ├── amazon_book.html
    ├── amazon_keyboard.html
    └── amazon_missing_price.html
```

Test:

- title
- price
- rating
- image
- missing fields
- URL patterns

### Repository tests

Use a temporary SQLite database to test:

- insert
- update
- read
- history
- delete

### Service tests

Test workflows such as:

- new product
- existing product refresh
- invalid URL
- missing product

---

# Suggested V2 Order

A practical implementation order:

```text
1. Final V1 UI/documentation polish
        ↓
2. Strengthen tests
        ↓
3. Provider abstraction
        ↓
4. Add one second marketplace
        ↓
5. Target price / ProductWatch
        ↓
6. Background refresh
        ↓
7. Notifications
        ↓
8. Availability + shipping hardening
        ↓
9. Image cache
        ↓
10. Snapshot deduplication
        ↓
11. Additional marketplaces
```

This order keeps architectural changes ahead of feature multiplication.

---

# Deferred / Out of Scope for Early V2

These may be useful later but should not be priorities yet:

- cloud deployment
- multi-user accounts
- web frontend
- full SaaS architecture
- mobile application
- complex authentication
- large-scale distributed scraping
- microservices
- multiple notification channels
- advanced analytics

The project should first become a reliable, extensible desktop tracker.
