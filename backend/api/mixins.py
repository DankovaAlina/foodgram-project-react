from rest_framework import generics, status


class UserAuthMixin(generics.CreateAPIView):
    """Миксин для пользователей."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
