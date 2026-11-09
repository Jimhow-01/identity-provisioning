import os
import subprocess
import time
from pathlib import Path

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def verificar_chrome_aberto():
    for proc in psutil.process_iter():
        if 'chrome.exe' in proc.name():
            return True
    return False

def abrir_navegador():
    """Mata o Chrome em execucao e sobe o WebDriver headless.

    NOTE: era codigo de nivel de modulo; agora roda so na execucao direta.
    """
    if verificar_chrome_aberto():
        subprocess.run(["taskkill", "/f", "/im", "chrome.exe"])
        time.sleep(1)

    servico = Service(ChromeDriverManager().install())
    caminho_perfil = os.environ.get('CHROME_PROFILE_DIR', str(Path.home() / 'chrome-profile'))
    opcoes = Options()
    opcoes.add_argument('--user-data-dir=' + caminho_perfil)
    opcoes.add_argument("--headless=new")
    return webdriver.Chrome(service=servico, options=opcoes)


navegador = None
     
def criar_usuario():
    print("Criando usuário...")
    navegador.get("https://<workspace>.slack.com")
    time.sleep(3)
    navegador.find_element(By.CLASS_NAME, 'p-page_header__buttons').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '/html/body/div[12]/div/div/div[2]/div/div[1]/div/div/div/div/div[3]/div/div[1]/div[2]').send_keys("user@example.com")
    time.sleep(1)
    actions = ActionChains(navegador)
    actions.send_keys(Keys.SPACE)
    actions.perform()
    time.sleep(1)
    navegador.find_element(By.XPATH, '/html/body/div[11]/div/div/div[3]/div[2]/button').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '/html/body/div[12]/div/div/button').click()
    time.sleep(1)
    navegador.quit()
    
def remover_usuario():
    print("Removendo usuário...")
    navegador.get("https://<workspace>.slack.com")
    time.sleep(3)
    navegador.find_element(By.XPATH, '//*[@id="page_contents"]/div/div/div/div[2]/div[1]/div/div[2]/div/input').send_keys("user@example.com")
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="workspace_members_table__row_1__column_1"]/div/div/button').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="menu-2-6"]').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '/html/body/div[12]/div/div/div[3]/div/button[2]').click()
    time.sleep(1)
    navegador.quit()
    
if __name__ == "__main__":
    criar_usuario()
    #remover_usuario()