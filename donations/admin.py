from django.contrib import admin

# Register your models here.
from django.utils import timezone

from .models import DonationRequest


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('donor', 'center', 'requirement', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'center')
    list_editable = ('status',)
    search_fields = ('donor__user__username', 'center__name', 'requirement__item_name')
    date_hierarchy = 'created_at'
    actions = ['mark_approved', 'mark_rejected']

    @admin.action(description='Mark selected requests as Approved')
    def mark_approved(self, request, queryset):
        count = queryset.update(status=DonationRequest.Status.APPROVED, updated_at=timezone.now())
        self.message_user(request, f'{count} request(s) approved.')

    @admin.action(description='Mark selected requests as Rejected')
    def mark_rejected(self, request, queryset):
        count = queryset.update(status=DonationRequest.Status.REJECTED, updated_at=timezone.now())
        self.message_user(request, f'{count} request(s) rejected.')