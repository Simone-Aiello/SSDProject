from rest_framework import permissions


class IsBeachManagerOrPOSTOnly(permissions.BasePermission):

    def has_permission(self, request, views):
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name='beach-managers').exists()
        return True
