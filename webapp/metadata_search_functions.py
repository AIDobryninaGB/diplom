from datetime import datetime
from create_db import db, Metadata, Theme, Community, Morph
from sqlalchemy.sql import exists


def thema_search(search_result, theme_names):
    """
    Фильтрует запрос по метаинформации (темы).
    :param search_result: объект SearchResult с query и aliases.
    :param theme_names: список названий тем для фильтрации.
    :return: обновленный объект SearchResult.
    """
    # Получаем идентификаторы тем на основе их названий
    theme_ids = db.session.query(Theme.theme_id).filter(Theme.theme_name.in_(theme_names)).all()
    theme_ids = [theme_id[0] for theme_id in theme_ids]

    # Если есть алиасы, фильтруем n-граммы
    if search_result.aliases:
        for alias in search_result.aliases:
            search_result.query = search_result.query.filter(
                exists().where(
                    (Metadata.message_id_meta == alias.message_id_word) &
                    (Metadata.theme_id_meta.in_(theme_ids))
                )
            )
    else:
        # Если алиасов нет, фильтруем по Text.message_id
        search_result.query = search_result.query.join(Metadata).filter(
            Metadata.theme_id_meta.in_(theme_ids)
        )

    return search_result


def community_search(search_result, comm_q):
    """
    Фильтрует запрос по метаинформации (сообщество).
    :param search_result: объект SearchResult с query и aliases.
    :param comm_q: список названий сообществ для фильтрации.
    """
    comm_ids = db.session.query(Community.community_id).filter(
        Community.community_name.in_(comm_q)
    ).all()
    comm_ids = [comm_id[0] for comm_id in comm_ids]

    # Если алиасы есть, применяем фильтр для n-граммного поиска
    if search_result.aliases:
        for alias in search_result.aliases:
            search_result.query = search_result.query.filter(
                exists().where(
                    (Metadata.message_id_meta == alias.message_id_word) &
                    (Metadata.community_id_meta.in_(comm_ids))
                )
            )
    else:
        # Для полнотекстового поиска — фильтрация по `Text.message_id`
        search_result.query = search_result.query.join(Metadata).filter(
            Metadata.community_id_meta.in_(comm_ids)
        )

    return search_result


def data_search(search_result, after_datetime_q=None, before_datetime_q=None):
    """
    Фильтрует запрос по диапазону дат.
    :param search_result: объект SearchResult с query и aliases.
    :param after_datetime_q: начальная дата в формате '%Y-%m-%dT%H:%M'.
    :param before_datetime_q: конечная дата в формате '%Y-%m-%dT%H:%M'.
    :return: обновленный объект SearchResult.
    """
    if after_datetime_q:
        after_datetime_q = datetime.strptime(after_datetime_q, '%Y-%m-%dT%H:%M')
    if before_datetime_q:
        before_datetime_q = datetime.strptime(before_datetime_q, '%Y-%m-%dT%H:%M')

    # Фильтрация для n-грамм с алиасами
    if search_result.aliases:
        for alias in search_result.aliases:
            if after_datetime_q and before_datetime_q:
                search_result.query = search_result.query.filter(
                    exists().where(
                        (Metadata.message_id_meta == alias.message_id_word) &
                        (Metadata.date > after_datetime_q) &
                        (Metadata.date < before_datetime_q)
                    )
                )
            elif after_datetime_q:
                search_result.query = search_result.query.filter(
                    exists().where(
                        (Metadata.message_id_meta == alias.message_id_word) &
                        (Metadata.date > after_datetime_q)
                    )
                )
            elif before_datetime_q:
                search_result.query = search_result.query.filter(
                    exists().where(
                        (Metadata.message_id_meta == alias.message_id_word) &
                        (Metadata.date < before_datetime_q)
                    )
                )
    else:
        # Фильтрация для полнотекстового поиска по Text.message_id
        if after_datetime_q and before_datetime_q:
            search_result.query = search_result.query.join(Metadata).filter(
                (Metadata.date > after_datetime_q) & (Metadata.date < before_datetime_q)
            )
        elif after_datetime_q:
            search_result.query = search_result.query.join(Metadata).filter(
                Metadata.date > after_datetime_q
            )
        elif before_datetime_q:
            search_result.query = search_result.query.join(Metadata).filter(
                Metadata.date < before_datetime_q
            )

    return search_result
