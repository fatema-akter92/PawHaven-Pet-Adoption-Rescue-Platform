from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access for anyone (or authenticated users),
    but restricts write access (POST, PUT, DELETE) to staff/admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to the owner of the adoption request or staff members.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user
