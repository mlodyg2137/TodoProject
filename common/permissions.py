from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", None) or obj
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and (
                project.owner_id == request.user.id or request.user in project.members.all()
            )
        return False


class IsProjectMemberRead_OwnerWrite(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        u = request.user
        if not u.is_authenticated:
            return False
        is_owner = project.owner_id == u.id
        is_member = project.members.filter(pk=u.pk).exists()
        if request.method in SAFE_METHODS:
            return is_owner or is_member
        return is_owner
