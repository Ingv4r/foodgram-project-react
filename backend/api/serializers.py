import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (FavouriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Field representing a base64 encoded image."""
    def to_internal_value(self, data):
        """Transform the base64 string into a native value."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = "__all__"


class Ingredients_RecipeSerializer(serializers.ModelSerializer):
    """Serializer for ingredients and recipes relation."""
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    id = serializers.ReadOnlyField(source="ingredient.id")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class CustomUserSerializer(UserSerializer):
    """Serializer for users."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Return True if the user is subscribed to author."""
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Serializer for create users."""
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )

    def validate_email(self, data):
        """Check user email validation."""
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует.",
            )
        return data

    def validate_first_name(self, data):
        """Check user first name validation."""
        if len(data) > 150:
            raise serializers.ValidationError("Слишком длинное имя.")
        return data

    def validate_last_name(self, data):
        """Check user last name validation."""
        if len(data) > 150:
            raise serializers.ValidationError("Слишком длинная фамилия.")
        return data


class SubscriptionSerializer(CustomUserSerializer):
    """Serializer for subscriptions."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model: User = User
        fields: tuple = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    @staticmethod
    def get_resipe_serializer():
        """Return short serializer for recipes."""
        return ShortRecipeSerializer

    def get_recipes(self, obj):
        """Return author's recipes if subcscribe."""
        author_recipes = Recipe.objects.filter(author=obj)

        if "recipes_limit" in self.context.get("request").GET:
            recipes_limit = self.context.get("request").GET["recipes_limit"]
            author_recipes = author_recipes[: int(recipes_limit)]

        if author_recipes:
            serializer = self.get_resipe_serializer()(
                author_recipes,
                context={"request": self.context.get("request")},
                many=True,
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        """Return count of author's recipes."""
        return Recipe.objects.filter(author=obj).count()


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients field in RecipeWriteSerializer."""
    id: int = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        fields: tuple = ("id", "amount")
        model = RecipeIngredient


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for create recipes."""
    ingredients = RecipeCreateIngredientSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(required=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    @staticmethod
    def is_auth_and_exists(obj, user, model) -> bool:
        """Check if user is authorized or exists in model."""
        if user.is_anonymous:
            return False
        return model.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj) -> bool:
        """Check for recipe in favorites."""
        user = self.context["request"].user
        return self.is_auth_and_exists(obj, user, FavouriteRecipe)

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Chek for recipe in user's shopping cart."""
        user = self.context["request"].user
        return self.is_auth_and_exists(obj, user, ShoppingCart)

    def validate_ingredients(self, values):
        """Ingredients validation."""
        if not values:
            raise serializers.ValidationError(
                "Нужно указать хотя бы один элемент.",
            )
        ingredients_list: list = []
        for value in values:
            ingredient = get_object_or_404(
                Ingredient, id=value["ingredient"].id
            )
            if int(value["amount"]) <= 0:
                raise serializers.ValidationError(
                    {"Количество должно быть больше 0."}
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    "Значения должны быть уникальны."
                )
            ingredients_list.append(ingredient)
        return values

    def validate_tags(self, values):
        """Tags validation."""
        if not values:
            raise serializers.ValidationError(
                "Нужно выбрать хотя бы один тег."
            )
        tags_list: list = []
        for tag in values:
            if tag in tags_list:
                raise serializers.ValidationError(
                    "Теги должны быть уникальными."
                )
            tags_list.append(tag)
        return values

    @transaction.atomic
    def create(self, validated_data):
        """Create a new recipe model instance."""
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        obj = Recipe.objects.create(**validated_data)
        obj.save()
        obj.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=obj,
                ingredient=ingredient["ingredient"],
                amount=ingredient["amount"],
            )
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a recipe model instance if ingredients field in data."""
        ingredients = validated_data.pop("ingredients", None)
        tags = validated_data.pop("tags", None)
        if ingredients is None or tags is None:
            raise serializers.ValidationError(
                "Поля ингредиентов и тегов должны быть заполнены."
            )
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient["ingredient"],
                amount=ingredient["amount"],
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Return recipe representation."""
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for safe HTTP methods and to representation."""
    image = Base64ImageField()
    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(
        read_only=True,
    )
    ingredients = Ingredients_RecipeSerializer(
        many=True, source="recipe_ingredient"
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model: Recipe = Recipe
        exclude: tuple = ("pub_date",)

    @staticmethod
    def is_auth_and_exists(obj, user, model) -> bool:
        """Check if user is authorized or exists in model."""
        if user.is_anonymous:
            return False
        return model.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj):
        """Check if recipe in favourite."""
        user = self.context["request"].user
        return self.is_auth_and_exists(obj, user, FavouriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        """Check if recipe in shopping cart."""
        user = self.context["request"].user
        return self.is_auth_and_exists(obj, user, ShoppingCart)


class IngredientSerialiser(serializers.ModelSerializer):
    """Serializer for ingredients."""
    class Meta:
        model: Ingredient = Ingredient
        fields: str = "__all__"


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Serializer for short recipe representation."""
    class Meta:
        model: Recipe = Recipe
        fields: tuple = ("id", "name", "image", "cooking_time")
