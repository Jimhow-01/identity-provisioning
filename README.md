# identity-provisioning

> Onboarding e offboarding automatizados de identidade: contas e grupos de servidor SVN, Slack e ClickUp a partir de um único menu — mais um script separado para criar o usuário local Windows.

![CI](https://img.shields.io/github/actions/workflow/status/Jimhow-01/identity-provisioning/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white) ![Tests](https://img.shields.io/badge/tests-4%20passing-brightgreen?logo=pytest&logoColor=white) ![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json) ![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white) ![Platform](https://img.shields.io/badge/platform-Windows-lightgrey) ![Status](https://img.shields.io/badge/status-portfolio%20showcase-lightgrey)

![Python](https://img.shields.io/badge/Python-377641?logo=python&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B08A?logo=selenium&logoColor=white) ![PowerShell](https://img.shields.io/badge/PowerShell-559657?logo=powershell&logoColor=white) ![SVN](https://img.shields.io/badge/SVN-FF7F50) ![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=white) ![ClickUp](https://img.shields.io/badge/ClickUp-7B68EE)

## O problema

Entrar num estúdio significa ganhar acesso a quatro sistemas ao mesmo tempo. Sair significa perder os quatro. Feito à mão, isso gera erro, acesso esquecido e ticket perdido.

Estes scripts cobrem o ciclo de acesso a três sistemas a partir do e-mail do funcionário — conta no servidor de versionamento, convite no Slack e vaga no ClickUp — e o caminho inverso na saída. O usuário local Windows é um script **separado** (`create_windows_user.py`), com GUI própria; `full_provision.py` não o chama. Deixar isso explícito porque a integração entre os dois era manual na época.

## Arquitetura

```
identity-provisioning/
├── provision/
│   ├── full_provision.py        menu unificado (SVN + Slack + ClickUp)
│   ├── create_windows_user.py   cria usuário local via `net user`
│   ├── slack_admin_ui.py        convites e remoções no painel do Slack
│   └── bootstrap_chrome.py      baixa e roda o instalador do Chrome (detecta se ja existe)
└── utils/
    └── filter_directory_export.py   extrai e-mails válidos de um export do diretório
```

## Destaques técnicos

### 🔌 SVN local via cmdlets PowerShell

O servidor de versionamento tem usuários e grupos próprios (`New-SvnLocalUser`, `Add-SvnLocalGroupMember`, `Remove-SvnLocalUser`). O script administra os dois por PowerShell, com senha gerada aleatoriamente e grupos nomeados por projeto/acesso.

### 🌐 Painel dirigido por Selenium

Slack (painel de admin do workspace) e ClickUp (team users) foram dirigidos com `selenium` + `webdriver-manager` em `--headless=new`, reaproveitando um perfil Chrome dedicado (`CHROME_PROFILE_DIR`) que já tem a sessão autenticada. Motivo declarado na época: parte das operações de administração não tinha endpoint simples de usar. Hoje eu faria API primeiro e Selenium só onde não há endpoint — e é importante dizer que **nenhum destes scripts chama API alguma**, então a justificativa não é demonstrável a partir do código publicado.

### 🪟 Controle de janela Win32

`create_windows_user.py` abre uma tela Tkinter fullscreen **sem botão de fechar**: remove `WS_SYSMENU` com `win32gui.GetWindowLong`/`SetWindowLong` e intercepta `WM_DELETE_WINDOW`. A tela exige digitar o e-mail corporativo para criar o usuário local. Uma ressalva honesta: a validação é um `endswith` do domínio e o sucesso chama `os._exit(0)` — **não há verificação HMAC nem integração com o lock** da `workstation-security-suite`. As duas peças existiam no mesmo ambiente mas não estavam conectadas por código.

### 🧹 Offboarding em lote

`filter_directory_export.py` lê o export JSON do diretório de usuários e filtra os e-mails pelo padrão do domínio, alimentando a remoção em massa.

## ⚠️ Fragilidades conhecidas (declaradas, não escondidas)

1. **Seletores XPath de painéis de terceiros.** Slack e ClickUp mudam layout com frequência e esses scripts quebram na primeira mudança. Eles usam `time.sleep` fixo em vez de `WebDriverWait` — é o primeiro ponto que eu reescreveria hoje.
2. **Senha na linha de comando.** `New-SvnLocalUser -Password (ConvertTo-SecureString '<senha>' -AsPlainText -Force)` expõe a senha no histórico do PowerShell e na lista de processos, e o script imprime a senha em texto claro no terminal. O correto é passar por stdin ou variável de ambiente e nunca imprimir.
3. **Efeito colateral em import (corrigido aqui).** `full_provision.py` e `slack_admin_ui.py` matavam o Chrome do usuário e subiam um WebDriver no **escopo do módulo** — importar o arquivo já causava isso. Movi para `abrir_navegador()` chamada só sob `if __name__ == "__main__"`. `create_windows_user.py` tinha `root.mainloop()` em nível de módulo pelo mesmo motivo, também corrigido.
4. **Selenium em vez de API.** Parte do que estes scripts fazem por UI tem API oficial (Slack admin, ClickUp API). Foi a solução disponível na época; a versão correta seria API primeiro, Selenium só onde não há endpoint.
5. **URL do ClickUp com ID duplicado.** `full_provision.py` monta `/settings/team/{CLICKUP_TEAM_ID}/users` com a variável repetida no caminho — resquício de sanitização (dois IDs diferentes foram substituídos pela mesma variável). Precisa ser conferido antes de usar.

## Testes e lint

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check .          # lint
pytest                # 4 testes
```

O CI roda lint, `compileall` e pytest em `windows-latest` (Python 3.11 e 3.12) a cada
push — Windows porque este código usa `pywin32`, `wmi` e `winreg`, que não existem em Linux.

A configuração do ruff está em `pyproject.toml` e declara, com o motivo de cada uma, as
regras que **não** estou corrigindo agora. Prefiro isso a escolher um subconjunto de regras
que passa por acaso.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # Windows (cp .env.example .env em Linux/macOS)
```

### Como rodar

```bash
# menu unificado: criar/remover usuario em SVN, Slack e ClickUp
python provision/full_provision.py

# criar usuario local Windows (GUI fullscreen sem botao de fechar)
python provision/create_windows_user.py

# painel de administracao do Slack
python provision/slack_admin_ui.py

# baixa e roda o instalador do Chrome (detecta se ja existe)
python provision/bootstrap_chrome.py

# offboarding em lote: extrai e-mails validos de um export do diretório
python utils/filter_directory_export.py
```

Os scripts de painel exigem um perfil Chrome já autenticado (`CHROME_PROFILE_DIR`)
porque dirigem a interface web por Selenium.

### Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `CHROME_PROFILE_DIR` | perfil Chrome reaproveitado pelo WebDriver (usado em `full_provision.py` e `slack_admin_ui.py`) |
| `CLICKUP_TEAM_ID` | ID da equipe, aparece na URL do painel de usuários |

Não há token de Slack nem token de API do ClickUp neste repositório: os dois painéis são dirigidos por Selenium sobre um perfil já autenticado. Se você trocar para API, aí sim entram `SLACK_BOT_TOKEN` e `CLICKUP_API_TOKEN`.

---

## ⚠️ Sobre o que isto é — e sobre titularidade

São **scripts internos de TI** escritos durante meu trabalho em um estúdio de jogos, **sanitizados** para publicação: tokens, senhas, hosts internos, IPs, nomes de projeto e dados de terceiros foram substituídos por variáveis de ambiente ou placeholders. O estúdio não é nomeado aqui de propósito.

Duas coisas que quero deixar claras em vez de deixar você descobrir:

- **Não estou reivindicando direitos sobre este código.** Parte dele foi produzida como funcionário, e direitos sobre trabalho de empregador pertencem ao empregador. Publico como demonstração de como eu resolvi os problemas — para leitura e estudo, não como software livre. Não há licença concedida (ver `LICENSE`).
- **Não são produtos prontos para produção.** São demonstrações de abordagem técnica, com limitações declaradas nas seções acima. Copie `.env.example` para `.env` e preencha antes de rodar qualquer coisa — e rode só contra infraestrutura sua.
