
filmes_bem_avaliados(Titulo, Nota) :-
    filme(_, Titulo, _, _, _, _, Nota, _, _, _),
    Nota > 7.


filmes_longos(Titulo, Duracao) :-
    filme(_, Titulo, _, _, _, Duracao, _, _, _, _),
    Duracao > 120.


ranking_lucro(Ranking) :-
    setof(Lucro-Titulo,
        (filme(_, Titulo, _, _, _, _, _, _, Orcamento, Receita),
         Orcamento > 0,
         Receita > 0,
         Lucro is Receita - Orcamento),
        Lista),
    reverse(Lista, Ranking).


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


filme_subestimado(Titulo) :-
    filme(_, Titulo, _, _, _, _, Nota, Votos, _, _),
    Nota >= 7,
    Votos < 100.


decada(Ano, Decada) :-
    Decada is (Ano // 10) * 10.


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


melhor_filme_genero(Genero, Titulo, Nota) :-
    filme(Id, Titulo, _, _, _, _, Nota, _, _, _),
    filme_genero(Id, Genero),
    Nota > 0,
    \+ (
        filme(Id2, _, _, _, _, _, Nota2, _, _, _),
        filme_genero(Id2, Genero),
        Nota2 > Nota
    ).


roi(Titulo, ROI) :-
    filme(_, Titulo, _, _, _, _, _, _, Orcamento, Receita),
    Orcamento > 0,
    Receita > 0,
    ROI is Receita / Orcamento.


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