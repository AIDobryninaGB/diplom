class SearchResult:
    def __init__(self, query, aliases=None):
        """
        Универсальный контейнер для хранения запроса и алиасов.
        :param query: SQLAlchemy Query object.
        :param aliases: Список алиасов Morph, если используются.
        """
        self.query = query
        self.aliases = aliases or []