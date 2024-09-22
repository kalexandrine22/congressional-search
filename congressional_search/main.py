from asyncio import run
from time import sleep
from playwright.async_api import async_playwright


SEARCH_KEYWORD = "arctic"
CONGRESS_GOV_HOME_URL = "https://www.congress.gov"
CONGRESS_GOV_SEARCH_URL = f"{CONGRESS_GOV_HOME_URL}/search"
USER_AGENT = " ".join(
    [
        "Mozilla/5.0",
        "(Windows NT 10.0; Win64; x64)",
        "AppleWebKit/537.36",
        "(KHTML, like Gecko)",
        "Chrome/128.0.0.0",
        "Safari/537.36",
    ]
)

async def scrape() -> str:
    print("starting scrape...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(user_agent=USER_AGENT)

        page = await context.new_page()

        await page.goto(CONGRESS_GOV_SEARCH_URL)
        await page.locator("#search-format").select_option("all-congresses")

        await page.locator("#search").fill(SEARCH_KEYWORD)
        await page.locator("#search-submit").click()

        await page.locator("#pageSort").select_option("dateOfIntroduction:asc")

        await page.locator("#button_subject").click()
        await page.locator(
            "#facetItemsubjectArmed_Forces_and_National_Security"
        ).click()

        sleep(2)

        html = await page.content()

        await context.close()
        await browser.close()

    print("scrape complete!")
    return html


async def main():
    #results = parse(await scrape())
    html = await scrape()
    
    

    
    
if __name__ == "__main__":
    run(main())
