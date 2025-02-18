import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# **Configuração do Chrome**
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")

# **Inicializa o Selenium**
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1280, 900)


# **Login automático no Twitter**
def login_twitter(usuario, senha):
    driver.get("https://twitter.com/login")
    time.sleep(5)

    user_input = driver.find_element(By.NAME, "text")
    user_input.send_keys(usuario)
    user_input.send_keys(Keys.ENTER)
    time.sleep(3)

    senha_input = driver.find_element(By.NAME, "password")
    senha_input.send_keys(senha)
    senha_input.send_keys(Keys.ENTER)
    time.sleep(5)


# **Ativar modo claro no Twitter**
def ativar_modo_claro():
    driver.get("https://twitter.com/i/display")
    time.sleep(3)

    try:
        light_mode_button = driver.find_element(By.XPATH, "//span[text()='Default']")
        light_mode_button.click()
        time.sleep(1)
        print("✅ Modo claro ativado no Twitter!")
    except:
        print("⚠️ O Twitter já está no modo claro ou o botão não foi encontrado.")


# **Captura tweets com extração via XPATH**
def capturar_tweets(palavras_chave, quantidade=100):
    for palavra_chave in palavras_chave:
        print(f"\n🔍 Buscando tweets para: {palavra_chave}")

        pasta = f"tweets_{palavra_chave.replace(' ', '_')}"
        os.makedirs(pasta, exist_ok=True)

        url = f"https://twitter.com/search?q={palavra_chave}&src=typed_query"
        driver.get(url)
        time.sleep(5)

        # **Criar DataFrame com a nova coluna "Link"**
        df_tweets = pd.DataFrame(columns=["ID", "Tweet", "Data", "Tema", "Link"])

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
        except:
            print(f"⚠️ Nenhum tweet encontrado para '{palavra_chave}'. Pulando para a próxima pesquisa.")
            continue  # Pular para o próximo termo

        body = driver.find_element(By.TAG_NAME, "body")
        tweets_capturados = set()
        tentativas_sem_novos_tweets = 0

        print(f"⏳ Carregando tweets para: {palavra_chave}")

        while len(tweets_capturados) < quantidade:
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            novos_tweets_encontrados = False

            for tweet in tweets:
                try:
                    WebDriverWait(driver, 5).until(EC.visibility_of(tweet))

                    # **Extrair o ID do tweet e gerar o link**
                    link_element = tweet.find_element(By.XPATH, ".//a[contains(@href, '/status/')]")
                    tweet_link = link_element.get_attribute("href")

                    tweet_id = tweet_link.split("/")[-1]  # Extrai o ID do link
                    if tweet_id not in tweets_capturados:
                        tweets_capturados.add(tweet_id)
                        novos_tweets_encontrados = True

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet)
                        time.sleep(1)

                        altura_tweet = tweet.size["height"]
                        altura_ajustada = max(900, altura_tweet + 150)
                        driver.set_window_size(1280, altura_ajustada)

                        screenshot_path = f"{pasta}/tweet_{len(tweets_capturados)}.png"
                        tweet.screenshot(screenshot_path)
                        print(f"📸 Print salvo: {screenshot_path}")

                        try:
                            # **Extraindo o texto do tweet via XPATH**
                            texto_extraido = tweet.find_element(By.XPATH,
                                                                ".//div[@data-testid='tweetText']").text.strip()
                        except Exception as e:
                            texto_extraido = "Erro ao extrair texto via XPATH"
                            print(f"⚠️ Erro ao extrair texto do tweet: {e}")

                        try:
                            data_element = tweet.find_element(By.XPATH, ".//time")
                            data_tweet = data_element.get_attribute("datetime").split("T")[0]
                        except:
                            data_tweet = "Desconhecida"

                        novo_tweet = pd.DataFrame({
                            "ID": [f"tweet_{len(tweets_capturados)}"],
                            "Tweet": [texto_extraido],
                            "Data": [data_tweet],
                            "Tema": [palavra_chave],
                            "Link": [tweet_link]  # **Adicionando o link do tweet**
                        })
                        df_tweets = pd.concat([df_tweets, novo_tweet], ignore_index=True)

                        print(f"📝 Tweet salvo - ID: {len(tweets_capturados)} - Link: {tweet_link}")

                        if len(tweets_capturados) >= quantidade:
                            print(f"✅ {quantidade} tweets coletados para '{palavra_chave}'!")
                            break
                except Exception as e:
                    print(f"⚠️ Erro ao capturar tweet: {e}")

            if not novos_tweets_encontrados:
                tentativas_sem_novos_tweets += 1
                if tentativas_sem_novos_tweets >= 5:
                    print(f"⚠️ Nenhum novo tweet encontrado para '{palavra_chave}', encerrando captura.")
                    break

            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(5)  # 🔄 Pausa maior para evitar bloqueios do Twitter

        # **Salvar os tweets em um arquivo Excel para este tema**
        nome_arquivo = f"tweets_{palavra_chave.replace(' ', '_')}.xlsx"
        df_tweets.to_excel(nome_arquivo, index=False)
        print(f"📂 Arquivo '{nome_arquivo}' criado com sucesso!")

        print(f"✅ Captura concluída para: {palavra_chave} - Total: {len(tweets_capturados)} tweets\n")
        time.sleep(10)  # Pausa maior entre buscas


# **Execução do Script**
try:
    login_twitter("@oFaelis", "Jgames780@")
    ativar_modo_claro()

    # **LISTA DE PALAVRAS PARA PESQUISAR**
    palavras = ["bieber"]

    # **CAPTURA OS TWEETS PARA TODAS AS PALAVRAS**
    capturar_tweets(palavras, quantidade=10)

except Exception as e:
    print(f"🚨 ERRO GERAL: {e}")

finally:
    driver.quit()  # Fechar navegador mesmo em caso de erro
    print("🛑 Navegador fechado.")

#Facebook

