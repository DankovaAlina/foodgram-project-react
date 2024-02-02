from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient,
    RecipeTag, Tag, User
)


class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('count_is_favorited',)
    list_display = ('name', 'author')
    list_filter = ('author__username', 'name', 'tags')
    filter_horizontal = ('favorite_recipes', 'shopping_cart_recipes')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Tag)
admin.site.register(User, UserAdmin)
