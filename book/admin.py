from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'nick_name', 'email', 'password')
    list_display_links = ('id', 'nick_name', )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'create_time', 'click_number', 'anthology', 'author', 'publish')
    list_display_links = ('id', 'title')


@admin.register(Anthology)
class AnthologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'number')
    list_display_links = ('id', 'author')


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'article')
    list_display_links = ('id', 'author')


@admin.register(Attention)
class AttentionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'ByFollowers')
    list_display_links = ('id', 'follower')


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'parent_comment_id', 'author', 'content', 'create_time')
    list_display_links = ('id', 'article')

