from django.contrib import admin
from .models import Post, PostImage
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ['title', 'category', 'published', 'created_at']
    list_filter = ['published', 'category']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
