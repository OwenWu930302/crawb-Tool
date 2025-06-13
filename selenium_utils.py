from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    # 加入容錯提示
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        raise RuntimeError(f"無法啟動瀏覽器，請確認已安裝 Chrome 及 chromedriver，錯誤訊息：{e}")

def find_by_keyword(url, keyword, headless=True):
    driver = None
    try:
        driver = create_driver(headless)
        driver.get(url)
        if not keyword:
            return "請輸入搜尋文字"
        xpath = f"//*[contains(text(), '{keyword}')]"
        elements = driver.find_elements(By.XPATH, xpath)
        texts = [el.text for el in elements if el.text.strip()]
        return '\n'.join(texts) if texts else f"未找到：{keyword}"
    except Exception as e:
        return f"錯誤：{e}\n請確認網址正確、網頁可正常開啟，或關鍵字是否合理。"
    finally:
        if driver:
            driver.quit()

def parse_input(input_str):
    input_str = input_str.strip().lower()
    # 處理 <nobr>、<nobr></nobr>、nobr
    if input_str.startswith('<') and input_str.endswith('>'):
        try:
            soup = BeautifulSoup(input_str, 'html.parser')
            tag = soup.find()
            if tag:
                return 'css', tag.name
            else:
                return 'css', '*'
        except Exception:
            return 'css', '*'
    # 純 tag name
    if input_str.isalpha():
        return 'css', input_str
    # XPath
    if input_str.startswith('/') or input_str.startswith('(') or input_str.lower().startswith('xpath:'):
        return 'xpath', input_str.replace('xpath:', '').strip()
    # CSS selector
    return 'css', input_str


def advanced_search(url, input_str, headless=True):
    driver = None
    try:
        driver = create_driver(headless)
        driver.get(url)
        if not input_str:
            return ["請輸入搜尋條件（標籤、class、id、CSS或XPath）"]
        mode, selector = parse_input(input_str)
        # 容錯：自動修正 selector
        try:
            if mode == 'css':
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                elements = driver.find_elements(By.XPATH, selector)
        except Exception as e:
            # 嘗試自動修正：若 CSS 失敗且疑似 XPath，則自動用 XPath 再試
            if mode == 'css' and (selector.startswith('/') or selector.startswith('(')):
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                except Exception:
                    return [f"選擇器語法錯誤，請檢查輸入內容。詳細：{e}"]
            else:
                return [f"選擇器語法錯誤，請檢查輸入內容。詳細：{e}"]
        results = [el.text for el in elements if el.text.strip()]
        return results if results else [f"未找到符合元素：{input_str}"]
    except Exception as e:
        return [f"錯誤：{e}\n請確認網址正確、網頁可正常開啟，或選擇器是否合理。"]
    finally:
        if driver:
            driver.quit()
