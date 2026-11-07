from django.contrib import admin

# Register your models here.


from .models import (ContactMessage, NeedPhoto, NeedPledge, NeedPost,
                        Offer, OfferClaim, OfferPhoto)


class NeedPhotoInline(admin.TabularInline):
    model = NeedPhoto
    extra = 0


class OfferPhotoInline(admin.TabularInline):
    model = OfferPhoto
    extra = 0


@admin.register(NeedPost)
class NeedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'center', 'category', 'quantity', 'is_closed', 'created_at')
    list_filter = ('category', 'is_closed', 'center__state')
    search_fields = ('title', 'center__name', 'description')
    inlines = [NeedPhotoInline]


@admin.register(NeedPledge)
class NeedPledgeAdmin(admin.ModelAdmin):
    list_display = ('post', 'donor', 'quantity', 'status', 'created_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('post__title', 'post__center__name', 'donor__user__username')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'donor', 'category', 'quantity', 'city', 'status', 'created_at')
    list_filter = ('category', 'status')
    search_fields = ('title', 'donor__user__username', 'city')
    inlines = [OfferPhotoInline]


@admin.register(OfferClaim)
class OfferClaimAdmin(admin.ModelAdmin):
    list_display = ('offer', 'center', 'status', 'created_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('offer__title', 'center__name')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'message')

