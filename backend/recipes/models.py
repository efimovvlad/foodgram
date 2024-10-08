from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20
    )

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

    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=5000
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes_images/'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1),)
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

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1),)
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

    def __str__(self):
        return f'{self.ingredient.name} для {self.recipe.name}'


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

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

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

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

    def __str__(self):
        return (
            f'{self.user.username} добавил '
            f'в список покупок {self.recipe.name}'
        )
