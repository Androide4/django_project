from django.contrib import admin
from .models import (
    Provider, Currency, Plan, PaymentMethod, Subscription,
    Payment, Notification, Comment, AuditLog
)

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'website', 'created_at')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'symbol', 'decimals', 'last_updated')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'duration_days', 'price', 'currency', 'created_at')
    search_fields = ('name',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'is_default', 'created_at')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'plan', 'status', 'start_date', 'end_date', 'currency')
    list_filter = ('status', 'currency', 'provider')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'paid_at', 'created_at')
    search_fields = ('reference',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'send_at', 'sent_at', 'read')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'user', 'created_at')
    ordering = ('-created_at',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_pk', 'user', 'timestamp')
    ordering = ('-timestamp',)
