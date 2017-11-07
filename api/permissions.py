from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow edit object only to its owner
    """

    def has_object_permission(self, request, view, obj):
        # if request.user is permissions.IsAdminUser:
        #     return True
        return request.user == obj.owner