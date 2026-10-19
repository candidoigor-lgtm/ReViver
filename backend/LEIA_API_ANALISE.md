# API de análise dos CSVs do ReViver

Esta API FastAPI fica separada do `app.py` Flask, que mantém os chatbots. Os CSVs são lidos do diretório principal do projeto e de `backend/`.

## Instalação no Linux
Na pasta principal do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

## Executar

```bash
cd backend
python -m uvicorn api_analise:app --reload
```

Abra `http://127.0.0.1:8000/docs`.

## Rotas GET
- `/analise/resumo` — resumo de todas as fontes e qualidade básica
- `/analise/qualidade` — quantidade de linhas/colunas, valores ausentes e duplicações por fonte
- `/analise/usuarios` — distribuição por tipo, objetivo e consentimento
- `/analise/clinicas` — clínicas por cidade, serviço e status
- `/analise/conversas` — conversas por categoria, urgência e encaminhamento
- `/analise/substancias` — catálogo educativo
- `/analise/indicadores` — indicadores do CSV geral, com valores numéricos válidos separados dos ausentes
- `/analise/dicionario` — documentação de campos do CSV de especificação

A fonte de indicadores contém células vazias e deve ser interpretada com cuidado. Células vazias não são consideradas automaticamente zero. O arquivo de dicionário é documentação e não deve ser misturado com os indicadores operacionais.
