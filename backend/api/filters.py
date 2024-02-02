from django_filters import rest_framework as filters
from django.db.models import Q

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр игредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.id:
            return queryset
        condition_is_favorited = Q(
            favorite_recipes__id__icontains=self.request.user.id
        )
        if value:
            return queryset.filter(condition_is_favorited)
        else:
            return queryset.exclude(condition_is_favorited)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.id:
            return queryset
        condition_is_in_shopping_cart = Q(
            shopping_cart_recipes__id__icontains=self.request.user.id
        )
        if value:
            return queryset.filter(condition_is_in_shopping_cart)
        else:
            return queryset.exclude(condition_is_in_shopping_cart)
