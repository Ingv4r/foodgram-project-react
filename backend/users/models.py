from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    """Model for User subscriptions."""
    user: int = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author: int = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="following",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints: list = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="user_not_author",
            ),
            models.UniqueConstraint(
                fields=["user", "author"], name="user_author_unique"
            ),
        ]
        ordering: tuple = ("-pk",)
        verbose_name: str = "Подписка"
        verbose_name_plural: str = "Подписки"

    def __str__(self) -> str:
        """Return a string representation of users."""
        return f"{self.user.username} подписан на {self.author.username}"
