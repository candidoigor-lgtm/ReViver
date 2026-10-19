# Avaliação de Backend de Ciência de Dados — ReViver

## Objetivo
Ler os CSVs do projeto com Pandas, verificar a qualidade dos dados e disponibilizar indicadores por uma API FastAPI em JSON. O arquivo `app.py` continua responsável pelo backend Flask/chatbots; a API de análise usa `api_analise.py` separadamente para evitar criar uma segunda aplicação no mesmo arquivo.

## Fontes e significado
- `usuarios.csv`: cada linha representa um registro de usuário; `id_usuario` identifica o registro, `tipo_usuario` distingue o perfil, `idade_faixa` é uma faixa e não idade exata, `objetivo_atendimento` indica a finalidade informada e `consentimento_dados` registra a opção presente na fonte.
- `clinicas.csv`: cada linha representa uma clínica cadastrada; contém localização, serviços, profissionais, disponibilidade e datas de acompanhamento. Os registros atuais são exemplos e não devem ser tratados como contatos reais.
- `conversas.csv`: cada linha representa um registro de conversa, não necessariamente uma pessoa única. Inclui categoria, urgência e encaminhamento. Perguntas individuais não devem ser expostas em dashboards públicos.
- `substancias.csv`: cada linha representa um registro educativo sobre uma substância. O conteúdo atual é genérico e precisa de fontes confiáveis e revisão profissional antes de orientar usuários.
- `backend/impactojovem.csv - Página1.csv`: fonte legada de indicadores, com diversas células vazias. As células vazias permanecem ausentes; não são convertidas automaticamente em zero.
- `planilha_sem_titulo_pagina1.csv`: documento misto de especificação/dicionário de dados, não deve ser somado como se fosse uma tabela de atendimentos.

## Perguntas de negócio
1. Quantos registros existem por perfil de usuário? Usar `/analise/usuarios`; visual recomendado: cartão total e gráfico de barras por tipo.
2. Quais clínicas estão cadastradas por cidade, serviço e status? Usar `/analise/clinicas`; visual recomendado: tabela, lembrando que os dados de clínicas são exemplos.
3. Quais categorias e níveis de urgência aparecem nos registros de conversa e quantos encaminhamentos estão marcados? Usar `/analise/conversas`; visual recomendado: barras agregadas. Não mostrar perguntas individuais.
4. Quantos registros educativos de substâncias existem? Usar `/analise/substancias`; visual recomendado: catálogo/tabela educativa após revisão profissional.
5. Quais CSVs têm mais valores ausentes ou linhas duplicadas? Usar `/analise/qualidade`; visual recomendado: tabela de qualidade dos dados.

## Premissas e limitações
- Os CSVs contêm poucos registros demonstrativos; os resultados não representam prevalência, sucesso de tratamento ou resultados clínicos.
- IDs são identificadores e não devem ser somados.
- A contagem de conversas é de registros, não de pessoas únicas.
- A fonte legada possui campos vazios e sem dicionário operacional suficiente para interpretar todos os indicadores com segurança.
- A API não altera os CSVs nem remove duplicações automaticamente.
- Dados pessoais e perguntas potencialmente sensíveis devem ser anonimizados antes de publicar evidências no GitHub.

## Executar no Linux
Na pasta principal do projeto:

```bash
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cd backend
python -m uvicorn api_analise:app --reload --port 8001
```

Documentação interativa: `http://127.0.0.1:8001/docs`.

## Rotas GET
- `/` — status da API.
- `/analise/resumo` — resumo e qualidade básica das fontes.
- `/analise/qualidade` — ausências por coluna, duplicações e tipos detectados.
- `/analise/usuarios` — distribuição agregada de usuários.
- `/analise/clinicas` — distribuição agregada de clínicas.
- `/analise/conversas` — distribuição agregada de conversas.
- `/analise/substancias` — catálogo educativo.
- `/analise/indicadores` — leitura cautelosa da planilha legada.
- `/analise/dicionario` — documentação dos campos.

## Evidências
Os JSONs em `evidencias/backend/` são snapshots gerados localmente a partir dos CSVs incluídos. Ao alterar os CSVs, gere novamente as respostas. Para capturas de tela, abra `/docs`, execute cada rota e registre rota, status HTTP e resposta. Não publique dados pessoais reais.
