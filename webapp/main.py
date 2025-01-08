from flask import Flask, render_template, request
from create_db import db, Community
from functions import total_search
import math
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db.app = app
db.init_app(app)


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@app.route('/info', methods=['GET'])
def info():
    return render_template('info.html')


@app.route('/search', methods=['GET'])
def search():
    communities_list = db.session.query(Community.community_name).all()
    return render_template('search.html',
                           communities_list=communities_list)


@app.route('/instruction', methods=['GET'])
def instruction():
    return render_template('instruction.html')


themes_dict_names = {'Чат мероприятия': "фандомные чаты",
                     'Спортивный чат': "спортивные чаты",
                     'Чат студенческого общежития': "чаты общежитий",
                     "чаты геймеров": "чаты геймеров"}


@app.route('/res', methods=['GET'])
def user_search():
    start_time = datetime.datetime.now()

    # Получаем запрос
    lemma_q = request.args.get('lemma-q-1', '')
    form_q = request.args.get('form-q-1', '')
    pos_q = request.args.get('pos-q-1', '')
    dist_q = []
    i = 2
    q_dict = []  # [{lemma_q: '', form_q: '', pos_q:''}, {}]
    while lemma_q or form_q or pos_q:
        word_dict = dict()
        word_dict['lemma_q'] = lemma_q
        lemma_q = request.args.get(f'lemma-q-{i}', '')

        word_dict['form_q'] = form_q
        form_q = request.args.get(f'form-q-{i}', '')

        word_dict['pos_q'] = pos_q
        pos_q = request.args.get(f'pos-q-{i}', '')

        q_dict.append(word_dict)
        dist_q.append(request.args.get(f'dist-q-{i}', ''))
        i += 1

    # поиск по теме
    theme_q = request.args.getlist('theme')
    if theme_q:
        # themes = [themes_dict.get(theme, None) for theme in theme_q]
        themes_name = ', '.join([themes_dict_names.get(theme, '') for theme in theme_q])
    else:
        # themes = None
        themes_name = None

    # поиск по дате
    datetime_after = request.args.get('date-after', '')
    datetime_before = request.args.get('date-before', '')

    # поиск по сообществу
    comm_q = request.args.getlist('comm')
    comm_q = [c for c in set(comm_q) if c]
    if comm_q:
        if comm_q[0]:
            communities_list = [comm[0] for comm in db.session.query(Community.community_name).all()]
            for c in comm_q:
                if c not in communities_list:
                    return render_template(
                        'results.html',
                        data=[['', 'Неправильно введено название сообщества ']],
                        page=1,
                        per_page=20,
                        total=0,
                        total_pages=0)

    # доп настройки
    register = request.args.get('register', '')
    remove_duplicates = request.args.get('duplicates', '')

    # Получаем номер страницы, по умолчанию 1
    page = request.args.get('page', 1, type=int)
    # Определяем количество записей на странице
    per_page = 20
    # Выполняем функцию поиска с пагинацией
    full_q = request.args.get('full-text-q', '')
    data, total = total_search(page,
                               per_page,
                               q_dict,
                               dist_q,
                               theme_q,
                               comm_q,
                               datetime_after,
                               datetime_before,
                               register,
                               remove_duplicates,
                               full_q)
    # Вычисляем общее количество страниц
    total_pages = math.ceil(total / per_page) if per_page else 1

    def url_for_other_page(page_num):
        '''
        Функция для генерации URL с измененным номером страницы
        '''
        args = request.args.to_dict()
        args['page'] = page_num
        return f"{request.path}?{'&'.join([f'{k}={v}' for k, v in args.items()])}"

    current_time = datetime.datetime.now()
    uptime = current_time - start_time
    uptime = str(uptime).split('.')[0]
    return render_template(
        'results.html',
        data=data,
        q_dict=q_dict,
        dist_q=dist_q,
        q_dict_len=range(1, len(q_dict)+1),
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        url_for_other_page=url_for_other_page,
        themes=themes_name,
        communities=', '.join(comm_q),
        datetime_before=datetime_before.replace('T', ' '),
        datetime_after=datetime_after.replace('T', ' '),
        full_q=full_q,
        uptime=uptime
    )


if __name__ == '__main__':
    app.run()
