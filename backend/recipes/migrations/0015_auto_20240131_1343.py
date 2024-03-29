# Generated by Django 3.2.3 on 2024-01-31 13:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20240125_1448'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'default_related_name': 'recipe_ingredient', 'verbose_name': 'Ингредиенты в рецептах'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'default_related_name': 'tag_ingredient', 'verbose_name': 'Теги в рецептах'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='favorite_recipes',
            field=models.ManyToManyField(blank=True, related_name='favorite_recipes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи, у которых рецепт добавлен в избранное'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='shopping_cart_recipes',
            field=models.ManyToManyField(blank=True, related_name='shopping_cart_recipes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи, у которых рецепт добавлен в список покупок'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipes.tag', verbose_name='Тег'),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscriptions',
            field=models.ManyToManyField(related_name='_recipes_user_subscriptions_+', to=settings.AUTH_USER_MODEL, verbose_name='Подписки'),
        ),
    ]
