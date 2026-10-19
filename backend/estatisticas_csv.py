from pathlib import Path
import pandas as pd

# Raiz do projeto: pasta acima de "backend"
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# CSVs encontrados no projeto ReViver
ARQUIVOS_CSV = [
    PASTA_PROJETO / "conversas.csv",
    PASTA_PROJETO / "planilha_sem_titulo_pagina1.csv",
    PASTA_PROJETO / "substancias.csv",
    PASTA_PROJETO / "usuarios.csv",
    PASTA_PROJETO / "clinicas.csv",
    PASTA_PROJETO / "backend" / "impactojovem.csv - Página1.csv",
]


def ler_csv(caminho):
    """Detecta o separador e tenta ler UTF-8 com BOM ou Latin-1."""
    try:
        return pd.read_csv(caminho, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(caminho, sep=None, engine="python", encoding="latin-1")


def analisar_csv(caminho):
    if not caminho.is_file():
        print(f"\n[AVISO] Arquivo não encontrado: {caminho}")
        return

    try:
        df = ler_csv(caminho)
    except Exception as erro:
        print(f"\n[ERRO] Não foi possível ler {caminho.name}: {erro}")
        return

    print("\n" + "=" * 55)
    print(f"ARQUIVO: {caminho.name}")
    print("=" * 55)
    print(f"Quantidade de registros: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")
    print("\nColunas:")
    print(df.columns.tolist())

    print("\nValores vazios por coluna:")
    print(df.isna().sum())

    vazias = df.columns[df.isna().all()].tolist()
    if vazias:
        print("\n[ATENÇÃO] Colunas totalmente vazias:")
        print(vazias)

    print(f"\nRegistros duplicados: {df.duplicated().sum()}")

    numericas = df.select_dtypes(include="number").dropna(axis=1, how="all")
    if not numericas.empty:
        print("\nEstatísticas numéricas:")
        print(numericas.describe().round(2))

    categoricas = df.select_dtypes(include=["object", "category"])
    for coluna in categoricas.columns:
        valores = df[coluna].dropna()
        if not valores.empty:
            print(f"\nValores mais frequentes em '{coluna}':")
            print(valores.astype(str).value_counts().head(10))


if __name__ == "__main__":
    encontrados = 0
    for arquivo in ARQUIVOS_CSV:
        if arquivo.is_file():
            encontrados += 1
        analisar_csv(arquivo)

    print("\n" + "=" * 55)
    print(f"Análise concluída. Arquivos encontrados: {encontrados}/{len(ARQUIVOS_CSV)}")
    print(f"Pasta principal do projeto: {PASTA_PROJETO}")
