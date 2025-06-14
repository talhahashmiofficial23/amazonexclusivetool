from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    allowed_roles = []
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        user_role = getattr(request.user.profile, 'role', None)
        allowed = getattr(view, 'allowed_roles', self.allowed_roles)
        return user_role in allowed if allowed else True
