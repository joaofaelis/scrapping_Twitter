import os
import time
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do Chrome
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Remova para ver o navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializa o Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# Função para login automático
def login_twitter(email, senha):
    driver.get("https://twitter.com/login")
    time.sleep(5)

    email_input = driver.find_element(By.NAME, "text")
    email_input.send_keys(email)
    email_input.send_keys(Keys.ENTER)
    time.sleep(3)

    senha_input = driver.find_element(By.NAME, "password")
    senha_input.send_keys(senha)
    senha_input.send_keys(Keys.ENTER)
    time.sleep(5)


# Função para capturar tweets
def capturar_tweets(palavra_chave, quantidade=5):
    pasta = f"tweets_{palavra_chave.replace(' ', '_')}"
    os.makedirs(pasta, exist_ok=True)

    url = f"https://twitter.com/search?q={palavra_chave}&src=typed_query"
    driver.get(url)
    time.sleep(5)

    # Rolar a página para carregar mais tweets
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):  # Aumentei a rolagem
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(3)

    # Espera explícita aumentada para 20s
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))

    # Tenta encontrar tweets
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

    print(f"Encontrados {len(tweets)} tweets")

    for i, tweet in enumerate(tweets[:quantidade]):
        try:
            screenshot_path = f"{pasta}/tweet_{i + 1}.png"
            tweet.screenshot(screenshot_path)
            print(f"Print salvo: {screenshot_path}")

            # Extração de texto com OCR
            texto_extraido = pytesseract.image_to_string(Image.open(screenshot_path))
            with open(f"{pasta}/tweet_{i + 1}.txt", "w", encoding="utf-8") as f:
                f.write(texto_extraido)

            print(f"Texto extraído salvo: {pasta}/tweet_{i + 1}.txt")

        except Exception as e:
            print(f"Erro ao capturar tweet {i + 1}: {e}")

    print("Captura concluída!")


# **LOGIN AUTOMÁTICO NO TWITTER**
login_twitter("@oFaelis", "Jgames780@")

# **CAPTURA OS TWEETS**
capturar_tweets("Inteligência Artificial", quantidade=5)

# Fechar o navegador
driver.quit()
