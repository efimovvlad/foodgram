from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME
)
from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=(validate_username,)
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=MAX_LENGTH_FIRST_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_LAST_NAME)
    avatar = models.ImageField(
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
        related_name='authors',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
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
