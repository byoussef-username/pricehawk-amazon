import asyncio
import csv
from playwright.async_api import async_playwright
from DROPALERT import send_notification

website_list = []

async def visitwebsite(context, website, old_price, sem):
    page = None
    try:
        async with sem:
            page = await context.new_page()
            await page.goto(website)
            element = await page.query_selector('.a-price-whole')
            if element:
                new_price = await element.inner_text()
                new_price = new_price.replace(",", "").rstrip(".")
                print(f"Old price: {old_price} | New price: {new_price}")
                if int(new_price) < int(old_price):
                    await send_notification(
                        "your_Email@gmail.com",
                        f"Price drop!\nOld: {old_price}\nNew: {new_price}\nLink: {website}"
                    )
                    print(f" PRICE DROP! {old_price} → {new_price}")
                else:
                    print("No drop")
            else:
                print(f"⚠️ Price not found: {website[:50]}")
    except Exception as e:
        print(f"Error: {website[:50]}: {e}")
    finally:
        if page:
            await page.close()


async def visiting(path):
    website_list.clear()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale='en-US',
            timezone_id='America/New_York',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        rows = list(csv.DictReader(open(path, encoding='utf-8')))
        website_links = [row['Link'] for row in rows]
        website_prices = [row['Price'] for row in rows]

        # set USD cookie
        page = await context.new_page()
        await page.goto('https://www.amazon.com')
        await page.evaluate("document.cookie = 'i18n-prefs=USD; domain=.amazon.com'")
        await page.close()

        sem = asyncio.Semaphore(5)
        minimum = min(len(website_links), len(website_prices))

        for i in range(minimum):
            website_list.append(visitwebsite(context, website_links[i], website_prices[i], sem))

        print("Processing...")
        await asyncio.gather(*website_list)
        await browser.close()