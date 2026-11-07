from django.contrib import admin

# Register your models here.

from .models import CareCenter, Requirement


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1


@admin.register(CareCenter)
class CareCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'center_type', 'state', 'district', 'is_active')
    list_filter = ('center_type', 'state', 'is_active')
    search_fields = ('name', 'district', 'state')
    inlines = [RequirementInline]


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'center', 'category', 'quantity_needed', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('item_name', 'center__name')