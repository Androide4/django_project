from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('subscription__provider__name', 'user__username', 'name', 'comment')
