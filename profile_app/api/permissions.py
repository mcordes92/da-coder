from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProfileOwnerOrReadOnly(BasePermission):
    """
    Erlaubt nur dem Besitzer des Profils, es zu bearbeiten.
    Lesezugriff ist für alle erlaubt.
    """

    message = "Nur der Besitzer des Profils kann es bearbeiten."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id