from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscriptions
from .filters import IngredientFilter, RecipeFilter
from .paginators import PaginatorWithLimit
from .permissions import ReadOnlyOrAuthor
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeRetrieveSerializer,
    ShortRecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from .utils import generate_txt

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """ViewSet для управления пользователями."""

    pagination_class = PaginatorWithLimit

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.request.method == 'GET':
            return UserSerializer
        return UserCreateSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if request.method == 'POST':
            _, created = Subscriptions.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                raise ValidationError(
                    'Вы уже подписаны на этого пользователя.'
                )
            return Response(
                SubscriptionsSerializer(
                    author, context={'request': request}
                ).data, status=status.HTTP_201_CREATED
            )
        subscription = Subscriptions.objects.filter(
            user=user, author=author).first()
        if not subscription:
            raise ValidationError('Вы не подписаны на этого пользователя.')
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления ингридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.AllowAny,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = PaginatorWithLimit
    permission_classes = (ReadOnlyOrAuthor,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'get_link'):
            return RecipeRetrieveSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        permission_classes=(permissions.AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(
            reverse('shortlink', args=[recipe.pk])
        )
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'Список покупок пуст.',
                status=status.HTTP_204_NO_CONTENT
            )
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        response = FileResponse(
            generate_txt(ingredients),
            content_type='text/plain',
            filename='shopping_list.txt'
        )
        return response

    @staticmethod
    def shoppingcart_favorite_method(request, pk, model, delete_message):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                return Response(
                    ShortRecipeSerializer(recipe).data,
                    status=status.HTTP_201_CREATED
                )
            raise ValidationError('Этот рецепт уже в списке.')
        subscription = model.objects.filter(user=user, recipe=recipe).first()
        if not subscription:
            raise ValidationError('Вы не подписаны на этот рецепт.')
        subscription.delete()
        return Response(
            {'delete': delete_message},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        url_path='favorite',
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self.shoppingcart_favorite_method(
            request, pk, Favorite,
            delete_message='Рецепт удален из избранного'
        )

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.shoppingcart_favorite_method(
            request, pk, ShoppingCart,
            delete_message='Рецепт удален из списка покупок'
        )


def redirect_to_recipe_detail(request, pk):
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'/recipes/{pk}/')
    else:
        raise ValidationError(f'Рецепт с id {pk} отсутствует.')
