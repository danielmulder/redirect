import random
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Proxy-lijst (VS)
proxies = [
    "http://23.95.255.103:6687",
    "http://31.58.10.48:6016",
    "http://31.58.10.190:6158",
    "http://45.38.70.131:7069",
    "http://104.168.8.85:5538",
    "http://104.238.36.234:6241",
    "http://104.238.37.130:6687",
    "http://104.239.124.237:6515",
    "http://104.252.20.250:6182",
    "http://104.252.41.80:7017",
]

def render_and_parse_page(url):
    try:
        proxy = random.choice(proxies)
        logger.info(f"🌐 Proxy: {proxy}")

        # ✅ Stealth-mode inschakelen
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--proxy-server={proxy}")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ✅ User-Agent instellen
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument(f'user-agent={user_agent}')
        logger.info(f"🦾 User-Agent: {user_agent}")

        # ✅ Stealth driver aanmaken
        driver = uc.Chrome(options=chrome_options)

        # ✅ Detecteerbare sporen verwijderen
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]})")
        driver.execute_script("Object.defineProperty(navigator, 'mimeTypes', {get: () => [1,2,3]})")

        # ✅ Blokkeer ongewenste bronnen (om fingerprinting te voorkomen)
        driver.execute_cdp_cmd(
            'Network.setBlockedURLs',
            {'urls': ['*.png', '*.jpg', '*.css', '*.gif', '*.svg']}
        )
        driver.execute_cdp_cmd('Network.enable', {})

        # ✅ Fetch pagina
        driver.get(url)

        # ✅ Wacht tot de body geladen is
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # ✅ Kort wachten om scripts te laten laden en daarna stoppen
        driver.execute_script("window.stop();")

        # ✅ HTML ophalen
        generated_html = driver.execute_script("return document.body.innerHTML;")

        # ✅ Dump naar bestand (optioneel)
        with open("dumped_html.html", "w", encoding="utf-8") as f:
            f.write(generated_html)

        logger.info("✅ HTML succesvol opgehaald en opgeslagen.")

        # ✅ Menselijk gedrag simuleren (muizenbewegingen en scrollen)
        actions = ActionChains(driver)
        actions.move_by_offset(100, 100).perform()
        driver.execute_script("window.scrollBy(0, 500);")

        return generated_html

    except Exception as e:
        logger.error(f"❌ Fout bij het renderen van {url}: {e}")
        return None

    finally:
        input("Druk op Enter om het venster te sluiten...")
        if driver:
            driver.quit()


# ✅ Voorbeeld gebruik
if __name__ == "__main__":
    test_url = "https://chatgpt.com/share/67445a0c-8aa4-8009-83ed-be116f826e5f"
    parsed_output = render_and_parse_page(test_url)

    if parsed_output:
        print("\n✅ Succesvolle parsing!")
    else:
        print("❌ Parsing mislukt.")
