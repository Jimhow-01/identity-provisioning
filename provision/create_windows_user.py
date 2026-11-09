import ctypes
import os
import subprocess
import tkinter as tk

import win32con
import win32gui


def gerar_senha():
    import secrets
    return secrets.token_urlsafe(12)


def createWindowsUser(username):
    generated_password = gerar_senha()
    try:
        output = subprocess.check_output(f"net user {username} {generated_password} /add", shell=True, stderr=subprocess.STDOUT, text=True)
        if "Comando concluído com êxito." in output:
            print(f"Usuário '{username}' criado com sucesso!")
            os._exit(0)  # Fecha o programa
        else:
            print(f"Erro ao criar o usuário '{username}': {output}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o usuário '{username}': {e.output}")

def on_ok_click():
    email = entry.get().strip()
    if email.endswith("@example.com"):
        username = email.split('@')[0]
        createWindowsUser(username)
    else:
        print("Por favor, insira um email válido da empresa.")

def remove_window_buttons(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_SYSMENU
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

def block_close():
    pass  # Bloqueia o fechamento da janela

# Configurações da janela principal
root = tk.Tk()
root.title("Workstation Locked")
root.protocol("WM_DELETE_WINDOW", block_close)

# Configurações para fullscreen e sempre no topo
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)

root.update_idletasks()

# Remove botões de minimizar, maximizar e fechar
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
remove_window_buttons(hwnd)

# Mensagem de bloqueio
large_message = tk.Label(root, text="ATENÇÃO!\nEsta estação de trabalho foi bloqueada.\nEntre com seu email da empresa para desbloquear.", font=("Helvetica", 16))
large_message.pack(pady=20)

# Campo de entrada para o email
frame = tk.Frame(root, borderwidth=2, relief="solid")
frame.pack(padx=20, pady=20)
entry = tk.Entry(frame, width=40)
entry.pack(padx=20, pady=10)
entry.focus_set()

# Botão OK
button = tk.Button(frame, text="OK", command=on_ok_click)
button.pack(pady=10)

if __name__ == "__main__":
    # Execução da aplicação
    root.mainloop()
