# Architecture

## Overview

ShoppingListTracker uses a layered structure to separate external data extraction, domain modeling, persistence, application logic, and presentation.

The current architecture is intentionally small enough for a desktop application while still separating responsibilities clearly.

```text
GUI
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

Amazon-specific data extraction follows a separate path:

```text
Amazon URL
 ↓
ASIN extraction
 ↓
AmazonFetcher
 ↓
HTML
 ↓
AmazonParser
 ↓
Product + ProductSnapshot
```

The service layer connects the scraping flow to persistence and the GUI.

---

## Main Responsibilities

### GUI

The PySide6 GUI is responsible for:

- receiving user input
- displaying tracked products
- showing product details
- displaying product images
- rendering price history with Matplotlib
- triggering add, refresh, and remove actions
- presenting confirmation dialogs and interface state

The GUI should not contain SQL or marketplace-specific parsing logic.

### Service

The service layer coordinates application-level operations such as:

- tracking a product
- refreshing a product
- retrieving product details
- listing tracked products
- removing a product

It acts as the boundary between the GUI and lower-level components.

### Repository

The repository layer translates between Python domain objects and SQLite rows.

It is responsible for:

- inserting products
- updating product metadata
- reading products
- inserting snapshots
- retrieving product history
- deleting products and their snapshots

### Database

SQLite is used for local persistence.

The main logical entities are:

```text
products
product_snapshots
```

A product has many snapshots.

```text
Product
 ├── ProductSnapshot
 ├── ProductSnapshot
 └── ProductSnapshot
```

---

## Domain Models

### Product

`Product` represents the stable identity and metadata of a tracked marketplace item.

Conceptually:

```python
Product(
    provider="amazon",
    external_id="0140424393",
    name="Paradise Lost",
    url="...",
    image_url="..."
)
```

Important fields:

- `provider`
- `external_id`
- `name`
- `url`
- `image_url`

The natural external identity of a product is:

```text
(provider, external_id)
```

For Amazon, `external_id` is the ASIN.

The database also uses an internal integer primary key for relationships.

### ProductSnapshot

`ProductSnapshot` represents an observation at a specific point in time.

Conceptually:

```python
ProductSnapshot(
    price=Decimal("70.11"),
    avg_rating=4.6,
    availability=None,
    shipping_fee=None,
    observed_at=...
)
```

Snapshots are append-oriented because historical observations are valuable even when the product already exists.

This separation allows the application to model:

```text
same product
different observations over time
```

without duplicating the product itself.

---

## Data Flow

### Adding a product

```text
User enters URL
 ↓
Service validates URL / extracts ASIN
 ↓
AmazonFetcher downloads HTML
 ↓
AmazonParser extracts product data
 ↓
Product + ProductSnapshot are created
 ↓
Repository inserts or updates Product
 ↓
Repository inserts ProductSnapshot
 ↓
GUI displays latest state
```

### Refreshing a product

```text
User selects product
 ↓
Service loads Product
 ↓
Stored URL is fetched again
 ↓
Latest data is parsed
 ↓
Product metadata is updated
 ↓
New ProductSnapshot is inserted
 ↓
GUI reloads details
 ↓
Matplotlib receives updated history
```

### Removing a product

```text
User selects product
 ↓
Confirmation dialog
 ↓
Snapshots are deleted
 ↓
Product is deleted
 ↓
GUI removes list item
 ↓
Details panel is cleared
```

---

## Engineering Decisions

### Decimal for money

Prices use Python's `Decimal` instead of `float`.

This avoids binary floating-point precision issues in monetary values.

```text
"111.43"
 ↓
Decimal("111.43")
```

### Money stored as SQLite TEXT

Monetary values are stored as textual decimal representations.

This preserves exact round-tripping between SQLite and `Decimal`.

```text
SQLite TEXT
 ↓
Decimal
```

Matplotlib may receive a temporary `float` conversion for visualization only.

### Product and ProductSnapshot are separate

The application distinguishes between product identity and temporal observations.

This makes price history a first-class part of the model rather than overwriting the previous price.

### `(provider, external_id)` as natural identity

The same external identifier may theoretically exist in different marketplaces.

Using both values keeps marketplace identity explicit:

```text
("amazon", "0140424393")
```

### `None` means unknown

Missing or unreliable data is represented as `None`.

For example:

```python
availability = None
```

means availability could not be determined reliably.

It does not mean the product is unavailable.

This avoids silently inventing data when scraping fails.

### Image URL instead of image BLOB

The database stores the image URL rather than full binary image data.

The GUI downloads the image when needed and converts the bytes to `QPixmap`.

This keeps SQLite focused on structured application data.

A future version may add a local filesystem cache.

### Structural ASIN extraction

Amazon URLs are parsed by recognized path structures instead of one fixed full URL.

Current supported patterns include:

```text
/dp/{ASIN}
/gp/product/{ASIN}
```

This makes ASIN extraction more resilient to URL variants.

---

## Current Trade-offs

### Synchronous network requests

HTTP requests currently run on the GUI thread.

Advantages:

- simpler V1 implementation
- easier debugging

Disadvantage:

- a slow request may temporarily freeze the interface

A later version should move network operations to Qt worker threads.

### Snapshot duplication

Each manual refresh currently creates a new snapshot even if the observed values are identical.

This preserves every observation but can create redundant history during frequent refreshes.

A later version may deduplicate snapshots or define a minimum observation interval.

### Amazon HTML dependency

The parser depends on Amazon's returned HTML structure.

External HTML is not an API contract, so selectors may require maintenance.

The application intentionally returns unknown values instead of guessing when data cannot be extracted reliably.

---

## Planned Multi-provider Architecture

The current service still contains Amazon-specific concepts.

A major V2 architectural goal is to introduce a provider boundary.

Conceptually:

```text
ProductProvider
 ├── AmazonProvider
 ├── AliExpressProvider
 ├── ShopeeProvider
 ├── MercadoLivreProvider
 └── TemuProvider
```

A provider should be responsible for marketplace-specific operations such as:

- recognizing supported URLs
- extracting external IDs
- fetching marketplace data
- parsing product state

The service should operate on a common provider result rather than directly depending on `AmazonFetcher` or `AmazonParser`.

A likely future flow is:

```text
URL
 ↓
Provider registry
 ↓
Matching ProductProvider
 ↓
Marketplace-specific fetch + parse
 ↓
Common Product / ProductSnapshot
 ↓
Repository
```

The first goal should be adding one second marketplace to validate the abstraction before adding several providers.
