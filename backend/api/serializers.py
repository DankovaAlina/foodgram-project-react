import base64
import webcolors

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import get_object_or_404
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from recipes.consts import (
    ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART, ERROR_MESSAGE_SIGNUP,
    MAX_LEN_EMAIL, MAX_LEN_NAME
)
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User
)
from recipes.validators import username_validator, validate_username_me


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserInfoSerializer(serializers.ModelSerializer):
    """Сериализатор информации пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Возвращает информацию о подписке пользователя."""
        user = self.context['request'].user
        if user.id is None:
            return False
        return user.subscriptions.filter(id=obj.id).exists()


class UserSignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    email = serializers.EmailField(max_length=MAX_LEN_EMAIL)
    username = serializers.CharField(
        max_length=MAX_LEN_NAME,
        validators=(username_validator, validate_username_me)
    )
    password = serializers.CharField(
        max_length=MAX_LEN_NAME,
        write_only=True
    )

    class Meta():
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password'
                  )

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        errors = {}
        users = User.objects.filter(
            Q(email=email) | Q(username=username)
        )
        if users:
            if any(user.username == username for user in users):
                errors['email'] = ERROR_MESSAGE_SIGNUP.format(
                    'username', 'email'
                )
            if any(user.email == email for user in users):
                errors['username'] = ERROR_MESSAGE_SIGNUP.format(
                    'email', 'username'
                )
            if errors:
                raise serializers.ValidationError(errors)

        attrs['password'] = make_password(attrs.get('password'))
        return attrs


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор получения токена."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, validated_data):
        user = validated_data.get('user')
        token, created = Token.objects.get_or_create(user=user)
        return token

    def validate(self, attrs):
        user = get_object_or_404(
            User,
            email=attrs.get('email')
        )
        if not user.check_password(attrs.get('password')):
            raise serializers.ValidationError('Неверный пароль.')
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        return {'auth_token': str(instance.key)}


class UserResetPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        user = self.instance
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError('Неверный пароль.')
        return attrs


class Name2HexColor(serializers.Field):
    """Сериализатор кодировки цвета."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError('Цвет не определен.')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    color = Name2HexColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор связи рецепта и ингредиента."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор связи рецепта и тега."""

    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = ('tag',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и редактирования рецепта."""

    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    ingredients = RecipeIngredientsSerializer(many=True, required=True)
    author = UserInfoSerializer(required=False)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time'
                  )
        read_only_fields = ('id', 'author')

    def validate(self, attrs):
        required_fields = (
            'ingredients', 'tags',
            'name', 'text', 'cooking_time'
        )
        errors = {}
        for field in required_fields:
            if field not in attrs or not attrs[field]:
                errors[field] = 'Поле обязательно для заполнения.'
        if not self.instance and 'image' not in attrs:
            errors['image'] = 'Поле обязательно для заполнения.'
        if errors:
            raise serializers.ValidationError(errors)
        unique_ingredients = set(
            [ingredient['ingredient']['id']
             for ingredient in attrs['ingredients']]
        )
        if len(unique_ingredients) != len(attrs['ingredients']):
            errors['ingredients'] = 'Нельзя дублировать игредиент.'
        unique_tags = set(attrs['tags'])
        if len(unique_tags) != len(attrs['tags']):
            errors['tags'] = 'Нельзя дублировать тег.'
        for ingredient in unique_ingredients:
            if not Ingredient.objects.filter(id=ingredient).exists():
                errors['ingredients'] = (f'Ингредиент [{ingredient}] '
                                         'не существует.')
        for tag in unique_tags:
            if not Tag.objects.filter(id=tag).exists():
                errors['tags'] = f'Тег [{tag}] не существует.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def add_tags(self, recipe, tags_data):
        """Добавляет теги к рецепту."""
        for tag_id in tags_data:
            RecipeTag.objects.create(
                tag=Tag.objects.get(id=tag_id),
                recipe=recipe
            )

    def add_ingredients(self, recipe, ingredients_data):
        """Добавляет ингредиенты к рецепту."""
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['ingredient']['id']
                ),
                amount=ingredient_data['amount'],
                recipe=recipe
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_ingredients(recipe, ingredients_data)
        self.add_tags(recipe, tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeTag.objects.filter(recipe=recipe).delete()
        self.add_ingredients(recipe, ingredients_data)
        self.add_tags(recipe, tags_data)
        return recipe

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return serializer


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецепта."""

    tags = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    author = UserInfoSerializer()
    image = Base64ImageField()
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    # image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_tags(self, obj):
        """Получает теги рецепта."""
        return TagSerializer(
            Tag.objects.filter(recipes__recipe=obj),
            many=True
        ).data

    def get_ingredients(self, obj):
        """Получает ингредиенты рецепта."""
        return RecipeIngredientsSerializer(
            RecipeIngredient.objects.filter(recipe=obj),
            many=True
        ).data

    def get_is_favorited(self, obj):
        """Получает информацию о добавлении рецепта в избранное."""
        user = self.context['request'].user
        return obj.favorite_recipes.filter(id=user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получает информацию о добавлении рецепта в список покупок."""
        user = self.context['request'].user
        return obj.shopping_cart_recipes.filter(id=user.id).exists()


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteAddSerializer(RecipeShortInfoSerializer):
    """Сериализатор добавления рецепта в избранное."""

    def validate(self, attrs):
        if self.instance.favorite_recipes.filter(
            id=self.initial_data['user'].id
        ).exists():
            raise serializers.ValidationError(
                ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART.format('избранное')
            )
        return attrs

    def save(self, **kwargs):
        self.instance.favorite_recipes.add(self.initial_data['user'])
        return self.instance


class ShoppingCartSerializer(RecipeShortInfoSerializer):
    """Сериализатор добавления рецепта в список покупок."""

    def validate(self, attrs):
        if self.instance.shopping_cart_recipes.filter(
            id=self.initial_data['user'].id
        ).exists():
            raise serializers.ValidationError(
                ERROR_MESSAGE_DELETE_FAV_SHOPPING_CART.format('список покупок')
            )
        return attrs

    def save(self, **kwargs):
        self.instance.shopping_cart_recipes.add(self.initial_data['user'])
        return self.instance


class UserSubscriptionSerializer(UserInfoSerializer):
    """Сериализатор подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserInfoSerializer.Meta):
        fields = UserInfoSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            'id', 'email', 'username',
            'first_name', 'last_name'
        )

    def validate(self, attrs):
        user = self.context['request'].user
        user_to_subscribe = self.instance
        if user == user_to_subscribe:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if user.subscriptions.filter(id=user_to_subscribe.id).exists():
            raise serializers.ValidationError('Подписка уже существует.')
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.subscriptions.add(self.instance)
        return self.instance

    def get_recipes(self, obj):
        """Получает рецепты автора, на которого подписан пользователь."""
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeShortInfoSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """
        Получает кол-во рецептов автора,
        на которого подписан пользователь.
        """
        return Recipe.objects.filter(author=obj).count()
