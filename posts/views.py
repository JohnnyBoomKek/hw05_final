from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page



def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


def search(request):
    keyword = request.GET.get('q')
    if keyword:
        posts = Post.objects.filter(text__contains=keyword)
    else:
        posts = None

    return render(request, "search.html", {"posts": posts, "keyword": keyword})


@login_required 
def new(request): 
    if request.method != 'POST': 
        form = PostForm() 
    else: 
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid(): 
            new_post = form.save(commit=False) 
            new_post.author = request.user 
            new_post = form.save() 
            return redirect('index') 
    context = {'form': form} 
    return render(request, 'new.html', context) 


def profile(request, username):
    user = get_object_or_404(User, username=username)
    author = User.objects.get(username=username)
    posts_cnt = user.author_posts.count()
    posts = user.author_posts.order_by("-pub_date").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user != author:
        NotMyPageFlag = True
    else:
        NotMyPageFlag = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author).exists():
            following = True
    context = {"user": user, "posts_cnt": posts_cnt, "page": page, "paginator": paginator, 'author': author, 'following': following, 'NotMyPageFlag': NotMyPageFlag}
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    posts_cnt = user.author_posts.count()
    comments = Comment.objects.filter(post = post_id).order_by("-created")
    comment_cnt = Comment.objects.filter(post = post_id).count()
    form = CommentForm()

    context = {'user': user, "post": post, 'posts_cnt': posts_cnt, 'author': post.author, 'comments': comments, 'form': form, 'comment_cnt': comment_cnt}
    return render(request, "post_page.html", context)

def post_edit(request, username, post_id): 
    user = get_object_or_404(User, username=username) 
    post = Post.objects.get(id=post_id) 
    if post.author != request.user: 
        raise Http404 
    if request.method != 'POST': 
        form = PostForm(instance=post) 
    else: 
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid(): 
            form.save() 
            return redirect('post', username, post.id) 
    context = {'post': post, 'form': form} 
    return render(request, "edit_post.html", context) 


def page_not_found(request, exception):
        # Переменная exception содержит отладочную информацию, 
        # выводить её в шаблон пользователской страницы 404 мы не станем
        return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
        return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username, post_id)
        return render(request, 'comments.html', {'form':form})

    return render(request, 'comments.html', {'form': form, 'post': post})

@login_required
def delete_comment(request, comment_id):
    comment_to_delete = Comment.objects.get(id=comment_id)
    post = comment_to_delete.post
    username = comment_to_delete.post.author
    if comment_to_delete.author == request.user:

        comment_to_delete.delete()
        return redirect('post', username, post.id)
    else:
        raise Http404 

@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    post_list = Post.objects.filter(author__in=follow.values_list('author'))
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user).filter(author=profile)
    if request.user != profile:
        if not following:
            Follow.objects.create(user=request.user, author=profile)
            return redirect ("profile", username)
    return redirect ("profile", username)
    

@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if author == request.user:
        raise Http404
    unfollow = Follow.objects.get(user=request.user, author=author)
    unfollow.delete()
    return redirect('profile', username)

        
