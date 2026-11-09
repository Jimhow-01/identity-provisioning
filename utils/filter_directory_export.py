import json
import re
from pathlib import Path

json_file_path = Path.home() / 'data' / "users_info.json"
output_json_file = Path.home() / 'data' / "emails_filtrados.json"

#filtrar todos os emails da empresa
email_pattern = "@example\\.com$"

#filtar somente usuarios da empresa
#email_pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@example\.com$'

def filtrar_emails(json_file_path, output_json_file):
    with open(json_file_path, encoding='utf-8') as file:
        dados = json.load(file)
    
    usuarios = dados.get('users', [])
    
    emails_validos = []
    
    for usuario in usuarios:
        email = usuario.get('Email Address [Required]', '')
        if re.search(email_pattern, email):
            emails_validos.append(email)
    
    if emails_validos:
        print("E-mails válidos encontrados:")
        for email in emails_validos:
            print(email)
        
        with open(output_json_file, 'w', encoding='utf-8') as output_file:
            json.dump(emails_validos, output_file, ensure_ascii=False, indent=4)
        
        print(f"E-mails salvos em {output_json_file}")
    else:
        print("Nenhum e-mail válido encontrado.")

if __name__ == "__main__":
    filtrar_emails(json_file_path, output_json_file)
