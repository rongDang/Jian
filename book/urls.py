# -*- encoding:utf8 -*-
from django.urls import path
from book import views
app_name = "book"

urlpatterns = [
    path('write/', views.write, name='write'),
    path('create_anthology/', views.create_anthology, name='create_anthology'),
    path('delete_anthology/', views.delete_anthology, name='delete_anthology'),
    path('update_anthology/', views.update_anthology, name='update_anthology'),
    path('submit/', views.submit, name='submit_article'),
    path('comment_submit/', views.comment_submit, name='comment_submit'),
    path('show/<id>', views.show, name='show_article'),
    path('collect_article/', views.collect_article, name='collect_article'),
    path('delete_collect/', views.delete_collect, name='delete_collect'),
    path('add_attention/', views.add_attention, name='add_attention'),
    path('del_attention/', views.del_attention, name='del_attention'),
    path('search_article/', views.search_article, name='search_article'),
    path('test/', views.test, name='tet'),
    # 登录注册部分
    path('login/', views.dengru01, name='login'),
    path('zhuce01/', views.zhuce01, name='sign'),
    path('mimachongzhi01/', views.mimachongzhi01, name='re_pwd'),
    path('dianjiyianzhengma/', views.dianjiyianzhengma),
    path('logout/', views.logout, name='logout'),
    # 首页，个人资料， 收藏页面
    path('index/', views.index, name='index'),
    path("Bookmark/", views.Bookmark, name='show_collect'),
    path("User/", views.user, name='upload_img'),
    path("xiugai/", views.xiugai),
    # 导航条消息显示/评论/关注
    path('information/', views.information, name='information'),
    path('attention/', views.attention, name='attention'),
    # 个人主页，文集页面，他人主页
    path('center/', views.center, name='center'),
    path('corpus/', views.corpus, name='corpus'),
    path('fans/', views.fans, name='fans'),
    path('introduce/', views.introduce, name='introduce'),
    path('Hiscenter/', views.Hiscenter, name='hiscenter'),
]
