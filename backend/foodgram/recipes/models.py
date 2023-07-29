from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from colorfield.fields import ColorField

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    measurement_unit = models.CharField('Единица измерения', max_length=10)

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название тега', unique=True, max_length=200)
    color = ColorField('Цвет', format="hex", unique=True, max_length=7)
    slug = models.SlugField('Slug', unique=True, max_length=200)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название рецепта', max_length=200)
    text = models.TextField('Описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes'
    )
    image = models.ImageField(
        "Изображение рецепта",
        upload_to="static/recipe",
        blank=True,
        null=True,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipe',
        related_name='recipes',
        verbose_name='список ингридиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'обычно меньше минуты не готовят')],
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='список ингридиентов',
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='recipe_ingredients'
    )
    amount = models.FloatField(
        verbose_name='количество ингридиента',
        default=1,
        validators=[MinValueValidator(1, 'добавь либо 1, либо ничего')],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique'
            )
        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_list'
            )
        ]
