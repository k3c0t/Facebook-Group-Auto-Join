import time, json, os
from selenium.webdriver.common.by import By

COOKIE_FILE = "cookies.json"

def load_cookies(driver):
    if not os.path.exists(COOKIE_FILE):
        print("❌ cookies.json tidak ditemukan")
        return False

    cookies = json.load(open(COOKIE_FILE, "r", encoding="utf-8"))
    for c in cookies:
        try:
            driver.add_cookie({
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ".facebook.com"),
                "path": c.get("path", "/")
            })
        except:
            pass
    return True


def auto_join_groups(driver, keyword, max_join, delay, status_callback=None):
    search_url = f"https://www.facebook.com/search/groups/?q={keyword}"
    driver.get(search_url)
    time.sleep(8)

    joined = 0
    scroll = 0

    while joined < max_join and scroll < 6:
        buttons = driver.find_elements(By.XPATH, "//div[@role='button']")

        for btn in buttons:
            if joined >= max_join:
                break

            try:
                text = btn.text.lower().strip()

                # 🧠 AUTO SKIP jika sudah joined
                if any(x in text for x in ["joined", "bergabung", "member", "anggota"]):
                    continue

                # ✅ tombol join valid
                if any(x in text for x in ["join", "gabung"]):
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", btn
                    )
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)

                    joined += 1

                    if status_callback:
                        status_callback(joined, max_join)

                    time.sleep(delay)

            except:
                pass

        driver.execute_script("window.scrollBy(0, 1200);")
        time.sleep(4)
        scroll += 1

    return joined

