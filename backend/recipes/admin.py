from django.contrib import admin

from .models import (FavouriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientAdmin(admin.StackedInline):
    """Stacked in line ingredients for RecipeAdmin."""
    model: RecipeIngredient = RecipeIngredient
    autocomplete_fields: tuple = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin interface for Recipies."""
    list_display: tuple = (
        "name",
        "author",
        "get_favorite_count",
    )
    search_fields: tuple = (
        "name",
        "author__username",
        "tags",
    )
    list_filter: tuple = (
        "name",
        "author__username",
        "tags",
    )
    inlines: tuple = (RecipeIngredientAdmin,)
    empty_value_display: str = "-пусто-"

    @admin.display(description="В избранном")
    def get_favorite_count(self, obj) -> int:
        """Get favorite recipes count."""
        return obj.favourite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for tags."""
    list_display: tuple = ("name", "color", "slug")
    search_fields: tuple = ("name",)
    list_filter: tuple = ("name",)
    empty_value_display: str = "пусто"


@admin.register(FavouriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Admin interface for favourite recipes."""
    list_display: tuple = ("id", "user", "recipe")
    search_fields: tuple = ("user__username", "recipe__name")
    list_filter: tuple = ("user__username", "recipe__name")
    empty_value_display: str = "-пусто-"


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    """Admin interface for ingredients."""
    list_display: tuple = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields: tuple = ("name", "measurement_unit",)
    list_filter: tuple = ("name", "measurement_unit",)
    empty_value_display: str = "пусто"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin interface for shopping cart."""
    list_display: tuple = ("user", "recipe",)
    search_fields: tuple = ("user__username", "recipe__name",)
    list_filter: tuple = ("user__username", "recipe__name",)
    empty_value_display: str = "-пусто-"
