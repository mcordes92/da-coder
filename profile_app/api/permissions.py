from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow only the profile owner to edit it.

    Read access is allowed for everyone.
    """

    message = "Only the profile owner can edit it."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id