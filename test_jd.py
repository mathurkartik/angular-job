import asyncio
from scrapers.base_scraper import BaseScraper

async def main():
    s = BaseScraper()
    await s.init_browser()
    await s.page.goto('https://careers.bakerhughes.com/global/en/job/BAHUGLOBALR162709EXTERNALENGLOBAL/Digital-Technology-Specialist-Software-Engineering')
    await s.page.wait_for_timeout(5000)
    await s.page.screenshot(path='baker.png')
    text = await s.page.evaluate("document.body.innerText")
    print("Length of text:", len(text))
    await s.close_browser()

asyncio.run(main())
