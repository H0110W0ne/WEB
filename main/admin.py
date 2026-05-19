from django.contrib import admin

from .models import Comment, Direction, Registration


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'user',
        'email',
        'phone',
        'age',
        'direction',
        'telegram_sent',
        'created_at',
    )
    list_filter = ('direction', 'telegram_sent', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'user__username')
    autocomplete_fields = ('direction',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_name', 'user', 'short_text', 'created_at')
    search_fields = ('author_name', 'text', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('created_at',)
    autocomplete_fields = ('user',)

    @staticmethod
    def short_text(obj):
        return obj.text[:60]
