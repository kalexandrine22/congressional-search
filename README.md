# congressional-search

## Methodology

The congress.gov site is hosted by Cloudflare. This presents an issue when scraping the page via a simple HTTP request, as the request frequently triggers a CAPTCHA. Additionally, the content of the congress.gov/search URL is dynamically generated with JavaScript. This inhibits scraping the results as they do not exist when the webpage is first rendered. To account for these challenges, the Python script leverages a library called Playwright that initializes a headless browser. Using Playwright, the Python script emulates the actions of a user visiting the page by programmatically selecting page elements and waiting for the content to load.


