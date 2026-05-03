# PriceHawk

PriceHawk is a smart tool for tracking Amazon prices. It searches for products, filters out the noise using AI, and emails you when prices drop.

---

## What PriceHawk Does

1. Searches Amazon for whatever keyword you enter
2. Filters out unrelated results with an LLM (Llama 3.3 through Groq)
3. Saves matches to a CSV file for you
4. Checks those prices every day with Playwright running asynchronously
5. Sends you an email alert if it finds a price drop

---

## Project Structure

| File             | What It Does                                             |
|------------------|---------------------------------------------------------|
| `PriceHawk.py`   | Handles Amazon searching, AI filtering, saves to CSV    |
| `PricePulse.py`  | Checks saved products daily to spot price drops         |
| `ai.py`          | Filters products using Groq’s LLM                       |
| `DROPALERT.py`   | Sends out price drop alerts using Gmail’s SMTP          |

---

## Tech Stack

- **Selenium** + **undetected-chromedriver** for scraping Amazon
- **Playwright** (async) for live, concurrent price checks
- **Groq API** (Llama 3.3 70b) for AI-powered filtering
- **asyncio** for running page checks together
- **schedule** for daily price monitoring
- **smtplib** to send alert emails

---

## How to Use PriceHawk

```python
# Search and filter with AI
p1 = SEARCH(keyword="sony wh-1000xm5", use_Ai=True)
p1.main()

# Search with a specific price range
p1 = SEARCH(keyword="logitech g305", min_price=50, max_price=200)
p1.main()

# Track prices for products already in a CSV file
p1 = SEARCH(csv_file_path="results.csv")
p1.main()
```

---

## Installation

```bash
pip install selenium undetected-chromedriver playwright groq ping3 schedule
playwright install chromium
```

---

## Notes

- Put your Groq API key in `ai.py`
- Set a Gmail App Password in `DROPALERT.py`
- PriceHawk was built and tested in May 2025. If Amazon updates their website or HTML structure, you might need to tweak things.
