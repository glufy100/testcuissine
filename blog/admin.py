from django.contrib import admin
from .models import Post, PostImage
from .access import is_admin
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return is_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_admin(request.user)

    def has_add_permission(self, request):
        return is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin(request.user)

    inlines = [PostImageInline]
    list_display = ['title', 'category', 'published', 'created_at']
    list_filter = ['published', 'category']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
