from rest_framework.pagination import LimitOffsetPagination


class GeneralPagination(LimitOffsetPagination):
    """Общий пагинатор для записей."""

    default_limit = 100
