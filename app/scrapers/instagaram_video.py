# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time

# def collect_reels(profile_url, limit=20):
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless=new")   # 👈 no browser UI
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--window-size=1920,1080")

#     driver = webdriver.Chrome(options=options)
#     driver.get(profile_url)

#     time.sleep(5)

#     links = set()

#     for _ in range(5):
#         elements = driver.find_elements(By.TAG_NAME, "a")

#         for el in elements:
#             href = el.get_attribute("href")
#             if href and "/reel/" in href:
#                 links.add(href)

#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)

#         if len(links) >= limit:
#             break

#     driver.quit()
#     return list(links)


# if __name__ == "__main__":
#     reels = collect_reels("https://www.instagram.com/futoreels/")
#     print(reels)