# ShoppingListTracker

A desktop price-tracking application built with Python and PySide6.

ShoppingListTracker tracks Amazon Brazil products, stores historical observations in SQLite, and displays product details and price history in a desktop GUI.

![ShoppingListTracker screenshot](docs/screenshot.png)

## Features

- Track Amazon Brazil products from product URLs
- Extract ASIN from supported Amazon URL structures
- Parse product title, price, rating, and cover image
- Persist products and historical snapshots in SQLite
- Refresh tracked products and create new observations
- Visualize price history with Matplotlib
- Remove products and their stored history
- Preserve unknown values as `None` instead of guessing

Supported Amazon URL patterns currently include:

```text
/dp/{ASIN}
/gp/product/{ASIN}
```

## Tech Stack

- Python
- Requests
- BeautifulSoup
- SQLite
- PySide6
- Matplotlib
- Pytest
- `Decimal` for monetary values

## Architecture

The application is split into layers with distinct responsibilities:

```text
GUI
 ↓
Service
 ↓
Repository
 ↓
SQLite

Amazon URL
 ↓
AmazonFetcher
 ↓
AmazonParser
 ↓
Product + ProductSnapshot
```

Amazon-specific scraping is kept separate from persistence and presentation logic.

For a more detailed explanation of the design, data flow, domain models, and engineering decisions, see:

[Architecture](docs/ARCHITECTURE.md)

## Project Structure

```text
ShoppingListTracker/
├── data/
│   └── shopping_tracker.db
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── screenshot.png
├── src/
│   └── shopping_tracker/
│       ├── amazon.py
│       ├── database.py
│       ├── fetch_image.py
│       ├── models.py
│       ├── repository.py
│       ├── service.py
│       └── gui/
│           └── ui.py
├── tests/
│   └── test_amazon.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ShoppingListTracker
```

Create and activate a virtual environment on Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running

From the project root:

```bash
python main.py
```

## Usage

1. Paste an Amazon Brazil product URL.
2. Click **Add**.
3. Select the product from the tracked-products list.
4. View its current information and price history.
5. Click **Refresh** to fetch a new observation.
6. Click **Remove** to delete the product and its stored history.

## Tests

Run the test suite with:

```bash
pytest
```

The current tests include ASIN extraction for supported Amazon URL formats.

Future test coverage should include parser fixtures, repository operations, service behavior, and edge cases such as missing fields.

## Current Limitations

- Amazon Brazil is the only supported marketplace.
- Availability extraction is not yet reliable.
- Shipping-fee extraction is not yet implemented reliably.
- Network requests are synchronous and may temporarily block the GUI.
- The parser depends on Amazon HTML structure and may require maintenance when the site changes.
- Repeated refreshes can create identical snapshots.

## Roadmap

The next major version is planned around extensibility and active price monitoring:

- provider abstraction
- additional marketplaces
- target prices
- background refresh
- notifications
- improved availability and shipping extraction
- image caching
- snapshot deduplication
- stronger error handling, logging, and tests

See the detailed roadmap:

[Roadmap](docs/ROADMAP.md)

## Status

### V1

The current version includes:

- Amazon Brazil product tracking
- ASIN extraction
- product metadata extraction
- product images
- SQLite persistence
- historical snapshots
- price-history charts
- manual refresh
- product removal
- desktop GUI

The project is currently a functional local desktop price tracker and portfolio project.
