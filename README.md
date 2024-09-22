# congressional-search

This directory houses the Python scripts used to scrape the congress.gov/search url for legislation results when searching the keyword "arctic".

## Installation

Package dependencies are managed by Poetry. To install, navigate to the /scraper directory and run:

```sh
poetry install
```

Chromium must be installed in order to use Playwright:

```sh
poetry run playwright install chromium
```

## Usage

After installation, run the script with:

```sh
# linux
poetry run python congressional-searcher/main.py
```

```sh
# windows
poetry run py ./congressional-search/main.py
```
