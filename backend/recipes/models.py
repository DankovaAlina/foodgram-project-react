from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from recipes.consts import (
    MAX_LEN_COLOR, MAX_LEN_EMAIL, MAX_LEN_NAME,
    MAX_LEN_PASSWORD, MAX_LEN_RECIPE_NAME
)
from recipes.validators import username_validator, validate_username_me


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LEN_EMAIL,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LEN_NAME,
        unique=True,
        validators=(username_validator, validate_username_me)
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LEN_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LEN_NAME
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_LEN_PASSWORD
    )
    subscriptions = models.ManyToManyField('self', verbose_name='Подписки')

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=MAX_LEN_NAME)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEN_NAME
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        unique=True,
        max_length=MAX_LEN_NAME
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=MAX_LEN_COLOR,
        default='#ffffff'
    )
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField('Название', max_length=MAX_LEN_RECIPE_NAME)
    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Игредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1 минуты.'
            ),
        )
    )
    favorite_recipes = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        verbose_name='Пользователи, у которых рецепт добавлен в избранное',
        blank=True
    )
    shopping_cart_recipes = models.ManyToManyField(
        User,
        related_name='shopping_cart_recipes',
        verbose_name=('Пользователи, у которых рецепт '
                      'добавлен в список покупок'),
        blank=True
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    @property
    @admin.display(description='Общее число добавлений рецепта в избранное')
    def count_is_favorited(self):
        return self.favorite_recipes.count()

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                1,
                message='Количество не может быть меньше 1.'
            ),
        )
    )

    class Meta:
        default_related_name = 'recipe_ingredient'
        verbose_name = 'Ингредиент в рецептах'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    """Модель связи рецепта и тега."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Тег'
    )

    class Meta:
        default_related_name = 'tag_ingredient'
        verbose_name = 'Тег в рецептах'
        verbose_name_plural = 'Теги в рецептах'

    def __str__(self):
        return self.tag.name
