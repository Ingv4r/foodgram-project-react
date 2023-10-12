from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()
MINIMUM_VALUE: int = 1


class Recipe(models.Model):
    """Recipe model."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор рецепта",
        null=False,
    )
    name = models.CharField(
        verbose_name="Название", max_length=200, db_index=True, null=False
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="foodgram_backend/images",
        null=False,
    )
    text = models.TextField(
        verbose_name="Описание", null=False, max_length=1000
    )
    ingredients: int = models.ManyToManyField(
        to="Ingredient",
        through="RecipeIngredient",
        verbose_name="Ингридиенты",
        related_name="recipe",
    )
    tags: int = models.ManyToManyField(
        to="Tag",
        verbose_name="Теги",
        related_name="recipe",
    )
    cooking_time: int = models.PositiveIntegerField(
        verbose_name="Время приготовления в минутах.",
        null=False,
        validators=(MinValueValidator(MINIMUM_VALUE),),
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    class Meta:
        verbose_name: str = "Рецепт"
        verbose_name_plural: str = "Рецепты"
        ordering: tuple = ("-pub_date",)

    def __str__(self) -> str:
        """Return a string representation of recipe name."""
        return self.name


class Tag(models.Model):
    """Tag model."""
    name: str = models.CharField(
        verbose_name="Название", max_length=150, unique=True
    )
    color: str = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        help_text=(
            "Цветовой код должен быть в 16-ричном формате. Например: #49B64E"
        ),
        validators=(
            RegexValidator(
                regex=r"^#[a-fA-F0-9]{6}$",
                message="Цвет должен быть в 16-ричном формате.",
                code="wrong_hex_code",
            ),
        ),
    )
    slug: str = models.SlugField(
        verbose_name="URL метка", help_text="Введите slug тега", unique=True
    )

    class Meta:
        verbose_name: str = "Tег"
        verbose_name_plural: str = "Tеги"
        ordering: tuple = ("-pk",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "slug"), name="unique_name_slug"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of name."""
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""
    name: str = models.CharField(
        verbose_name="Название", max_length=100, null=False, db_index=True
    )
    measurement_unit: str = models.CharField(
        verbose_name="Еденица измерения", max_length=40, null=False
    )

    class Meta:
        verbose_name: str = "ингридиент"
        verbose_name_plural: str = "ингридиенты"
        ordering = ("-pk",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_name_unit"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of name and measurement."""
        return f"{self.name}, {self.measurement_unit}"


class RecipeIngredient(models.Model):
    """Custom intermediate related with Recipe and Ingredient model."""
    recipe: int = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredient",
    )
    ingredient: int = models.ForeignKey(
        Ingredient,
        verbose_name="Ингридиент",
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    amount: int = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(MinValueValidator(MINIMUM_VALUE),),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient_pair",
            )
        ]


class FavouriteRecipe(models.Model):
    """Favourite recipe model."""
    user: int = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favourite",
    )
    recipe: int = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name="favourite",
    )
    date_added: models.DateTimeField = models.DateTimeField(
        verbose_name="дата создания", auto_now_add=True
    )

    class Meta:
        verbose_name: str = "Избранное"
        verbose_name_plural: str = "Избранное"
        ordering: tuple = ("-date_added",)
        constraints: list = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favourite"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of this object."""
        return (
            f"{self.user.username} добавил "
            f"{self.recipe.name} в избранное."
        )


class ShoppingCart(models.Model):
    """Shopping Cart model."""
    user: int = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe: int = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name: str = "Список покупок"
        verbose_name_plural: str = "Список покупок"
        constraints: list = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]

    def __str__(self) -> str:
        """Return a string representation of this object."""
        return (
            f"{self.user.username} добавил "
            f"{self.recipe.name} в список покупок."
        )
