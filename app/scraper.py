import asyncio
from playwright.async_api import async_playwright
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to fetch HTML content of the given URL
async def get_page_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Fetching page: {url}")
        try:
            await page.goto(url, timeout=60000)  # Timeout set to 60 seconds
            print("Page fetched successfully!")
            html_content = await page.content()
        except Exception as e:
            print(f"Error fetching page: {e}")
            html_content = None
        await browser.close()
        return html_content

# Function to fetch dynamic CSS selectors using OpenAI GPT
async def get_dynamic_selectors(html):
    print("Fetching dynamic CSS selectors using OpenAI GPT...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for extracting data from HTML."},
                {
                    "role": "user",
                    "content": (
                        f"Extract CSS selectors for reviews from this HTML. "
                        f"Selectors should include title, body, rating, and reviewer name: {html[:1000]}"  # Limit HTML size
                    ),
                },
            ],
        )
        result = response["choices"][0]["message"]["content"]
        print("Dynamic Selectors fetched successfully!")
        return result
    except Exception as e:
        print(f"Error fetching CSS selectors:\n{e}")
        return None

# Fallback function to manually provide CSS selectors
def fallback_selectors():
    print("Using fallback CSS selectors...")
    return {
        "title": ".jdgm-rev-widg-title",
        "body": ".jdgm-rev-widg-text",
        "rating": "[data-rating]",
        "reviewer": ".jdgm-rev-widg-user-name",
    }

# Function to scrape reviews from the product page
async def scrape_reviews(url):
    html_content = await get_page_html(url)

    if not html_content:
        print("Failed to fetch the page content. Exiting...")
        return None

    selectors = await get_dynamic_selectors(html_content)
    if not selectors:
        print("Dynamic selector fetch failed. Falling back to default selectors.")
        selectors = fallback_selectors()

    # Extract selectors
    try:
        if isinstance(selectors, str):  # If selectors were returned as a string
            selectors = eval(selectors)
        print("Parsed Selectors:", selectors)
        title_selector = selectors.get("title", "")
        body_selector = selectors.get("body", "")
        rating_selector = selectors.get("rating", "")
        reviewer_selector = selectors.get("reviewer", "")
    except Exception as e:
        print(f"Error parsing selectors: {e}")
        return None

    # Use the extracted selectors to scrape reviews
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            print("Scraping reviews...")

            # Extract reviews using the selectors
            reviews = []
            titles = await page.query_selector_all(title_selector)
            bodies = await page.query_selector_all(body_selector)
            ratings = await page.query_selector_all(rating_selector)
            reviewers = await page.query_selector_all(reviewer_selector)

            for i in range(len(titles)):
                review = {
                    "title": await titles[i].inner_text(),
                    "body": await bodies[i].inner_text() if i < len(bodies) else "",
                    "rating": await ratings[i].get_attribute("data-rating") if i < len(ratings) else "",
                    "reviewer": await reviewers[i].inner_text() if i < len(reviewers) else "",
                }
                reviews.append(review)

            await browser.close()
            print("Reviews scraped successfully!")
            return {"reviews_count": len(reviews), "reviews": reviews}
        except Exception as e:
            print(f"Error scraping reviews: {e}")
            await browser.close()
            return None

# Main function
async def main():
    url = "https://2717recovery.com/products/recovery-cream"  # Example URL
    reviews_data = await scrape_reviews(url)

    if reviews_data:
        print("Scraped Data:")
        print(reviews_data)
    else:
        print("Failed to scrape reviews.")

if __name__ == "__main__":
    asyncio.run(main())
