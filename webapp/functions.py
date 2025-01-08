import re
from ngramm_search import *
from parsing_finctions import *
from metadata_search_functions import *
from sqlalchemy.engine.row import Row
from classes import SearchResult


def beautify_morph_info(token, txt, step=0):
    # Формируем грамматическую информацию о слове
    wordinf = f'Tокен: {token.token}<br>Лемма: {token.lemma}<br>Часть речи: {token.upos}'
    if token.feats:
        wordinf += f'<br><span>Другие признаки: {token.feats.replace("|", ", ")}</span>'

    # Вставляем HTML-теги для выделения найденного слова
    if token.start_char is not None and token.end_char is not None:
        txt.insert(token.start_char + step, '<span class="found-word"><b class="target">')
        txt.insert(token.end_char + 1 + step, f'</b><span class="description">{wordinf}</span></span>')

    # morph_txt = ''.join(txt)
    return txt


def get_all_info(message, full_q_flag=False):
    """
    Форматирует результаты поиска для отображения в шаблоне.
    """
    out = []
    i = 0
    for token in message:
        message_info = []
        i += 1
        if full_q_flag:
            txt = token.text
            metadata = token.my_metadata  # Используем relationship
        else:
            # Получаем текст сообщения
            if isinstance(token, Row):  # поиск по n-граммам
                text_record = token[0].text
                if not text_record:
                    continue
                txt = list(text_record.text)
                # Получаем метаданные
                metadata = token[0].text.my_metadata  # Используем relationship

            else:
                # поиск по одному слову
                text_record = token.text  # Используем relationship
                if not text_record:
                    continue
                txt = list(text_record.text)
                # Получаем метаданные
                metadata = token.text.my_metadata  # Используем relationship

        if metadata:
            src = metadata.source.source_name if metadata.source else 'Неизвестно'
            comm = metadata.community.community_name if metadata.community else 'Неизвестно'
            thm = metadata.theme.theme_name if metadata.theme else 'Неизвестно'
            dt = str(metadata.date).replace('T', ' ') if metadata.date else 'Неизвестно'

            if full_q_flag:
                beautiful_text = txt

            else:
                if isinstance(token, Row):
                    step = 0
                    for t in token:
                        txt = beautify_morph_info(t, txt, step)
                        step += 2
                    beautiful_text = ''.join(txt)
                else:
                    txt = beautify_morph_info(token, txt)
                    beautiful_text = ''.join(txt)



            message_info.extend([
                str(i) + '.',  # Номер по пороядку вывода
                beautiful_text,  # Текст сообщения с выделенным словом
                src,  # Источник
                comm,  # Сообщество
                thm,  # Тема
                dt  # Время
            ])
            out.append(message_info)
    return out


def full_text_search(query):
    """
    Выполняет поиск текстов, полностью совпадающих с запросом.
    Возвращает SearchResult с query и пустыми aliases.
    """
    query_obj = Text.query.options(
        joinedload(Text.morphs),
        joinedload(Text.my_metadata)
    ).filter(
        Text.text == query
    )
    return SearchResult(query=query_obj)


def query_type(lemma_q, form_q, pos_q):
    pattern_word = re.compile(
        r"[\U0001F600-\U0001F64F]"  # Emoticons
        r"|[\U0001F300-\U0001F5FF]"  # Symbols & Pictographs
        r"|[\U0001F680-\U0001F6FF]"  # Transport & Map Symbols
        r"|[\U0001F700-\U0001F77F]"  # Alchemical Symbols
        r"|[\U0001F780-\U0001F7FF]"  # Geometric Shapes Extended
        r"|[\U0001F800-\U0001F8FF]"  # Supplemental Arrows-C
        r"|[\U0001F900-\U0001F9FF]"  # Supplemental Symbols & Pictographs
        r"|[\U0001FA00-\U0001FA6F]"  # Chess Symbols
        r"|[\U0001FA70-\U0001FAFF]"  # Symbols and Pictographs Extended-A
        r"|[а-яёА-ЯЁ]+"  # Russian words
        r"|[a-zA-Z]+"  # English words
    )
    # pattern_word = re.compile(r'^[а-яёА-ЯЁ]+$')
    pattern_pos = re.compile(r'^[a-zA-Z]+$')
    if lemma_q and form_q and pos_q:
        if pattern_word.match(lemma_q) and pattern_word.match(form_q) and pattern_pos.match(pos_q):
            return 'triple'
    if lemma_q and form_q:
        if pattern_word.match(lemma_q) and pattern_word.match(form_q):
            return 'lemma+form'
    if lemma_q and pos_q:
        if pattern_word.match(lemma_q) and pattern_pos.match(pos_q):
            return 'lemma+pos'
    if form_q and pos_q:
        if pattern_pos.match(pos_q) and pattern_word.match(form_q):
            return 'form+pos'
    if lemma_q:
        if pattern_word.match(lemma_q):
            return 'lemma'
    if form_q:
        if pattern_word.match(form_q):
            return 'form'
    if pos_q:
        if pattern_pos.match(pos_q):
            return 'pos'
    return 'Неверный запрос'


def total_search(page, per_page,
                 q_dict,
                 dist_q,
                 theme_ids=None,
                 comm_q=None,
                 after_datetime_q=None,
                 before_datetime_q=None,
                 register=None,
                 remove_duplicates=None,
                 full_q=False):
    """
    Выбирает подходящую функцию поиска в зависимости от типа запроса
    """
    query_list = []
    if full_q:
        full_q_flag = True
        pagination_query = full_text_search(full_q)
    else:
        full_q_flag = False
        if q_dict:
            for word in q_dict:
                full_q_flag = False
                lemma_q = word['lemma_q']
                form_q = word['form_q']
                pos_q = word['pos_q']

                q_type = query_type(lemma_q, form_q, pos_q)

                if q_type == 'form':
                    pagination_query = exact_search(form_q, register)
                elif q_type == 'lemma':
                    pagination_query = lemma_search(lemma_q)
                elif q_type == 'pos':
                    pagination_query = pos_search(pos_q)
                elif q_type == 'form+pos':
                    pagination_query = exact_pos_search(form_q, pos_q)
                elif q_type == 'lemma+pos':
                    pagination_query = lemma_pos_search(lemma_q, pos_q)
                elif q_type == 'lemma+form':
                    pagination_query = lemma_exact_search(lemma_q, form_q)
                elif q_type == 'triple':
                    pagination_query = triple_search(lemma_q, form_q, pos_q)
                else:
                    return [['', 'Неверный запрос']], 0
                query_list.append(pagination_query)
                pagination_query = search_ngram(query_list, dist_q)
        else:
            return [['', 'Неверный запрос']], 0

    # Поиск по метаинформации

    # фильтр по нескольким темам, если передан список theme_ids
    if theme_ids:
        pagination_query = thema_search(pagination_query, theme_ids)

    if comm_q:
        if comm_q[0]:
            pagination_query = community_search(pagination_query, comm_q)

    # филтр по дате, если указана дата до или после которой должно быть сообщение
    if after_datetime_q or before_datetime_q:
        pagination_query = data_search(pagination_query, after_datetime_q, before_datetime_q)

    # if remove_duplicates:
    #
    #     pagination_query = pagination_query.query.join(Text, Morph.text).group_by(Text.text)
        # pagination_query = (
        #     pagination_query.query
        #     .join(Text, Morph.text)
        #     .group_by(Text.text)
        #     .with_entities(Text.text,
        #                    func.any_value())
        # )
    # else:
    #     pagination_query = pagination_query.query
    pagination_query = pagination_query.query
        # pagination_query = pagination_query.join(Text, Morph.text).filter(Text.text.in_(subquery))

    # Пагинация
    pagination = pagination_query.paginate(page=page, per_page=per_page, error_out=False)
    # Получаем результат
    all_tokens = pagination.items

    data = get_all_info(all_tokens, full_q_flag)

    return data, pagination.total
