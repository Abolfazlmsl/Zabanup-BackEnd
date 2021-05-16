import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.http import HttpResponse
from django.utils.translation import gettext as _

from core import models

# Register your models here.


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class UserAdmin(UserAdminBase):
    ordering = ['id']
    list_display = ['phone_number', 'name']
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (
            _('Personal Info'),
            {
                'fields': (
                    'name',
                    'email',
                    'generated_token',
                    'is_verified',
                    'picture',
                    'gender',
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
            }
        ),
        (
            _('Important dates'),
            {
                'fields': ('last_login',)
            }
        )
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Book)
admin.site.register(models.Category)
admin.site.register(models.Answer)
admin.site.register(models.Question)
admin.site.register(models.UserAnswer)
admin.site.register(models.Comment)
admin.site.register(models.Ticket)
admin.site.register(models.TicketMessage)
admin.site.register(models.Chat)
admin.site.register(models.ChatMessage)


@admin.register(models.QuestionDescription)
class QuestionAdmin(admin.ModelAdmin, ExportCsvMixin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["queryset"] = models.Category.objects.filter(type='question')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Reading)
class ReadingAdmin(admin.ModelAdmin, ExportCsvMixin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "passage_type":
            kwargs["queryset"] = models.Category.objects.filter(type='type')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin, ExportCsvMixin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "difficulty":
            kwargs["queryset"] = models.Category.objects.filter(type='difficulty')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)