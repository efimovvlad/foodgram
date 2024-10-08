import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscriptions

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователей."""

    email = serializers.EmailField()

    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (*DjoserUserCreateSerializer.Meta.fields,)


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        is_subscribed = Subscriptions.objects.filter(
            user=request.user, author=user
        ).exists()
        return is_subscribed


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe для списка подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, recipe):
        """Возращает рецепты согласно параметру "recipes_limit" в запросе."""
        request = self.context.get('request')
        recipes_limit = int(request.GET.get('recipes_limit', 1000))
        recipes = recipe.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        """Проверяет, добавлен ли рецепт в избранное."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and recipe.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет, добавлен ли рецепт в список покупок."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and recipe.shopping_cart.filter(user=user).exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def to_representation(self, instance):
        return RecipeRetrieveSerializer(instance, context=self.context).data

    @staticmethod
    def validate_items(items, model, field_name):
        if not items:
            raise serializers.ValidationError(
                {field_name: f'Поле {field_name} не может быть пустым.'}
            )
        existing_items = model.objects.filter(
            id__in=items).values_list('id', flat=True)
        missing_items = set(items) - set(existing_items)
        if missing_items:
            raise serializers.ValidationError(
                {field_name: f'Элемент(ы) с id {missing_items} не существует.'}
            )
        non_unique_ids = {item for item in items if items.count(item) > 1}
        if non_unique_ids:
            raise serializers.ValidationError(
                {field_name: f'Элементы с id {non_unique_ids} не уникальны.'}
            )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле "ingredients" не может быть пустым.'
            )
        ingredients_ids = [item['id'] for item in ingredients]
        self.validate_items(ingredients_ids, Ingredient, 'ingredients')
        self.validate_items(tags, Tag, 'tags')
        return data

    def set_ingredients(self, recipe, ingredients):
        """Добавляет ингредиенты в промежуточную модель."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe,
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.save()
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)
