"""
ETL – Knowledge Engine
Dataset : TMDB 5000 Movies (Kaggle)
"""
import json
import os
import re
import unicodedata
import pandas as pd


COLUNAS = [
    "id",
    "title",
    "genres",
    "original_language",
    "release_date",
    "runtime",
    "vote_average",
    "vote_count",
    "budget",
    "revenue",
]

MAPEAMENTO_COLUNAS = {
    "id": "id",
    "title": "titulo",
    "genres": "generos",
    "original_language": "idioma_original",
    "release_date": "data_lancamento",
    "runtime": "duracao",
    "vote_average": "media_votos",
    "vote_count": "contagem_votos",
    "budget": "orcamento",
    "revenue": "receita",
}



def remover_acentos(texto: str) -> str:
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def normalizar_atomo(texto: str) -> str:
    if not isinstance(texto, str):
        texto = str(texto)
    texto = remover_acentos(texto)
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("_")
    if not texto:
        return "desconhecido"
    if texto[0].isdigit():
        texto = f"'{texto}'"
    return texto


def normalizar_float(valor, casas: int = 1) -> float:
    return round(float(valor), casas)


def normalizar_inteiro(valor, padrao: int = 0) -> int:
    if pd.isna(valor):
        return padrao
    return int(float(valor))


def extrair_generos(genres_json: str) -> list[str]:
    if not isinstance(genres_json, str):
        return []
    
    if genres_json.strip() == "" or genres_json == "[]":
        return []

    generos = json.loads(genres_json)

    if not isinstance(generos, list):
        return []

    return [
        normalizar_atomo(g["name"])
        for g in generos
        if isinstance(g, dict) and "name" in g
    ]


def extrair_data(data_str: str) -> tuple | None:
    data = pd.to_datetime(data_str, errors="coerce")
    if pd.isna(data):
        return None
    return int(data.year), int(data.month), int(data.day)


def carregar_dataset() -> pd.DataFrame:
    base_dir = os.path.dirname(__file__)
    caminho = os.path.join(base_dir, "..", "data", "tmdb_5000_movies.csv")

    df = pd.read_csv(caminho)
    df = df[COLUNAS].copy()
    df = df.rename(columns=MAPEAMENTO_COLUNAS)

    df = df.dropna(subset=["id", "titulo", "generos", "data_lancamento"])
    df = df[df["duracao"].fillna(0) > 0]

    return df.sample(300, random_state=42)


def gerar_base_prolog(df: pd.DataFrame) -> int:
    base_dir = os.path.dirname(__file__)
    prolog_dir = os.path.join(base_dir, "..", "prolog")
    os.makedirs(prolog_dir, exist_ok=True)

    filmes = []
    generos_aux = []

    for _, linha in df.iterrows():
        data = extrair_data(linha["data_lancamento"])
        if data is None:
            continue
        ano, mes, dia = data

        generos = extrair_generos(linha["generos"])
        if not generos:
            continue

        genero_principal = generos[0]

        movie_id  = normalizar_inteiro(linha["id"])
        titulo    = normalizar_atomo(linha["titulo"])
        idioma    = normalizar_atomo(str(linha.get("idioma_original", "desconhecido")))
        duracao   = normalizar_inteiro(linha["duracao"])
        nota      = normalizar_float(linha["media_votos"])
        votos     = normalizar_inteiro(linha["contagem_votos"])
        orcamento = normalizar_inteiro(linha["orcamento"])
        receita   = normalizar_inteiro(linha["receita"])

        filmes.append(
            f"filme({movie_id}, {titulo}, {genero_principal}, {idioma}, "
            f"data({ano},{mes},{dia}), {duracao}, {nota}, {votos}, "
            f"{orcamento}, {receita}).\n"
        )

        for genero in generos:
            generos_aux.append(f"filme_genero({movie_id}, {genero}).\n")

    pl_path = os.path.join(prolog_dir, "base_filmes.pl")
    
    with open(pl_path, "w", encoding="utf-8") as arquivo:
        for fato in filmes:
            arquivo.write(fato)
        arquivo.write("\n")
        for fato in generos_aux:
            arquivo.write(fato)

    return len(filmes)


if __name__ == "__main__":
    print("Carregando dataset...")
    df = carregar_dataset()

    print("Gerando base Prolog...")
    total = gerar_base_prolog(df)
    print(f"Filmes gerados : {total}")
    print("Arquivo        : prolog/base_filmes.pl")
