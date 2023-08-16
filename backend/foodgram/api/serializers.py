import webcolors
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import ValidationError

from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Follow, User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            *User.REQUIRED_FIELDS,
            User.USERNAME_FIELD,
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True,)
    new_password = serializers.CharField(required=True,)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'пароль не соответсвует установленному'
            )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_in_shopping_list = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_list",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_in_shopping_list(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated or self.context.get("request") is not None:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    @staticmethod
    def get_ingredients(obj):
        ingredients = IngredientsRecipe.objects.filter(recipe=obj)
        return IngredientsRecipeSerializer(ingredients, many=True).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientsRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        IngredientsRecipe.objects.bulk_create(
            IngredientsRecipe(
                recipe=recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"]
            )
            for ingredient in ingredients
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'в рецепте должен быть хоть один ингридиент'
            )
        for ingredient in ingredients:
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиент уже добавлен в рецепт')
            ingredient_list.append(ingredient)
        return data

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        image = validated_data.pop("image")
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        IngredientsRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = RecipeSerializer(
            recipe, context={"request": self.context.get("request")}
        ).data
        return data


class RecipeShortShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.favorite.filter(recipe=data['recipe']).exists():
            raise ValidationError(
                'Рецепт уже в избранном'
            )
        return data

    def representation(self, instance):
        return RecipeShortShowSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise ValidationError(
                'Рецепт уже есть в списке покупок'
            )
        return data

    def representation(self, instance):
        return RecipeShortShowSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        ).data


class FollowSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeShortShowSerializer(
            recipes,
            many=True,
            context=self.context
        )
        return serializer.data

    def validate(self, data):
        author_id = (
            self.context.get('request').parser_context.get('kwargs').get('id')
        )
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user

        if user.follower.filter(author=author).exists():
            raise ValidationError(
                detail='Вы уже подписанны',
                code=status.HTTP_400_BAD_REQUEST,
            )

        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )

        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes_count',
            'recipes',
            'is_subscribed',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )
