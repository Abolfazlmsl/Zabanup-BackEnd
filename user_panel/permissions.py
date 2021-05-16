from rest_framework.permissions import BasePermission

from core.models import Ticket


class IsTicketMessageOwner(BasePermission):
    message = 'شما اجازه دسترسی ندارید'

    def has_permission(self, request, view):
        if request.POST:
            current_ticket_id = request.POST.get('ticket')
            ticket = Ticket.objects.get(id=current_ticket_id)
            return request.user == ticket.student
        return True
