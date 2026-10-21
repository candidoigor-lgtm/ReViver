from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
ARQUIVOS = ["usuarios.csv", "conversas.csv", "clinicas.csv", "substancias.csv"]

def ler(nome):
    caminho = BASE / nome
    return pd.read_csv(caminho, encoding="utf-8-sig", dtype=str)

def main():
    print("=== ReViver — execução e validação dos CSVs ===")
    dados = {}
    for nome in ARQUIVOS:
        df = ler(nome)
        dados[nome] = df
        print(f"\n{nome}: {len(df)} registros | {len(df.columns)} colunas")
        print("Colunas:", ", ".join(df.columns))
        print("Linhas duplicadas:", int(df.duplicated().sum()))
        print("Valores vazios:", int(df.isna().sum().sum()))

    usuarios = dados["usuarios.csv"]
    conversas = dados["conversas.csv"]
    clinicas = dados["clinicas.csv"]
    substancias = dados["substancias.csv"]

    ids_usuarios = set(usuarios["id_usuario"].dropna().astype(str))
    ids_referenciados = set(conversas["id_usuario"].dropna().astype(str))
    sem_usuario = sorted(ids_referenciados - ids_usuarios)
    ids_clinicas = set(clinicas["id_clinica"].dropna().astype(str))
    duplicados_usuario = int(usuarios["id_usuario"].duplicated().sum())
    duplicados_conversa = int(conversas["id_conversa"].duplicated().sum())

    print("\n=== Validação de relacionamentos ===")
    print(f"IDs de usuários únicos: {len(ids_usuarios)}")
    print(f"Conversas sem usuário correspondente: {len(sem_usuario)}")
    print(f"IDs de usuário duplicados: {duplicados_usuario}")
    print(f"IDs de conversa duplicados: {duplicados_conversa}")
    print(f"Clínicas cadastradas (dados fictícios): {len(ids_clinicas)}")
    print(f"Substâncias no catálogo: {len(substancias)}")
    if sem_usuario:
        print("IDs sem correspondência:", ", ".join(sem_usuario[:20]))
        raise SystemExit("Falha na validação: há conversas sem usuário correspondente.")
    if duplicados_usuario or duplicados_conversa:
        raise SystemExit("Falha na validação: há identificadores duplicados.")
    print("\nValidação concluída com sucesso.")
    print("AVISO: os CSVs são dados sintéticos de demonstração; clínicas e contatos não são reais.")

if __name__ == "__main__":
    main()
