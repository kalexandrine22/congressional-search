import os
import json
import io
import re
import sys
from asyncio import run
from time import sleep

import pypdf
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup, ResultSet, Tag
from playwright.async_api import async_playwright

load_dotenv()


OUTDIR = os.path.join(os.path.dirname(os.getcwd()), "analysis")
SEARCH_KEYWORD = "arctic"
CONGRESS_API_URL = "https://api.congress.gov/v3/bill"
CONGRESS_API_KEY = os.environ.get("CONGRESS_API_KEY", None)
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
BILLS_TO_IGNORE = {
    "H.R.324",
    "H.Con.Res.87",
    "H.Res.488",
    "S.152",
    "S.789",
    "S.1460",
    "S.Con.Res.46",
    "S.Res.327",
    "S.Res.397",
    "S.Res.459",
    "S.Res.577",
    "S.Res.585",
    "S.Res.618",
    "S.Res.745",
}

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
        await page.evaluate("window.scrollTo({top:0, behavior:'instant'})")
        await page.screenshot(path ='playwright_result.png')

        html = await page.content()

        await context.close()
        await browser.close()

    print("scrape complete!")
    return html
  
def parse(html: str):
    print("parsing html...")
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.select("ol.basic-search-results-lists li.expanded")
    return parse_search_results(search_results)
  
def parse_search_results(search_results: ResultSet[Tag]) -> list[dict]:
    parsed_results = []

    for item in search_results:
        result_heading = item.find(attrs={"class": "result-heading"})
        bill, _a, congress_with_suffix, _b, congress_year = result_heading.get_text().split(" ")
  
        if bill in BILLS_TO_IGNORE:
            continue

        legislation_type = item.find(attrs={"class": "visualIndicator"}).get_text()

        *body, bill_no = bill.split(".")
        bill_type = "".join(body).lower()
        bill_url = f"{CONGRESS_GOV_HOME_URL}{result_heading.find('a').get('href')}"
        bill_title = item.find(attrs={"class": "result-title"}).get_text()

        congress_no = remove_suffixes(congress_with_suffix)

        parsed_results.append(
            {
                "legislation_type": legislation_type,
                "bill": bill,
                "bill_title": bill_title,
                "bill_type": bill_type,
                "bill_no": bill_no,
                "bill_url": bill_url,
                "bill_text_api_url": get_bill_text_api_url(
                    congress_no, bill_type, bill_no
                ),
                "congress_no": congress_no,
                "congress_year": congress_year,
            }
        )

    print("parsing complete!")
    return parsed_results
  
def write_json(file, data):
    print(f"saving results to {os.path.join(OUTDIR, file)}")
    os.makedirs(OUTDIR, exist_ok=True)

    with open(os.path.join(OUTDIR, file), "w", encoding="utf8") as f:
        f.write(json.dumps(data, indent=2))
        
def remove_suffixes(s: str) -> str:
    return s.removesuffix("st").removesuffix("nd").removesuffix("rd").removesuffix("th")
  
def get_bill_text_api_url(congress: str, bill_type: str, bill_no: str) -> str:
    return f"{CONGRESS_API_URL}/{congress}/{bill_type}/{bill_no}/text"


def progress(i, total, length=40):
    percent = ("{0:.1f}").format(100 * (i / float(total)))
    filled_length = int(length * i // total)
    bar = "=" * filled_length + "-" * (length - filled_length)

    sys.stdout.write(f"\r[{bar}] {percent}% Complete")
    sys.stdout.flush()
    
def get_pdf(pdf_url: str) -> io.BytesIO:
    response = requests.get(pdf_url, timeout=20)
    return io.BytesIO(response.content)


def get_pdf_url(api_url: str):
    if not CONGRESS_API_KEY:
        raise Exception("congress API key not found")
    response = requests.get(api_url, params={"api_key": CONGRESS_API_KEY}, timeout=20)
    res_json = response.json()
    latest_version = res_json["textVersions"][-1]
    formats = latest_version["formats"]
    pdf_url = next((fmt["url"] for fmt in formats if fmt["type"] == "PDF"), None)
    return pdf_url


def count_keyword(keyword: str, pdf_bytes_stream: io.BytesIO) -> int:
    reader = pypdf.PdfReader(pdf_bytes_stream)
    keyword_count = 0

    for page in reader.pages:
        text = page.extract_text(0)
        matches = re.findall(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE)
        keyword_count += len(matches)

    return keyword_count
  
  
def keyword_search(keyword: str, data: list[dict]) -> list[dict]:
    results = []
    num_results = len(data)

    print("results found:", num_results)
    print(f"searching pdfs for keyword '{keyword}'")

    for index, item in enumerate(data):
        progress(index + 1, num_results)
        bill_text_api_url = item["bill_text_api_url"]
        congress = " ".join([item["congress_no"], item["congress_year"]])

        pdf_url = get_pdf_url(bill_text_api_url)
        pdf_bytes_stream = get_pdf(pdf_url)
        keyword_count = count_keyword(keyword, pdf_bytes_stream)

        results.append({"congress": congress, f"{keyword}_count": keyword_count})

    print("\nsearch complete!")
    return results
  
  
async def main():
    results = parse(await scrape())
    write_json("search_results.json", results)

    keyword_search_results = keyword_search(SEARCH_KEYWORD, results)
    write_json("keyword_search_results.json", keyword_search_results)
    

    
    
if __name__ == "__main__":
    run(main())
