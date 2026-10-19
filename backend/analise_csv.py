from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
BACKEND = Path(__file__).resolve().parent

ARQUIVOS = {
    "usuarios": BASE / "usuarios.csv",
    "clinicas": BASE / "clinicas.csv",
    "conversas": BASE / "conversas.csv",
    "substancias": BASE / "substancias.csv",
    "indicadores": next(iter(BACKEND.glob("impactojovem.csv*")), BACKEND / "impactojovem.csv"),
    "dicionario": BASE / "planilha_sem_titulo_pagina1.csv",
}


def ler_csv(nome):
    """Lê um CSV do projeto e retorna um DataFrame com valores ausentes padronizados."""
    if nome not in ARQUIVOS:
        raise ValueError(f"Fonte desconhecida: {nome}")
    caminho = ARQUIVOS[nome]
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho.name}")
    df = pd.read_csv(caminho, encoding="utf-8-sig", dtype=str, keep_default_na=True)
    df.columns = [str(c).strip() for c in df.columns]
    # Espaços vazios passam a ser valores ausentes para a análise de qualidade.
    for coluna in df.columns:
        if df[coluna].dtype == "object":
            df[coluna] = df[coluna].map(lambda x: x.strip() if isinstance(x, str) else x)
            df[coluna] = df[coluna].replace("", pd.NA)
    return df


def resumo_fonte(nome):
    df = ler_csv(nome)
    return {
        "fonte": nome,
        "arquivo": ARQUIVOS[nome].name,
        "total_registros": int(len(df)),
        "total_colunas": int(len(df.columns)),
        "colunas": list(df.columns),
        "valores_ausentes_por_coluna": {str(k): int(v) for k, v in df.isna().sum().items()},
        "linhas_duplicadas": int(df.duplicated().sum()),
    }


def resumo_geral():
    fontes = {}
    for nome in ARQUIVOS:
        try:
            fontes[nome] = resumo_fonte(nome)
        except (OSError, ValueError, pd.errors.ParserError) as erro:
            fontes[nome] = {"fonte": nome, "erro": str(erro)}
    return {
        "projeto": "ReViver",
        "observacao": "Contagens descrevem os CSVs disponíveis; não representam necessariamente pessoas únicas nem resultados clínicos.",
        "fontes": fontes,
    }


def por_coluna(nome, coluna):
    df = ler_csv(nome)
    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe na fonte '{nome}'.")
    contagem = df[coluna].fillna("Não informado").value_counts(dropna=False)
    return [{"categoria": str(k), "quantidade": int(v)} for k, v in contagem.items()]


def analise_usuarios():
    df = ler_csv("usuarios")
    return {
        "total_registros": int(len(df)),
        "por_tipo_usuario": por_coluna("usuarios", "tipo_usuario") if "tipo_usuario" in df else [],
        "por_objetivo_atendimento": por_coluna("usuarios", "objetivo_atendimento") if "objetivo_atendimento" in df else [],
        "por_consentimento": por_coluna("usuarios", "consentimento_dados") if "consentimento_dados" in df else [],
        "nota": "A idade está em faixas; não deve ser interpretada como idade exata. IDs são identificadores, não medidas para somar.",
    }


def analise_clinicas():
    df = ler_csv("clinicas")
    resultado = {
        "total_registros_clinica": int(len(df)),
        "por_cidade": por_coluna("clinicas", "cidade") if "cidade" in df else [],
        "por_status_atendimento": por_coluna("clinicas", "status_atendimento") if "status_atendimento" in df else [],
        "por_servico": por_coluna("clinicas", "servicos") if "servicos" in df else [],
        "nota": "Vagas disponíveis não são somadas porque a fonte pode conter textos como 'Consultar disponibilidade'. Verifique antes de tratar como número.",
    }
    return resultado


def analise_conversas():
    df = ler_csv("conversas")
    return {
        "total_registros_conversa": int(len(df)),
        "por_categoria": por_coluna("conversas", "categoria_pergunta") if "categoria_pergunta" in df else [],
        "por_urgencia": por_coluna("conversas", "nivel_de_urgencia") if "nivel_de_urgencia" in df else [],
        "necessita_profissional": por_coluna("conversas", "necessita_profissional") if "necessita_profissional" in df else [],
        "encaminhamento_realizado": por_coluna("conversas", "encaminhamento_realizado") if "encaminhamento_realizado" in df else [],
        "nota": "A contagem é de registros de conversa, não necessariamente de pessoas distintas. Evite expor perguntas individuais em dashboards públicos.",
    }


def analise_substancias():
    df = ler_csv("substancias")
    return {
        "total_registros_substancia": int(len(df)),
        "substancias": df.fillna("").to_dict(orient="records"),
        "nota": "O CSV contém material educativo. Confira fontes e revisão profissional antes de usar o conteúdo como orientação de saúde.",
    }


def analise_indicadores():
    df = ler_csv("indicadores")
    # A fonte contém indicadores em colunas e várias células vazias; não inventamos valores ausentes.
    numericas = ["acolhimento", "total de buscas", "desistencias", "usuarios", "avanço", "entrada", "saida", "SUCESSO", "empenho"]
    colunas_presentes = [c for c in numericas if c in df.columns]
    totais = {}
    for coluna in colunas_presentes:
        valores = pd.to_numeric(df[coluna], errors="coerce")
        totais[coluna] = {
            "soma_dos_valores_numericos_validos": float(valores.sum()) if valores.notna().any() else None,
            "valores_numericos_validos": int(valores.notna().sum()),
            "valores_nao_numericos_ou_ausentes": int(valores.isna().sum()),
        }
    return {
        "total_registros": int(len(df)),
        "colunas": list(df.columns),
        "indicadores_numericos": totais,
        "por_clinica": por_coluna("indicadores", "clinicas") if "clinicas" in df.columns else [],
        "nota": "As somas consideram apenas valores numéricos válidos. Células vazias não foram convertidas em zero; confirme o significado de cada indicador antes de comparar ou somar.",
    }


def dicionario_dados():
    df = ler_csv("dicionario")
    # Este CSV documenta campos/regras e tem formato misto; retornamos as linhas como documentação, sem usá-las em indicadores.
    return {
        "total_registros": int(len(df)),
        "colunas": list(df.columns),
        "registros": df.fillna("").to_dict(orient="records"),
        "nota": "Arquivo de documentação/especificação, não uma fonte de indicadores de atendimento.",
    }
