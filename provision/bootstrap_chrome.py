import os
import subprocess
import time
import webbrowser
from pathlib import Path


def chrome_instalado():
    """Procura o Chrome nos caminhos padrao do Windows."""
    candidates = [
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    return next((c for c in candidates if c and c.exists()), None)


def instalar_chrome():
    # Instala o Google Chrome apenas se ele ainda nao estiver presente
    existente = chrome_instalado()
    if existente:
        print(f"Google Chrome ja instalado em {existente}.")
        return
    chrome_installer_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    installer_path = "chrome_installer.exe"
    
    try:
        # Baixar o instalador do Chrome
        subprocess.run(["powershell", "Invoke-WebRequest", "-Uri", chrome_installer_url, "-OutFile", installer_path], check=True)
        
        # Instalar o Chrome
        subprocess.run([installer_path], check=True)
        print("Google Chrome instalado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o Google Chrome: {e}")

def abrir_remote_desktop_setup():
    # Abrir o link do Google Chrome Remote Desktop para configuração manual
    url = 'https://remotedesktop.google.com/access'
    print("Abrindo o link para configurar o acesso remoto...")
    webbrowser.open(url)

if __name__ == "__main__":
    instalar_chrome()
    time.sleep(5)  # Pausa para garantir que o Chrome esteja instalado
    abrir_remote_desktop_setup()
    print("Siga as instruções no navegador para concluir a configuração do Chrome Remote Desktop.")
