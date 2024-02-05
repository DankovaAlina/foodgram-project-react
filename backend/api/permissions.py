from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsAuthorOrReadOnly(BasePermission):
    """
    Проверяет, что вносить изменения может
    только автор объекта.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return (request.user.is_authenticated and (request.user == obj.author))

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated
