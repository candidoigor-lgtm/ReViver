from fastapi import FastAPI, HTTPException
import pandas as pd
import analise_csv

app = FastAPI(
    title="API de Análise de Dados — ReViver",
    description="Rotas GET para análise dos CSVs do projeto ReViver. Dados de demonstração devem ser anonimizados.",
    version="1.0.0",
)


def executar(funcao):
    try:
        return funcao()
    except FileNotFoundError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except (ValueError, pd.errors.ParserError, UnicodeError) as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    except OSError as erro:
        raise HTTPException(status_code=503, detail="Não foi possível ler a fonte CSV.") from erro


@app.get("/")
def inicio():
    return {"projeto": "ReViver", "status": "online", "documentacao": "/docs"}


@app.get("/analise/resumo")
def consultar_resumo():
    return executar(analise_csv.resumo_geral)


@app.get("/analise/qualidade")
def consultar_qualidade():
    return executar(analise_csv.resumo_geral)


@app.get("/analise/usuarios")
def consultar_usuarios():
    return executar(analise_csv.analise_usuarios)


@app.get("/analise/clinicas")
def consultar_clinicas():
    return executar(analise_csv.analise_clinicas)


@app.get("/analise/conversas")
def consultar_conversas():
    return executar(analise_csv.analise_conversas)


@app.get("/analise/substancias")
def consultar_substancias():
    return executar(analise_csv.analise_substancias)


@app.get("/analise/indicadores")
def consultar_indicadores():
    return executar(analise_csv.analise_indicadores)


@app.get("/analise/dicionario")
def consultar_dicionario():
    return executar(analise_csv.dicionario_dados)
