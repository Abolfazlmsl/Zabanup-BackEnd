from rest_framework.permissions import BasePermission
from core.models import Ticket


class IsManager(BasePermission):
    message = 'شما اجازه دسترسی ندارید'

    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Manager'):
            return True
        return False


class IsTicketMessageOwner(BasePermission):
    message = 'شما اجازه دسترسی ندارید'

    def has_permission(self, request, view):
        if request.POST:
            current_ticket_id = request.POST.get('ticket')
            ticket = Ticket.objects.get(id=current_ticket_id)
            return request.user == ticket.staff
        return True
