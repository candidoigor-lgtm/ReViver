# ReViver — passo a passo da avaliação de backend

Este backend foi adaptado para a avaliação: a primeira entidade é `usuarios` (PK `id_usuario`) e a segunda é `conversas` (FK `id_usuario`). As rotas de análise dos CSVs também foram mantidas.

## 1. Abrir o projeto no Linux

Extraia o ZIP e abra a pasta `impacto-jovem-main` no VS Code. No terminal, entre na pasta backend:

```bash
cd caminho/para/impacto-jovem-main/backend
```

## 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se o terminal mostrar `(.venv)`, o ambiente está ativo.

## 3. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

## 4. Iniciar a API

Ainda dentro da pasta `backend`, execute:

```bash
python -m uvicorn api_analise:app --reload --host 127.0.0.1 --port 8001
```

Use o comando acima para manter compatibilidade com o comando antigo. A API completa estará em `http://127.0.0.1:8001` e a documentação em `http://127.0.0.1:8001/docs`. Mantenha esse terminal aberto.

Por padrão, o sistema usa SQLite e cria `backend/reviver.db` automaticamente. Não é necessário configurar PostgreSQL para realizar os testes locais. Para usar PostgreSQL, configure `DATABASE_URL` em um arquivo `backend/.env`; nunca envie `.env` ao GitHub.

## 5. Testar cadastro de usuário (POST)

Em `/docs`, abra `POST /usuarios`, clique em **Try it out** e envie:

```json
{
  "tipo_usuario": "familiar",
  "idade_faixa": "35-44",
  "objetivo_atendimento": "Buscar orientação para apoiar um familiar",
  "consentimento_dados": "sim"
}
```

Clique em **Execute**. A resposta deve ter status `201` e incluir `id_usuario`. Anote esse número para o próximo teste.

## 6. Testar consulta de usuário (GET)

Execute `GET /usuarios` para listar os cadastros ou `GET /usuarios/{id_usuario}` usando o identificador retornado no POST.

## 7. Testar conversa relacionada (POST)

Abra `POST /conversas`. Troque `id_usuario` pelo ID realmente retornado no passo 5:

```json
{
  "id_usuario": 1,
  "data_hora": "2026-10-19T10:30:00",
  "pergunta_usuario": "Como posso conversar com meu familiar de forma acolhedora?",
  "categoria_pergunta": "orientacao_familiar",
  "nivel_de_urgencia": "baixo",
  "necessita_profissional": "sim",
  "encaminhamento_realizado": "nao"
}
```

A resposta deve ter status `201` e incluir `usuario_tipo`, para mostrar de forma compreensível o tipo de usuário relacionado.

## 8. Testar consultas e chave estrangeira

- `GET /conversas`: lista conversas e inclui `usuario_tipo`.
- `GET /conversas?id_usuario=1`: filtra conversas de um usuário.
- `GET /conversas/{id_conversa}`: consulta uma conversa específica.
- Em `POST /conversas`, tente usar um `id_usuario` que não exista, como `999999`. A API deve responder `404` com uma mensagem dizendo que o usuário precisa existir.
- Em `GET /usuarios/999999`, a API deve responder `404`.

## 9. Testar análise dos CSVs

A documentação também deve listar as rotas antigas:

- `/analise/resumo`
- `/analise/qualidade`
- `/analise/usuarios`
- `/analise/clinicas`
- `/analise/conversas`
- `/analise/substancias`
- `/analise/indicadores`
- `/analise/dicionario`

Elas leem os CSVs do projeto; os cadastros feitos nas rotas POST ficam no banco SQLite e não são automaticamente inseridos nos CSVs.

## 10. Encerrar corretamente

No terminal do Uvicorn, pressione `Ctrl+C`. Depois execute:

```bash
deactivate
```

## 11. GitHub

Antes de enviar, confira se `.env`, `.venv/` e `backend/reviver.db` estão ignorados pelo `.gitignore`. Não faça commit de dados pessoais reais. Faça commit somente depois dos testes:

```bash
git status
git add backend docs/PASSO_A_PASSO_BACKEND_REVIVER.md .gitignore
git commit -m "Implementa backend ReViver com usuarios e conversas relacionadas"
git push
```

## Estrutura e relacionamento

- `database.py`: conexão SQLAlchemy e sessões.
- `models.py`: tabelas `usuarios` e `conversas`, com PK e FK.
- `schemas.py`: validação dos dados de entrada e saída.
- `main.py`: aplicação FastAPI e rotas.
- `api_analise.py`: mantém compatibilidade com `uvicorn api_analise:app`.
- `analise_csv.py`: análises já existentes dos arquivos CSV.

Os CSVs ampliados contêm dados sintéticos para testes. Não representam usuários, clínicas ou resultados reais e não devem ser usados como evidência clínica.


## 12. Executar os testes automatizados

Com o ambiente virtual ativado e dentro da pasta `backend/`, execute:

```bash
python -m pytest -q test_backend.py
```

O teste automatizado cria um usuário, cria uma conversa vinculada a ele, consulta a conversa e verifica os erros para identificadores inexistentes. O resultado esperado é `1 passed`. Para a evidência da avaliação, capture a tela do terminal com esse resultado e a tela do `/docs` mostrando as rotas.


## 13. Executar e validar os CSVs integrados

A partir da raiz do projeto, execute:

```bash
cd backend
python executar_csv.py
```

O programa lê os quatro CSVs operacionais, mostra estatísticas básicas e verifica os vínculos `conversas.id_usuario` → `usuarios.id_usuario`. Se a validação falhar, confira os IDs apontados no terminal. Os CSVs são dados sintéticos de demonstração.
