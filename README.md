# ReViver

O **ReViver** é um projeto educacional de apoio e informação para pessoas que enfrentam problemas relacionados ao uso de substâncias e para seus familiares. A plataforma oferece orientação geral, chatbot e listagem de serviços de apoio. Ela **não substitui** médicos, psicólogos, CAPS ou outros serviços de saúde.

## Tecnologias
- Frontend: HTML, CSS e JavaScript.
- Backend: Python com Flask.
- Banco de dados: PostgreSQL.
- Chatbot opcional: Ollama local.

## Executar no Linux
1. Instale Python 3.10+ e PostgreSQL. Para o chatbot, instale e inicie o Ollama separadamente.
2. Crie um banco chamado `reviver` e configure a variável `DATABASE_URL`, por exemplo: `postgresql://postgres:SUA_SENHA@localhost:5432/reviver`.
3. Execute o script `database/script_ddl.sql` no banco `reviver`. **Atenção:** esse script apaga e recria o schema `apoio`; faça backup antes de executá-lo em um banco com dados.
4. Instale as dependências: `python -m venv .venv`, `source .venv/bin/activate` e `pip install -r backend/requirements.txt`.
5. Inicie a API a partir da pasta do projeto: `python backend/app.py`. A API ficará em `http://127.0.0.1:5000`.
6. Abra `frontend/index.html` no navegador. Para uso real, sirva o frontend por um servidor HTTP e configure o endereço da API em `localStorage` com a chave `reviver-api`.

## Ollama (opcional)
Configure `OLLAMA_URL` e `OLLAMA_MODEL` conforme sua instalação. O modelo padrão é `llama3.2`. Sem Ollama disponível, o backend retorna uma resposta alternativa simples.

## Observações importantes
- GitHub Pages hospeda apenas arquivos estáticos; o backend Flask e o PostgreSQL precisam ficar hospedados em um servidor separado para que o site funcione publicamente.
- Antes de publicar, configure CORS para permitir somente o domínio do frontend e implemente autenticação real com sessão/token. O cabeçalho `X-Usuario-ID` usado neste protótipo não é um mecanismo de autenticação seguro.
- Não use dados reais sensíveis de saúde em demonstrações escolares.
