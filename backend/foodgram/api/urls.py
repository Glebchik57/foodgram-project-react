from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet)
router.register('ingredients', IngredientViewSet,  basename='ingredients')
router.register('tags', TagViewSet,  basename='tags')
router.register('recipes', RecipeViewSet,  basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
