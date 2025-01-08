from create_db import db, Morph
from sqlalchemy.orm import aliased
from classes import SearchResult

def search_ngram(queries, word_distance):
    """
    Расширенный поиск по n-граммам с произвольной длиной.
    Возвращает SearchResult с query и aliases.
    """
    morph_aliases = [aliased(Morph) for _ in queries]

    ngram_query = db.session.query(*morph_aliases)
    for i in range(1, len(morph_aliases)):
        ngram_query = ngram_query.join(
            morph_aliases[i],
            (morph_aliases[i - 1].message_id_word == morph_aliases[i].message_id_word) &
            (morph_aliases[i].word_id == morph_aliases[i - 1].word_id + word_distance[i - 1])
        )

    for i, query in enumerate(queries):
        ngram_query = ngram_query.filter(
            morph_aliases[i].word_id.in_(query.with_entities(Morph.word_id).subquery())
        )

    return SearchResult(query=ngram_query, aliases=morph_aliases)


