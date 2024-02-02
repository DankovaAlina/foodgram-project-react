import csv

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import UserAuthMixin
from api.pagination import GeneralPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteAddSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeReadSerializer, ShoppingCartSerializer, TagSerializer,
    UserInfoSerializer, UserResetPasswordSerializer, UserSignupSerializer,
    UserSubscriptionSerializer, UserTokenSerializer
)
from recipes.consts import ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART
from recipes.models import Ingredient, Recipe, Tag, User


class UserToken(UserAuthMixin):
    """Вьюсет получения токена."""

    serializer_class = UserTokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    pagination_class = GeneralPagination
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSignupSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        url_name='get_self_info',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Получение информации о себе."""
        serializer = UserInfoSerializer(
            self.request.user,
            context={'request': self.request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_name='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """Смена пароля."""
        user = self.request.user
        serializer = UserResetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        """Подписка/удаление подписки на пользователя."""
        user = self.request.user
        user_to_subscribe = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = UserSubscriptionSerializer(
                user_to_subscribe,
                context={'request': self.request},
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not user.subscriptions.filter(id=user_to_subscribe.id).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'errors': ('Подписки на данного '
                                   'пользователя не существует.')
                    }
                )
            user.subscriptions.remove(user_to_subscribe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_name='subscriptions',
        serializer_class=UserSubscriptionSerializer,
        pagination_class=GeneralPagination,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Получение подписок пользователя."""
        queryset = self.request.user.subscriptions.all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = GeneralPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта в избранном."""
        if request.method == 'POST':
            recipe = Recipe.objects.filter(id=pk).first()
            if not recipe:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            request.data['user'] = self.request.user
            serializer = FavoriteAddSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            recipe = get_object_or_404(Recipe, id=pk)
            if not recipe.favorite_recipes.filter(
                id=self.request.user.id
            ).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'errors': ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART.
                          format('избранное')}
                )
            recipe.favorite_recipes.remove(self.request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в списке покупок."""
        if request.method == 'POST':
            recipe = Recipe.objects.filter(id=pk).first()
            if not recipe:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            request.data['user'] = self.request.user
            serializer = ShoppingCartSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            recipe = get_object_or_404(Recipe, id=pk)
            if not recipe.shopping_cart_recipes.filter(
                id=self.request.user.id
            ).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'errors': ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART
                          .format('список покупок')}
                )
            recipe.shopping_cart_recipes.remove(self.request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Сохранение файла списка покупок."""
        is_in_shopping_cart = Q(
            shopping_cart_recipes__id__icontains=self.request.user.id
        )
        recipes = self.queryset.filter(is_in_shopping_cart)
        shopping_cart = {}
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition":
                     'attachment; filename="shopping_list.csv"'},
        )
        for recipe in recipes:
            for ingr_rel in recipe.recipe_ingredient.all():
                if ingr_rel.ingredient not in shopping_cart:
                    shopping_cart[ingr_rel.ingredient] = ingr_rel.amount
                else:
                    shopping_cart[ingr_rel.ingredient] += ingr_rel.amount
        writer = csv.writer(response)
        writer.writerow(['Название', 'Единица измерения', 'Количество'])
        for ingredient, amount in shopping_cart.items():
            writer.writerow(
                [ingredient.name, ingredient.measurement_unit, amount]
            )
        return response
