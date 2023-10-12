from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    """Permissions for a recipe endpoints."""
    def has_permission(self, request, view) -> bool:
        """Return True if permission is granted."""
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if permission for object is granted."""
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
        )


class AdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Permissions for an admin or read only."""
    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if permission for object is granted."""
        return bool(
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )


class CurrentUserOnly(permissions.IsAuthenticated):
    """Permissions for current user only."""
    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if permission for object is granted."""
        return bool(request.user and request.user.id == obj.pk)
