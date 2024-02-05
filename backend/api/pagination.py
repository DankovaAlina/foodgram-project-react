from rest_framework.pagination import PageNumberPagination


class GeneralPagination(PageNumberPagination):
    """Общий пагинатор для записей."""

    page_size = 10
    page_size_query_param = 'limit'
    page_query_param = 'page'
