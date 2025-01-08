from sqlalchemy.orm import joinedload
from create_db import Text, Morph
from sqlalchemy import func


def exact_search(query, register=False):
    if not register:
        pagination_query = Morph.query.options(
            joinedload(Morph.text).joinedload(Text.my_metadata)
        ).filter(func.lower(Morph.token).ilike(func.lower(query)))
    else:
        pagination_query = Morph.query.options(
            joinedload(Morph.text).joinedload(Text.my_metadata)
        ).filter(Morph == query)

    return pagination_query


def lemma_search(query):
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.lemma == query)
    return pagination_query


def pos_search(query):
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.upos == query)
    return pagination_query


def exact_pos_search(from_q, pos_q):
    pos_q = pos_q.upper()
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.token == from_q, Morph.upos == pos_q)
    return pagination_query


def lemma_exact_search(lemma_q, form_q):
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.lemma == lemma_q, Morph.token == form_q)
    return pagination_query


def lemma_pos_search(lemma_q, pos_q):
    pos_q = pos_q.upper()
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.lemma == lemma_q, Morph.upos == pos_q)
    return pagination_query


def triple_search(lemma_q, form_q, pos_q):
    pos_q = pos_q.upper()
    pagination_query = Morph.query.options(
        joinedload(Morph.text).joinedload(Text.my_metadata)
    ).filter(Morph.lemma == lemma_q, Morph.upos == pos_q, Morph.token == form_q)
    return pagination_query