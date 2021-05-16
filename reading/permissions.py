from rest_framework.permissions import BasePermission
from core.models import Comment


class IsComment(BasePermission):
    message = 'امکان ریپلای کردن ریپلای وجود ندارد!'

    def has_permission(self, request, view):
        if request.POST:
            parent_id = request.POST.get('parent')
            print('salam' + parent_id)
            if parent_id:
                comment = Comment.objects.get(id=parent_id)
                return comment.parent is None
        return True
