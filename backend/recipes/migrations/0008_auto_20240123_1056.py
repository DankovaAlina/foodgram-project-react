# Generated by Django 3.2.3 on 2024-01-23 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240122_1659'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'default_related_name': 'recipe_ingredient'},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_favorited',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_in_shopping_cart',
        ),
        migrations.AddField(
            model_name='recipe',
            name='favorite_recipes',
            field=models.ManyToManyField(related_name='favorite_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart_recipe',
            field=models.ManyToManyField(related_name='shopping_cart_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.recipe'),
        ),
    ]
