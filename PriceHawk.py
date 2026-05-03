from ai import get_legit_items
import threading
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ping3 import ping
from PricePulse import visiting
import csv
import time
import asyncio
import schedule


class SEARCH:
    def __init__(self, keyword=None, csv_file_path=None, min_price=None, max_price=None, use_Ai=False):
        if keyword is not None:
            self.driver = uc.Chrome(version_main=147)
        self.stop_ping = False
        self.keyword = keyword
        self.csv_file_path = csv_file_path
        self.min_price = min_price
        self.max_price = max_price
        self.use_Ai = use_Ai
        self.saved_once = None
        self.absolute_file_path = "YOUR_ABSOLUTE_PATH/results.csv"

    def monitor_ping(self):
        self.stop_ping = False
        lowest_latency = None
        avg_latency = 0
        highest_latency = None
        time_ping = 0
        while not self.stop_ping:
            time.sleep(0.5)
            result = ping("amazon.com")
            time_ping += 1
            avg_latency += result
            if lowest_latency is None or result < lowest_latency:
                lowest_latency = result
            if highest_latency is None or result > highest_latency:
                highest_latency = result
            if result is False:
                print("Ping: Request timed out - No response from server")
            elif result * 1000 > 300:
                print(f"Ping: {result * 1000}ms - High latency detected")
        else:
            print("Ping monitoring stopped.")
            print(f"Lowest Latency:  {lowest_latency * 1000:.2f} ms")
            print(f"Average Latency: {(avg_latency/time_ping) * 1000:.2f} ms")
            print(f"Highest Latency: {highest_latency * 1000:.2f} ms")

    def main(self):
        if self.keyword is not None:
            t = threading.Thread(target=self.monitor_ping)
            try:
                t.start()
                self.driver.get("https://www.amazon.com/")
                self.driver.add_cookie({
                    "name": "i18n-prefs",
                    "value": "USD",
                    "domain": ".amazon.com"
                })
                wait = WebDriverWait(self.driver, 10)
                amazon_searchbox = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input#twotabsearchtextbox"))
                )
                amazon_searchbox.send_keys(self.keyword)
                amazon_searchbox.send_keys(Keys.ENTER)
                time.sleep(2)

                amazon_prices = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-component-type="s-search-result"] .a-price-whole'))
                )
                amazon_titles = [p.find_element(
                    By.XPATH, "./ancestor::div[@data-component-type='s-search-result']//a/h2") for p in amazon_prices]
                amazon_links = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-component-type="s-search-result"] #price-link + a'))
                )

                minimum_len = min(len(amazon_links), len(amazon_prices), len(amazon_titles))
                print(f"Number of products found: {minimum_len}")
                number_of_product = 0

                if self.use_Ai:
                    item_to_pop_by_ai = get_legit_items(
                        [amazon_titles[i].get_attribute('textContent') for i in range(minimum_len)],
                        self.keyword
                    )
                    print(f"AI flagged these indices: {item_to_pop_by_ai}")

                def printing(i):
                    print("*" * 20)
                    print(f"Title  n°{number_of_product}: {amazon_titles[i].get_attribute('textContent')}")
                    print(f"Link   n°{number_of_product}: {amazon_links[i].get_attribute('href')}")
                    print(f"Price  n°{number_of_product}: {amazon_prices[i].get_attribute('textContent')}")

                def pricechecker():
                    if self.min_price is None or not isinstance(self.min_price, int):
                        self.min_price = 0
                    if self.max_price is None or not isinstance(self.max_price, int):
                        self.max_price = 2000000000000000
                    if self.min_price > self.max_price:
                        self.min_price, self.max_price = self.max_price, self.min_price

                def savingascsv():
                    self.saved_once = True
                    with open(self.absolute_file_path, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Title', 'Link', 'Price'])
                        for i in range(minimum_len):
                            writer.writerow([
                                amazon_titles[i].get_attribute('textContent').replace(",", ""),
                                amazon_links[i].get_attribute('href'),
                                amazon_prices[i].get_attribute('textContent').replace(",", "").rstrip(".")
                            ])
                    print("Results saved to results.csv")

                pricechecker()

                if not self.use_Ai:
                    for i in range(minimum_len):
                        price = int(amazon_prices[i].get_attribute('textContent').replace(",", "").rstrip("."))
                        if self.min_price < price < self.max_price:
                            printing(i)
                        number_of_product += 1
                    savingascsv()

                elif self.use_Ai:
                    print("-" * 20, "Using AI Filter", "-" * 20)
                    for i in range(minimum_len):
                        price = int(amazon_prices[i].get_attribute('textContent').replace(",", "").rstrip("."))
                        if self.min_price < price < self.max_price and i not in item_to_pop_by_ai:
                            printing(i)
                        number_of_product += 1
                    savingascsv()
                    for i in item_to_pop_by_ai:
                        print(f"Flagged: {amazon_titles[i].get_attribute('textContent')}")

            except Exception as e:
                print(f"Error: {e}")
                if t.is_alive():
                    print("Stopping ping thread due to error.")
                self.stop_ping = True
            finally:
                self.stop_ping = True
                t.join()
                self.driver.quit()

        elif self.keyword is None and self.csv_file_path is not None:
            print("-" * 20, "Using CSV file", "-" * 20)
            if self.use_Ai:
                self.use_Ai = False
                print("-" * 20, "AI not available with local CSV", "-" * 20)

        time.sleep(2)

        def price_csv():
            if self.saved_once is None and self.csv_file_path is None:
                print("No results to process.")
                return
            elif self.saved_once is None:
                path = self.csv_file_path
            else:
                path = self.absolute_file_path
            run_job(path)

        def run_job(path):
            asyncio.run(visiting(path))

        schedule.every().day.at("09:00").do(price_csv)
        print("PriceHawk is watching 👁️")
        while True:
            schedule.run_pending()
            time.sleep(1)


