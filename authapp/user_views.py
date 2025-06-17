from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from .user_serializers import UserListSerializer, UserUpdateSerializer
from .permissions import RolePermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [RolePermission]

    def get_allowed_roles(self):
        if self.action in ['list', 'destroy']:
            return ['admin']
        if self.action in ['update', 'partial_update']:
            # Only admin or self can update
            return ['admin', 'user']
        return ['admin', 'user']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    def get_permissions(self):
        self.allowed_roles = self.get_allowed_roles()
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        if getattr(request.user.profile, 'role', None) != 'admin':
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if getattr(request.user.profile, 'role', None) != 'admin':
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'success'}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_role = getattr(request.user.profile, 'role', None)
        if user_role != 'admin' and request.user.pk != int(kwargs['pk']):
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_role = getattr(request.user.profile, 'role', None)
        if user_role != 'admin' and request.user.pk != int(kwargs['pk']):
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
