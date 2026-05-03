# APS - Knowledge Engine

Projeto desenvolvido na disciplina de Lógica e Matemática Discreta.

## Objetivo

Este projeto transforma dados brutos de filmes em fatos lógicos no formato Prolog e permite responder perguntas por meio de consultas e regras. A ideia é representar conhecimento de forma simbólica, determinística e explicável.

## Dataset utilizado

* **TMDB 5000 Movies**
* Fonte: Kaggle
* Foi utilizada apenas a tabela `tmdb_5000_movies.csv`

## Estrutura do projeto

```text
projeto/
├── data/
│   └── tmdb_5000_movies.csv
├── prolog/
│   ├── base_filmes.pl
│   └── queries.pl
├── src/
│   └── etl.py
└── README.md
```

## O que o ETL faz

O script em Python:

1. lê o CSV original;
2. seleciona colunas relevantes;
3. limpa e normaliza textos para o formato aceito pelo Prolog;
4. converte datas para `data(ano,mes,dia)`;
5. extrai os gêneros do campo JSON;
6. gera a base de conhecimento em Prolog.

## Predicados gerados

A base usa dois predicados principais:

```prolog
filme(Id, Titulo, GeneroPrincipal, Idioma, Data, Duracao, Nota, Votos, Orcamento, Receita).
filme_genero(Id, Genero).
```

## Como executar

### 1. Gerar a base

Execute o script Python:

```bash
python src/etl.py
```

Isso gera o arquivo:

```text
prolog/base_filmes.pl
```

### 2. Testar no Prolog

Abra o SWI-Prolog ou o SWISH e carregue os fatos e as regras do arquivo `queries.pl` junto com `base_filmes.pl`.

No SWISH, cole o conteúdo dos dois arquivos na área  **Program** .

> **Observação:**  
> As consultas avançadas foram desenvolvidas utilizando técnicas como agregação, ordenação e inferência lógica, atendendo ao critério de **perguntas sofisticadas** da avaliação.

## Queries e explicação

### Consultas simples (auxiliares)

### 1. Filmes bem avaliados

```prolog
filmes_bem_avaliados(Titulo, Nota) :-
    filme(_, Titulo, _, _, _, _, Nota, _, _, _),
    Nota > 7.
```

Retorna filmes com nota maior que 7. Essa query usa comparação numérica para filtrar os registros.

Exemplo:

```prolog
?- filmes_bem_avaliados(Titulo, Nota).
```

---

### 2. Filmes longos

```prolog
filmes_longos(Titulo, Duracao) :-
    filme(_, Titulo, _, _, _, Duracao, _, _, _, _),
    Duracao > 120.
```

Retorna filmes com duração maior que 120 minutos.

Exemplo:

```prolog
?- filmes_longos(Titulo, Duracao).
```

---
### Consultas avançadas 

### 3. Ranking de lucro

```prolog
ranking_lucro(Ranking) :-
    setof(Lucro-Titulo,
        (filme(_, Titulo, _, _, _, _, _, _, Orcamento, Receita),
         Orcamento > 0,
         Receita > 0,
         Lucro is Receita - Orcamento),
        Lista),
    reverse(Lista, Ranking).
```

Calcula o lucro de cada filme (`receita - orçamento`), ordena os pares `Lucro-Titulo` e inverte a lista para mostrar os maiores lucros primeiro.

Exemplo:

```prolog
?- ranking_lucro(Ranking).
```

---

### 4. Média de nota por gênero

```prolog
media_genero(Genero, Media) :-
    setof(Genero, Id^filme_genero(Id, Genero), Generos),
    member(Genero, Generos),
    findall(Nota,
        (filme(Id, _, _, _, _, _, Nota, _, _, _),
         filme_genero(Id, Genero),
         Nota > 0),
        Lista),
    length(Lista, N),
    N > 0,
    sum_list(Lista, Soma),
    Media is Soma / N.
```

Calcula a média das notas de filmes de cada gênero. Primeiro obtém a lista de gêneros únicos, depois coleta as notas dos filmes daquele gênero e calcula a média.

Exemplo:

```prolog
?- media_genero(Genero, Media).
```

---

### 5. Filme subestimado

```prolog
filme_subestimado(Titulo) :-
    filme(_, Titulo, _, _, _, _, Nota, Votos, _, _),
    Nota >= 7,
    Votos < 100.
```

Retorna filmes com nota alta, mas poucos votos. A ideia é identificar obras boas que tiveram pouca visibilidade.

Exemplo:

```prolog
?- filme_subestimado(Titulo).
```

---

### 6. Década de lançamento

```prolog
decada(Ano, Decada) :-
    Decada is (Ano // 10) * 10.
```

Converte um ano em sua década correspondente. Por exemplo, `1999` vira `1990`.

Exemplo:

```prolog
?- decada(1999, D).
```

---

### 7. Média de nota por década

```prolog
media_decada(Decada, Media) :-
    findall(Nota,
        (filme(_, _, _, _, data(Ano,_,_), _, Nota, _, _, _),
         Nota > 0,
         decada(Ano, Decada)),
        Lista),
    length(Lista, N),
    N > 0,
    sum_list(Lista, Soma),
    Media is Soma / N.
```

Calcula a média de notas dos filmes lançados em uma década específica.

Exemplo:

```prolog
?- media_decada(2000, Media).
```

---

### 8. Melhor filme por gênero

```prolog
melhor_filme_genero(Genero, Titulo, Nota) :-
    filme(Id, Titulo, _, _, _, _, Nota, _, _, _),
    filme_genero(Id, Genero),
    Nota > 0,
    \+ (
        filme(Id2, _, _, _, _, _, Nota2, _, _, _),
        filme_genero(Id2, Genero),
        Nota2 > Nota
    ).
```

Retorna um filme cujo valor de nota é o maior dentro do gênero informado. A negação é usada para garantir que não exista outro filme do mesmo gênero com nota maior.

Exemplo:

```prolog
?- melhor_filme_genero(drama, Titulo, Nota).
```

---

### 9. ROI

```prolog
roi(Titulo, ROI) :-
    filme(_, Titulo, _, _, _, _, _, _, Orcamento, Receita),
    Orcamento > 0,
    Receita > 0,
    ROI is Receita / Orcamento.
```

Calcula o retorno sobre investimento de cada filme como `receita / orçamento`.

Exemplo:

```prolog
?- roi(Titulo, ROI).
```

---

### 10. Ranking de ROI

```prolog
ranking_roi(Ranking) :-
    findall(ROI-Titulo,
        ( filme(_, Titulo, _, _, _, _, _, _, Orcamento, Receita),
          Orcamento > 0,
          Receita > 0,
          ROI is Receita / Orcamento
        ),
        Lista),
    sort(Lista, Ordenada),
    reverse(Ordenada, Ranking).
```

Cria um ranking dos filmes com maior retorno sobre investimento.

Exemplo:

```prolog
?- ranking_roi(Ranking).
```

## Observações

* Os nomes foram normalizados para o formato aceito pelo Prolog.
* Datas seguem o padrão `data(ano,mes,dia)`, pois o ano é o atributo mais relevante para inferência temporal, facilitando consultas como agrupamento por década e comparações entre períodos.
* As consultas utilizam agregação, ordenação, comparação e inferência lógica.
* As consultas principais foram projetadas para extrair conhecimento da base, atendendo ao critério de **perguntas sofisticadas** da avaliação.
* As consultas simples são utilizadas apenas para validação e exploração inicial da base.
