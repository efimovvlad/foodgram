from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from .constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_TEXT,
    MAX_LENGTH_UNIT,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
)

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    slug = models.CharField(max_length=MAX_LENGTH_SLUG, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(max_length=MAX_LENGTH_NAME)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient_unit',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(max_length=MAX_LENGTH_NAME)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    text = models.TextField(max_length=MAX_LENGTH_TEXT)
    image = models.ImageField(upload_to='recipes_images/')
    pub_date = models.DateTimeField(auto_now_add=True)
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),)
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author',),
                name='unique_recipe_author',
            ),
        )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(
        validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),)
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_recipe_ingredient',
            ),
        )


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            ),
        )
