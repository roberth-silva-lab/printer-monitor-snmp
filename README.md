# 🖨️ Automacao Impressora

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![SNMP](https://img.shields.io/badge/SNMP-Monitoramento-0A7E8C)
![Pandas](https://img.shields.io/badge/Pandas-Dados-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Graficos-3F4F75?logo=plotly&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?logo=telegram&logoColor=white)

Painel em Python para monitoramento de impressoras via SNMP com interface Streamlit, historico em CSV, relatorios (PDF/ZIP/Excel) e integracao com Telegram bot.

---

## 1. ✅ Funcionalidades

- Cadastro de impressoras (nome, IP, departamento)
- Coleta SNMP:
  - individual
  - em lote (todas cadastradas)
- Historico em CSV
- Dashboard com:
  - total de impressoras
  - total de departamentos
  - total de paginas
  - ultima coleta
  - filtros e graficos
- Status de conectividade:
  - `ONLINE` = ping + SNMP OK
  - `OFFLINE` = sem ping
  - `SNMP BLOQUEADO` = ping OK, sem SNMP
- Relatorios:
  - PDF por impressora
  - PDF por departamento
  - PDF consolidado
  - ZIP por impressora/departamento
  - Excel consolidado
- Telegram bot com comandos operacionais

---

## 2. 🧩 Tecnologias utilizadas

- Python
- Streamlit
- SNMP
- Pandas
- Plotly
- Telegram Bot API

---

## 3. 🗂️ Estrutura do projeto

```text
automacaoimpressora/
|-- main.py                  # Runner Streamlit
|-- telegram_main.py         # Runner Telegram
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- app/
    |-- main.py
    |-- config/
    |-- core/
    |-- data/                # Dados locais (nao versionados)
    |-- exports/             # Arquivos gerados (nao versionados)
    |-- models/
    |-- pdf/
    |-- repositories/
    |-- services/
    |-- telegram/
    `-- ui/
```

---

## 4. ⚙️ Instalacao (copy/paste)

Requisitos:

- Python 3.10+
- Windows (recomendado)
- Impressoras acessiveis em rede
- SNMP habilitado nas impressoras

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. 🔐 Configuracao do .env

1. Crie o arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

2. Edite `.env` com valores reais.

Exemplo ficticio:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEF_EXEMPLO_TOKEN_NAO_REAL
TELEGRAM_ADMIN_ID=111222333
TELEGRAM_ADMIN_IDS=111222333,444555666
```

Regras de autorizacao no Telegram:

- Se `TELEGRAM_ADMIN_ID` e `TELEGRAM_ADMIN_IDS` estiverem vazios: bot responde para todos.
- Se algum deles estiver preenchido: bot responde somente para os IDs autorizados.
- Use `/meuid` para descobrir seu `user_id`.

---

## 6. 🤖 Como criar um bot no Telegram (BotFather)

1. No Telegram, abra conversa com `@BotFather`.
2. Envie:
   - `/newbot`
3. Defina:
   - Nome do bot (ex.: `Monitor Impressoras`)
   - Username do bot (deve terminar com `bot`, ex.: `monitor_impressoras_bot`)
4. O BotFather vai retornar um token (formato `123456:ABC...`).
5. Cole esse token no `.env` em `TELEGRAM_BOT_TOKEN`.

Opcional, mas recomendado:

- Defina comandos visiveis no Telegram com `/setcommands` no BotFather.
- Sugestao de comandos:

```text
start - Iniciar atendimento
status - Ver resumo de status das impressoras
coletar - Iniciar coleta SNMP
relatorio - Gerar relatorios
impressoras - Listar impressoras cadastradas
ajuda - Exibir ajuda
meuid - Mostrar seu user_id
```

---

## 7. 🚀 Executar o Streamlit

```powershell
python -m streamlit run main.py --server.port 8510
```

Acesse:

- `http://localhost:8510`

---

## 8. 📲 Executar o bot Telegram

```powershell
python telegram_main.py
```

---

## 9. 📌 Comandos do bot (UX de uso)

### `/start`
Inicia conversa e mostra orientacao basica.

### `/ajuda`
Mostra a lista de comandos disponiveis.

### `/meuid`
Retorna seu `user_id` e `chat_id` atual.
Use este comando para configurar `TELEGRAM_ADMIN_ID`/`TELEGRAM_ADMIN_IDS`.

### `/impressoras`
Lista impressoras cadastradas no JSON.

### `/status`
Retorna resumo:

- total
- online
- offline
- snmp bloqueado

### `/coletar`
Abre menu com botoes:

- Coletar todas
- Coletar uma

### `/relatorio`
Abre menu com botoes:

- Uma impressora
- Um departamento
- Todas as impressoras

O bot gera e envia PDF no chat.

---

## 10. 🧪 Exemplo de uso

Exemplo de cadastro (ficticio):

| Nome         | IP          | Departamento |
|--------------|-------------|--------------|
| HP-CONTABIL  | 10.20.30.11 | Contabil     |
| HP-RH-01     | 10.20.30.21 | RH           |
| HP-FISCAL-02 | 10.20.30.31 | Fiscal       |

Exemplo de JSON (ficticio):

```json
[
  {
    "nome": "HP-CONTABIL",
    "ip": "10.20.30.11",
    "departamento": "Contabil"
  },
  {
    "nome": "HP-RH-01",
    "ip": "10.20.30.21",
    "departamento": "RH"
  }
]
```

Fluxo recomendado de operacao:

1. Cadastrar impressoras no Streamlit.
2. Executar coleta SNMP (lote ou individual).
3. Validar dados no dashboard.
4. Gerar relatorios para operacao.
5. Usar Telegram para consulta rapida e envio de relatorios.

---

## 11. 🔒 Seguranca

O projeto esta configurado para nao versionar residuos sensiveis/operacionais:

- `.env`
- `.venv`
- `app/data/*.csv`
- `app/data/*.json`
- `app/exports/`
- arquivos gerados (`.pdf`, `.zip`, `.xlsx`)

Somente arquivos de exemplo devem ir para o repositorio:

- `.env.example`
- exemplos deste README

---

## 12. 🛠️ Troubleshooting

### Bot nao responde

- Confirme que `python telegram_main.py` esta em execucao.
- Verifique `TELEGRAM_BOT_TOKEN` no `.env`.
- Rode `/meuid` e valide se seu ID esta autorizado.

### Erro de conflito do Telegram (`getUpdates`)

- Ja existe outra instancia do bot com o mesmo token.
- Feche a outra instancia e execute novamente.

### Sem dados de SNMP

- Verifique comunidade SNMP, ACL e firewall (UDP 161).
- Verifique conectividade IP/ping.

---

## 13. 📈 Melhorias futuras

- Agendamento automatico de coleta
- Alertas proativos no Telegram
- Dashboards temporais por periodo
- Camada de autenticacao no painel

---

## 14. 👤 Autor

Desenvolvido por **Roberth Silva**.

Este projeto foi criado com foco em automacao, monitoramento de rede e gestao de impressoras em ambientes corporativos, utilizando Python, Streamlit, SNMP e integracao com Telegram.

GitHub: `https://github.com/roberth-silva-lab`
