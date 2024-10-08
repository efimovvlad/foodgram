from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150,
        validators=(validate_username,)
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users_avatars/',
        blank=True,
        null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель подписки."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='authors',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='followers',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
