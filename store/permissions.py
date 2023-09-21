from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user.is_authenticated)
        else:
            return bool(request.user.is_authenticated and request.user.is_staff)
