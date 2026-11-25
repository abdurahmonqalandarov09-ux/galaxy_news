from django.contrib import admin
from .models import News, GmailConfirm


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    list_display_links = ['id', 'title']
    search_fields = ['title', 'text']
    list_filter = ['author', 'created_at']


@admin.register(GmailConfirm)
class GmailConfirmAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code')