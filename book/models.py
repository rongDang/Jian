from django.db import models
from mdeditor.fields import MDTextField
import uuid


def image_upload_to(instance, filename):
    return 'img/{}'.format(uuid.uuid4().hex+filename)


class Users(models.Model):
    """
        用户表: 昵称，邮箱，密码，个人简介，头像地址
    """
    nick_name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    introduce = models.CharField(max_length=255, blank=True, null=True)
    head = models.ImageField(upload_to=image_upload_to, default='http://img3.duitang.com/uploads/item/201505/22/20150522205616_KeX3C.jpeg')

    def __str__(self):
        return self.nick_name


class Article(models.Model):
    """
        文章表: 标题，内容，创建时间，点击量，所属文集，作者，是否发布（默认不发布）
    """
    title = models.CharField(max_length=100)
    content = MDTextField()
    create_time = models.DateTimeField(auto_now_add=True)
    click_number = models.IntegerField(default=0)
    anthology = models.ForeignKey('Anthology', on_delete=models.CASCADE)
    author = models.ForeignKey('Users', on_delete=models.CASCADE)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Anthology(models.Model):
    """
        文集表: 文集所属作者，文集名，文集下文章数
    """
    author = models.ForeignKey('Users', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    number = models.IntegerField(default=0)

    def __str__(self):
        return '%s 的 %s' % (self.author.nick_name, self.name)


class Collect(models.Model):
    """
        文章收藏表: 文章收藏者(作者), 被收藏的文章
    """
    author = models.ForeignKey('Users', on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)

    def __str__(self):
        return '%s 收藏了文章 %s' % (self.author.nick_name, self.article.title)


class Attention(models.Model):
    """
        关注表: 关注者，被关注者
    """
    follower = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='user_from')
    ByFollowers = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='user_to')
    Attention_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s 关注了 %s' % (self.follower.nick_name, self.ByFollowers.nick_name)


class Comments(models.Model):
    """
        评论表: 评论对象(文章), 父级评论(当前评论表),评论者，评论内容，评论时间
    """
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comments', on_delete=models.CASCADE, blank=True, null=True)
    author = models.ForeignKey('Users', on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s 评论了 %s' % (self.author.nick_name, self.article.title)


