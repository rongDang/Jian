from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from django.core.mail import send_mail
from .forms import ArticleForm
from .models import *
from django.db.models import Q
import markdown, random,os,json, datetime
# from django.contrib.auth.decorators import login_required  # 如果要使用login_required的话得使用django的用户系统
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date


# 自定义序列化时间格式
class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


# 自定义装饰器用来判断用户是否登录，因为这里用没有用Django的user表所以无法通过login_required来验证
def my_login_required(func):
    def check_login_stauts(request):
        if request.session.get("nick_name"):
            return func(request)
        else:
            return HttpResponseRedirect("/book/login")
    return check_login_stauts


# 写文章页面，form表单渲染
@my_login_required
def write(request):
    # 获取文章id，如果没有则是写文章页面，如果有则是编辑文章
    article_id = request.GET.get("id")
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    anthology = Anthology.objects.filter(author=user)
    try:
        article = Article.objects.get(id=int(article_id))
        # 如果是编辑，则给form表单添加默认值为要编辑的文章
        form = ArticleForm(initial={"content": article.content, "title": article.title})
    except:
        form = ArticleForm()
    return render(request, 'book/writing.html', locals())


# 搜索文章页面
def search_article(request):
    key = request.GET.get("key")
    # 名称中包含 "字段"，且字段不区分大小写name__icontains="字段"
    search_data = Article.objects.filter(Q(title__icontains=key) | Q(content__icontains=key) & Q(publish=True))
    return render(request, 'book/search.html', locals())


# 创建文集
def create_anthology(request):
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    anthology = request.POST.get('name')
    if Anthology.objects.filter(Q(name=anthology) & Q(author=user)):
        # 查找该用户是否有同名文集
        return HttpResponse('0')
    else:
        Anthology.objects.create(author=user, name=anthology)
        id = Anthology.objects.filter(Q(name=anthology) & Q(author=user))[0].id
        return HttpResponse(str(id))


# 删除文集
def delete_anthology(request):
    name = "12"
    if name == request.session.get("nick_name"):
        return HttpResponseRedirect(reverse("book:index"))
    id = request.POST.get('anthology_id')
    Anthology.objects.get(id=id).delete()
    return HttpResponse('ok')


# 修改文集
def update_anthology(request):
    name = request.session.get("nick_name")
    # 获取id，更新的文集名，判断该用户是否存在有同名的文集，有的化则不更改
    user = Users.objects.get(nick_name=name)
    id = request.POST.get('anthology_id')
    name = request.POST.get('name')
    if Anthology.objects.filter(Q(name=name) & Q(author=user)):
        # 查找该用户是否有同名文集
        return HttpResponse('0')
    else:
        anthology = Anthology.objects.get(id=id)
        anthology.objects.update(name=name)
        return HttpResponse(name)


# 提交文章, 保存文章
def submit(request):
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    article_id = request.POST.get("article_id")
    title = request.POST.get("title")
    content = request.POST.get("content")
    anthology_id = request.POST.get("anthology_id")
    publish = request.POST.get("publish")
    if publish == "true":
        publish = True
    else:
        publish = False
    # 如果文章id存在则是修改文章，否时是创建文章
    if article_id != "None":
        article = Article.objects.get(id=int(article_id))
        article.title = title
        article.content = content
        article.anthology_id = int(anthology_id)
        article.author = user
        article.publish = publish
        article.save()
        print("修改")
    else:
        print("创建")
        article = Article.objects.create(title=title, content=content, anthology_id=int(anthology_id), author=user, publish=publish)
    return HttpResponse(str(article.id))


# 展示文章，
def show(request, id):
    # 获取登录的用户信息，
    name = request.session.get("nick_name")
    data = Article.objects.get(id=id)
    data.click_number += 1
    data.save()
    # 查找该文章下的评论内容
    comments = Comments.objects.filter(article=data).order_by("-create_time")
    # 判断当前登录用户是否有收藏这篇文章
    try:
        user = Users.objects.get(nick_name=name)
        # user.user_from是找登录用户的关注用户信息中有文章作者的
        attention_flag = user.user_from.filter(ByFollowers=data.author)
        collect_flag = user.collect_set.get(author=user)
    except:
        collect_flag = None
    content = markdown.markdown(data.content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    return render(request, 'book/Article.html', locals())


# 评论数据的提交
def comment_submit(request):
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    # replay是被回复的评论,article是评论的文章id，content是评论内容  评论者是登录的用户
    reply = request.POST.get("parent_id")
    article = request.POST.get("article")
    content = request.POST.get("content")
    print(reply, article, content)
    # 到评论表中创建数据，被回复的评论可以为空
    Comments.objects.create(content=content, article_id=int(article), author=user, parent_comment_id=reply)
    return HttpResponse("1")


# 收藏文章
def collect_article(request):
    name = request.session.get("nick_name")
    article_id = request.POST["article_id"]
    user = Users.objects.get(nick_name=name)
    Collect.objects.create(author=user, article_id=int(article_id))
    return HttpResponse('ok')


def delete_collect(request):
    name = request.session.get("nick_name")
    article_id = request.POST["article_id"]
    user = Users.objects.get(nick_name=name)
    Collect.objects.get(author=user, article_id=int(article_id)).delete()
    return HttpResponse('ok')


def add_attention(request):
    author_id = request.POST["author"]
    print(author_id)
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    Attention.objects.create(follower=user, ByFollowers_id=int(author_id))
    return HttpResponse('ok')


def del_attention(request):
    author_id = request.POST["author"]
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    Attention.objects.get(follower=user, ByFollowers_id=int(author_id)).delete()
    return HttpResponse('ok')


# 测试关注
def test(request):
    # 假设小白是登录用户
    user = Users.objects.get(nick_name='小白')
    # 查询关注小白的用户
    fans = user.user_to.all()
    # 查询小白关注的用户
    by_followers = user.user_from.all()
    # 查询判断
    fans_list = []
    for i in fans:
        di = {}
        di["fans"] = i
        for j in by_followers:
            if i.follower == j.ByFollowers:
                print("关注了")
                di["flag"] = True
        fans_list.append(di)
    return render(request, 'book/test.html', locals())


# 注册页面, --------------------------------------------------------------------------------旭
def zhuce01(request):
    if request.method == "POST":
        # 从浏览器获取数据
        uesr1 = request.POST.get('yhm')  # 用户名
        yx1 = request.POST.get('yx')  # 邮箱
        pw1 = request.POST.get('mm')  # 密码
        wyzm = request.POST.get('yzm')  # 验证码
        # 从浏览器获取缓存数据
        try:
            yzm = request.session['message']
        except:
            return HttpResponse("请发送邮箱验证码")
        # 判断用户名是否重复
        if Users.objects.filter(nick_name=uesr1):
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("用户名重复，注册失败！")

        # 判断邮箱是否重复
        elif Users.objects.filter(email=yx1):
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("邮箱重复，注册失败！")

        # 判断验证码是否和邮箱验证码一样
        elif wyzm != yzm:
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("验证码错误或者过期")
        else:
            # 判断验证码是否一样
            if wyzm == yzm:
                del request.session['message']  # 删除浏览器缓存
                request.session['message'] = ''  # 设置浏览器缓存message 为空
                # 储存到数据库中
                user = Users(nick_name=uesr1, email=yx1, password=pw1)
                user.save()
                Anthology.objects.create(author=user, name="日记本")
                return HttpResponse("ok")
            else:
                return HttpResponse("注册失败！")
    return render(request, 'book/zhuce.html')


# 登入页面
def dengru01(request):
    if request.method == "POST":
        # 从浏览器获取数据
        duesr1 = request.POST.get('dyhm')  # 用户名
        dpw1 = request.POST.get('dmm')  # 密码
        # 异常捕捉
        try:
            # 判断用户名或者邮箱和密码是否和数据库匹配
            user = Users.objects.get(Q(Q(nick_name=duesr1) | Q(email=duesr1)) & Q(password=dpw1))
            request.session["nick_name"] = user.nick_name
            print(request.session.get("nick_name"))
            return HttpResponse('ok')
        except:
            return HttpResponse("用户名或者密码错误！")
    return render(request, 'book/dengru.html')


# 密码重置页面
def mimachongzhi01(request):
    if request.method == "POST":
        # 从浏览器中获取数据
        uesr1 = request.POST.get('zyhm')  # 用户名
        pw1 = request.POST.get('zxmm1')  # 密码1
        pw2 = request.POST.get('zxmm2')  # 密码2
        zyx = request.POST.get('zyx')  # 验证码
        # 从浏览器获取缓存数据
        try:
            uesr2 = Users.objects.get(email=uesr1)
        except:
            return HttpResponse("输入邮箱未注册")
        try:
            zyx1 = request.session['message']
        except:
            return HttpResponse("请发送邮箱验证码")

        # 判断密码，验证码是否一致
        if (pw1 == pw2) & (zyx == zyx1):
            # 判断邮箱是否一致
            try:
                uesr2 = Users.objects.get(email=uesr1)
                # 更改密码
                uesr2.password = pw1
                # 放到数据库中
                uesr2.save()
                del request.session['message']  # 删除浏览器缓存
                request.session['message'] = ''  # 设置浏览器缓存message 为空
                return HttpResponse("重置成功！")
            except:
                return HttpResponse("输入邮箱未注册")
        # 判断密码和验证码是否一致
        elif (pw1 == pw2) & (zyx != zyx1):
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("验证码错误或者过期！")
        # 判断密码和验证码是否一致
        elif (pw1 != pw2) & (zyx == zyx1):
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("密码不一致！")
        else:
            del request.session['message']  # 删除浏览器缓存
            request.session['message'] = ''  # 设置浏览器缓存message 为空
            return HttpResponse("密码不一致或者验证码错误！")
    return render(request, 'book/chongzhimima.html')


def dianjiyianzhengma(request):
    # 随机数
    number = str(random.randint(100000, 999999))
    yx1 = request.POST.get('yx')  # 邮箱
    print(yx1)
    # 将message放到浏览器中
    request.session['message'] = number
    # 邮箱验证码
    send_mail("重置密码", "重置密码的验证码："+number, "1542776628@qq.com", [yx1], fail_silently=True)
    return HttpResponse(number)


# 退出登录,删除所有session数据
def logout(request):
    request.session.delete()
    return HttpResponseRedirect('/book/index')


# 展示首页,显示所有已经发布了的文章-----------------------------------------------------------辉
def index(request):
    articles = Article.objects.filter(publish=True)
    paginator = Paginator(articles, 2)
    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)
    try:
        print(page)
        book_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        book_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        book_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
    return render(request, 'book/index.html', {"articles": paginator, "Articlea": book_list})


# 收藏页面， 获取用户名然后查询对应用户收藏的文章
def Bookmark(request):
    nick_name = request.GET.get("username")
    print(nick_name)
    user = Users.objects.get(nick_name=nick_name)
    article = Collect.objects.filter(author=user)
    return render(request, 'book/collect.html', {"articles": article})


def allowed_file(filename):
    IMG = ["png", "jpg", "gif", "jpeg"]  # 允许的拓展名
    # 判断文件格式,使用rsplit()从右向左寻找,参数1是只分割一次，lower()将字符串大写转换为小写
    # print(filename.rsplit(".", 1))
    return "." in filename and filename.rsplit(".", 1)[1].lower() in IMG


# post上传头像
def user(request):
    name = request.session.get("nick_name")
    Usersa = Users.objects.get(nick_name=name)
    if request.method == 'POST':
        from Jian.settings import MEDIA_ROOT
        name = request.session.get("nick_name")
        boy = Users.objects.get(nick_name=name)
        img = request.FILES.get('img')
        if allowed_file(str(img)):
            try:
                os.remove(MEDIA_ROOT + "/" + str(boy.head))
            except:
                pass
            boy.head = img
            boy.save()
            src = Users.objects.get(nick_name=name).head
            return HttpResponse(str(src))
        else:
            return HttpResponse('error')
    return render(request, 'book/user.html', {'Usersa': Usersa})


# 修改个人资料昵称，个人简介
def xiugai(request):
    name = request.session.get("nick_name")
    nick_name = request.POST.get('nick_name')
    introduce = request.POST.get('introduce')
    Usersa = Users.objects.get(nick_name=name)
    try:
        Users.objects.get(nick_name=nick_name)
        return HttpResponse('no')
    except:
        Usersa.nick_name = nick_name
        Usersa.introduce = introduce
        Usersa.save()
        return HttpResponse('ok')


# 显示评论，关注----------------------------------------------------------------------------------川
def information(request):
    # 假设登录用户为小白，查找评论表中评论的文章作者为小白的评论集合
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    ret = Comments.objects.filter(article__author=user)
    content = {'author': ret}
    return render(request, "book/news_comment.html", content)


def attention(request):
    name = request.session.get("nick_name")
    user = Users.objects.get(nick_name=name)
    # 查询关注登录用户的用户
    fans = user.user_to.all()
    # 查询登录用户关注的用户
    by_followers = user.user_from.all()
    # 查询判断
    fans_list = []
    for i in fans:
        di = {}
        di["fans"] = i
        for j in by_followers:
            if i.follower == j.ByFollowers:
                print("关注了")
                di["flag"] = True
        fans_list.append(di)
    content = {'fans_list': fans_list}
    return render(request, 'book/news_attention.html', content)


# 个人主页，文集，他人主页-------------------------------------------------------------------------苗
def search(obj):
    FAtten = Attention.objects.filter(follower=obj)
    ByAtten = Attention.objects.filter(ByFollowers=obj)
    antho = Anthology.objects.filter(author=obj)
    article = Article.objects.filter(author=obj)[:1]

    return FAtten, ByAtten, antho, article


# 我的主页
@my_login_required
def center(request):
    if request.method == 'POST':
        name = request.session.get("nick_name")
        page = int(request.POST.get("page"))
        obj = Users.objects.get(nick_name=name)
        data = []
        article = Article.objects.filter(author=obj)[page:page + 1]
        if article:
            for a in article:
                Dict = {}
                Dict["id"] = a.id
                Dict["title"] = a.title
                Dict["content"] = a.content
                Dict["number"] = a.click_number
                Dict["comment_number"] = a.comments_set.count()
                Dict["collect_number"] = a.collect_set.count()
                Dict["date"] = a.create_time
                data.append(Dict)
                # print(str)
                return HttpResponse(json.dumps(data, cls=CJsonEncoder))
        else:
            return HttpResponse('error')
    name = request.session.get("nick_name")
    obj = Users.objects.get(nick_name=name)
    article1 = Article.objects.filter(author_id=obj).order_by('-click_number')
    FAtten, ByAtten, antho, article = search(obj)
    return render(request, 'book/Mycenter.html', locals())


# 编辑个人介绍
def introduce(request):
    name = request.session.get("nick_name")
    text = request.POST.get('texts')
    obj = Users.objects.get(nick_name=name)
    obj.introduce = text
    obj.save()
    return HttpResponse('ok')


# 文集(查询还有问题)
def corpus(request):
    user = request.GET.get('user')
    names = request.GET.get('name')
    obj3 = Users.objects.get(nick_name=user)
    FAtten, ByAtten, antho, article = search(obj3)
    # print(obj3.anthology_set.get(name='倾城').article_set.all().order_by('-create_time'))
    times = obj3.anthology_set.get(name=names).article_set.all().order_by('-create_time')
    return render(request, 'book/corpus.html', locals())


# 粉丝
def fans(request):
    name = request.session.get("nick_name")
    obj2 = Users.objects.get(nick_name=name)
    fans = obj2.user_to.all()
    # 查询登录关注的用户
    by_followers = obj2.user_from.all()
    # 查询判断
    fans_list = []
    for i in fans:
        di = {}
        di["fans"] = i
        for j in by_followers:
            if i.follower == j.ByFollowers:
                print("关注了")
                di["flag"] = True
        fans_list.append(di)
    FAtten, ByAtten, antho, article = search(obj2)
    return render(request, 'book/fans.html', locals())


# 他的主页
def Hiscenter(request):
    # 获取用户名，判断是当前用户还是其他用户
    name = request.session.get("nick_name")
    username = request.GET.get('username')
    if username == name:
        return HttpResponseRedirect('/book/center/')
    his = Users.objects.get(nick_name=username)
    pub = his.article_set.filter(publish=True).order_by('-create_time')
    try:
        # myname为当前登录用户，hisAtten为查找登录用户关注的用户有没有当前用户的
        myname = Users.objects.get(nick_name=name)
        hisAtten = myname.user_from.filter(ByFollowers=his)
    except:
        hisAtten = None
    return render(request, 'book/Hiscenter.html', locals())
