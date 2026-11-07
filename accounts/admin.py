from django.contrib import admin, messages

from .models import CenterProfile, Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state')
    list_filter = ('state',)
    search_fields = ('user__username', 'user__first_name', 'user__email', 'phone', 'city')


@admin.register(CenterProfile)
class CenterProfileAdmin(admin.ModelAdmin):
    list_display = ('center', 'contact_person', 'phone', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('center__name', 'contact_person', 'user__username', 'phone')
    actions = ['approve', 'unapprove']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.center.is_active = obj.is_approved
        obj.center.save(update_fields=['is_active'])

    @admin.action(description='Approve selected care centers')
    def approve(self, request, queryset):
        count = 0
        for profile in queryset.select_related('center'):
            profile.is_approved = True
            profile.save(update_fields=['is_approved'])
            profile.center.is_active = True
            profile.center.save(update_fields=['is_active'])
            count += 1
        self.message_user(request, f'{count} care center(s) approved.', messages.SUCCESS)

    @admin.action(description='Remove approval from selected care centers')
    def unapprove(self, request, queryset):
        count = 0
        for profile in queryset.select_related('center'):
            profile.is_approved = False
            profile.save(update_fields=['is_approved'])
            profile.center.is_active = False
            profile.center.save(update_fields=['is_active'])
            count += 1
        self.message_user(request, f'{count} care center(s) set to pending.', messages.WARNING)