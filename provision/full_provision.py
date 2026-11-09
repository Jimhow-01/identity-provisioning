import os
import random
import string
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

CLICKUP_TEAM_ID = os.environ.get("CLICKUP_TEAM_ID", "")

# Grupos de acesso do servidor de versionamento (ajuste ao seu ambiente)
GROUPS = [
    "core-team",
    "assets-alpha",
    "assets-beta",
    "beta-full",
    "local",
    "remote",
    "remote-with-permissions",
]

def verificar_chrome_aberto():
    for proc in psutil.process_iter():
        if 'chrome.exe' in proc.name():
            return True
    return False

def abrir_navegador():
    """Mata o Chrome em execucao e sobe o WebDriver headless.

    NOTE: isso era codigo de nivel de modulo - importar o arquivo ja mataba o
    navegador do usuario. Agora roda so na execucao direta.
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

#seção svn
def gerar_senha():
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(12))

def criar_usuario(email):
    username = email.split('@')[0]
    password = gerar_senha()
    command_create_user = f"New-SvnLocalUser -Name '{username}' -Password (ConvertTo-SecureString '{password}' -AsPlainText -Force)"
    subprocess.run(['powershell', '-Command', command_create_user], shell=True, check=True)
    return username, password

def add_user_group(username):
    group = input(f"Grupos disponiveis:\n{', '.join(GROUPS)}\nEscolha um grupo e digite para adicionar o usuario '{username}': ")
    command_group_user = f"Add-SvnLocalGroupMember '{group}' (Get-SvnLocalUser {username})"
    subprocess.run(['powershell', '-Command', command_group_user], shell=True, check=True)
    
def deletar_usuario(username):
    command_delete_user = f"Remove-SvnLocalUser -Name '{username}'"
    subprocess.run(['powershell', '-Command', command_delete_user], shell=True, check=True)



#seção slack
def criar_usuario_slack(email):
    print("Criando usuário no slack...")
    navegador.get("https://<workspace>.slack.com")
    time.sleep(3)
    navegador.find_element(By.CLASS_NAME, 'p-page_header__buttons').click()
    time.sleep(2)
    navegador.find_element(By.CLASS_NAME, 'c-multi_select_input__space').send_keys(email)
    time.sleep(1)
    actions = ActionChains(navegador)
    actions.send_keys(Keys.SPACE)
    actions.perform()
    time.sleep(1)
    navegador.find_element(By.CLASS_NAME, 'c-sk-modal_footer_actions').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '/html/body/div[12]/div/div/button').click()
    time.sleep(3)
    navegador.quit()

def remover_usuario_slack(email):
    print("Removendo usuário do slack...")
    navegador.get("https://<workspace>.slack.com")
    time.sleep(3)
    navegador.find_element(By.XPATH, '//*[@id="page_contents"]/div/div/div/div[2]/div[1]/div/div[2]/div/input').send_keys(email)
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="workspace_members_table__row_1__column_1"]/div/div/button').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="menu-2-6"]').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '/html/body/div[12]/div/div/div[3]/div/button[2]').click()
    time.sleep(3)
    navegador.quit()

#seção clickup
def convidando_usuario_clickup(email):
    print("Convidando usuário no clickup...")
    navegador.get(f"https://app.clickup.com/{CLICKUP_TEAM_ID}/settings/team/{CLICKUP_TEAM_ID}/users")
    time.sleep(5)
    navegador.find_element(By.XPATH, '//*[@id="settings-main"]/cu-team-settings/cu-team-users-settings/cu-team-users-settings-view/cu-team-settings/div/div[1]/div[2]/cu-invite-team-user/div/div[1]/input').send_keys(email)
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="settings-main"]/cu-team-settings/cu-team-users-settings/cu-team-users-settings-view/cu-team-settings/div/div[1]/div[2]/cu-invite-team-user/div/button').click()
    time.sleep(1)
    navegador.quit()

def remover_usuario_clickup(email):
    print("Removendo usuário do clickup...")
    navegador.get(f"https://app.clickup.com/{CLICKUP_TEAM_ID}/settings/team/{CLICKUP_TEAM_ID}/users")
    time.sleep(5)
    navegador.find_element(By.XPATH, '//*[@id="settings-main"]/cu-team-settings/cu-team-users-settings/cu-team-users-settings-view/cu-team-settings/div/div[1]/div[2]/div/div/div/input').send_keys(email)
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="settings-main"]/cu-team-settings/cu-team-users-settings/cu-team-users-settings-view/cu-team-settings/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div[1]/div/div[6]/div').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="cdk-overlay-0"]/div/div/a[4]/div[2]').click()
    time.sleep(1)
    navegador.find_element(By.XPATH, '//*[@id="app-root"]/cu-modal-keeper/cu-modal/div/div[2]/div[2]/div/cu-confirmation-modal/div[3]/button[2]').click()
    time.sleep(3)
    navegador.quit()

def main():
    global navegador
    navegador = abrir_navegador()

    print ('\n 1:Criar usuario svn\n 2:Criar usuario slack\n 3:Criar usuario clickup\n\n 4:Remover usuario svn\n 5:Remover usuario slack\n 6:Remover usuario clickup')
    numero = (input("\nColoque um numero: "))

    if numero == '1':
        emails = input("Digite o email do usuário: ")
        while emails:
            username, password = criar_usuario(emails)
            print(f"Usuário criado, Nome de usuário: {username} Senha: {password}")
            add_user_group(username)
            emails = input("Digite o email do próximo usuário (ou deixe em branco e de ENTER para parar): ")
    elif numero == '2':          
        email = input("Digite o email do usuário: ")
        criar_usuario_slack(email)
    elif numero == '3':
        email = input("Digite o email do usuário: ")
        convidando_usuario_clickup(email)
    elif numero == '4':
        nome_usuario_excluir = input("Digite o nome do usuário a ser excluído: ")
        deletar_usuario(nome_usuario_excluir)    
    elif numero == '5':
        email = input("Digite o email do usuário: ")
        remover_usuario_slack(email)
    elif numero == '6':
        email = input("Digite o email do usuário: ")
        remover_usuario_clickup(email)


if __name__ == "__main__":
    main()
