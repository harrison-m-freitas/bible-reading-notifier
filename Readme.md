# Documentação do Projeto

## Estrutura de Pastas

```text
bible-reading-notifier/
├── bible/
│   ├── Antigo Testamento/
│   └── Novo Testamento
├── config/
│   ├── contact.json
│   └── last_sent_date.json
├── debug/
├── bible_manager.py
├── controler.py
└── whatsapp_manager.py
```

## Arquivos do Projeto

### `controler.py`

Este arquivo contém a classe `Controller` que gerencia o envio de mensagens diárias via WhatsApp utilizando `WhatsAppManager` e `BibleManager`.

### `whatsapp_manager.py`

Este arquivo contém a classe `WhatsAppManager` que gerencia a interação com o WhatsApp Web via Selenium.

### `bible_manager.py`

Este arquivo contém a classe `BibleManager` que gerencia a leitura diária da Bíblia.

## Dependências

- Python 3.x
- Selenium
- pyperclip

## Instalação

1. Clone o repositório:

    ```sh
    git clone https://github.com/seu-usuario/bible-reading-notifier.git
    cd bible-reading-notifier
    ```

2. Crie um ambiente virtual e ative-o:

    ```sh
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    .\venv\Scripts\activate  # Windows
    ```

3. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

4. Configure os arquivos `contact.json` e `last_sent_date.json` no diretório `config/`.

5. Execute o script:

    ```sh
    python controler.py
    ```
