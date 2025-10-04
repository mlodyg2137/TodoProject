from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", None) or obj
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and (project.owner_id == request.user.id or request.user in project.members.all())
        return request.user.is_authenticated and (project.owner_id == request.user.id or request.user in project.members.all())
    
        # TODO: Rozbudować tą metode o dodatkowe rozpatrywanie i zwracanie odpowiednich uprawnień 