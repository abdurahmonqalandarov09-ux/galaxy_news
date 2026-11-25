from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from .models import News, GmailConfirm


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name='Editors').exists()


def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Такое имя пользователя уже занято')
            return render(request, 'registration.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Эта почта уже зарегистрирована')
            return render(request, 'registration.html')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )
        code = str(randint(100000, 999999))
        GmailConfirm.objects.update_or_create(user=user, defaults={'code': code})
        send_mail(
            'Код подтверждения: Сводка',
            f'Здравствуйте, {username}!\n\n'
            f'Ваш код подтверждения: {code}\n\n'
            'Введите его на странице подтверждения, чтобы завершить регистрацию.\n'
            'Если вы не регистрировались на сайте, просто проигнорируйте это письмо.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        messages.success(request, 'Мы отправили код на вашу почту')
        return render(request, 'confirm_email.html', {'username': username})
    return render(request, 'registration.html')


def confirm_email(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        code = request.POST.get('code')
        user = User.objects.filter(username=username).first()
        code_obj = GmailConfirm.objects.filter(user=user).first()
        if user is not None and code_obj is not None and code_obj.code == code:
            user.is_active = True
            user.save()
            group, created = Group.objects.get_or_create(name='Readers')
            user.groups.add(group)
            code_obj.delete()
            login(request, user)
            messages.success(request, 'Почта подтверждена. Добро пожаловать!')
            return redirect('profile')
        messages.error(request, 'Неверный код, попробуйте ещё раз')
        return render(request, 'confirm_email.html', {'username': username})
    return render(request, 'confirm_email.html')


def login_user(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            return redirect('news_list')
        messages.error(request, 'Неверный логин или пароль, либо почта не подтверждена')
    return render(request, 'login_user.html')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'profile.html', {'is_editor': is_editor(request.user)})


def news_list(request):
    query = request.GET.get('q')
    news = News.objects.all().order_by('-created_at')
    if query:
        news = news.filter(Q(title__icontains=query) | Q(text__icontains=query))
    return render(request, 'news_list.html', {
        'news': news,
        'query': query,
        'is_editor': is_editor(request.user),
    })


def news_detail(request, id):
    news = get_object_or_404(News, id=id)
    return render(request, 'news_detail.html', {
        'news': news,
        'is_editor': is_editor(request.user),
    })


@login_required
def news_create(request):
    if not is_editor(request.user):
        messages.error(request, 'Добавлять новости могут только редакторы')
        return redirect('news_list')
    if request.method == 'POST':
        news = News.objects.create(
            title=request.POST.get('title'),
            text=request.POST.get('text'),
            image=request.FILES.get('image'),
            author=request.user
        )
        messages.success(request, 'Новость опубликована')
        return redirect('news_detail', id=news.id)
    return render(request, 'news_form.html', {'news': None})


@login_required
def news_update(request, id):
    if not is_editor(request.user):
        messages.error(request, 'Править новости могут только редакторы')
        return redirect('news_list')
    news = get_object_or_404(News, id=id)
    if request.method == 'POST':
        news.title = request.POST.get('title')
        news.text = request.POST.get('text')
        if request.FILES.get('image'):
            news.image = request.FILES.get('image')
        news.save()
        messages.success(request, 'Изменения сохранены')
        return redirect('news_detail', id=news.id)
    return render(request, 'news_form.html', {'news': news})


@login_required
def news_delete(request, id):
    if not is_editor(request.user):
        messages.error(request, 'Удалять новости могут только редакторы')
        return redirect('news_list')
    news = get_object_or_404(News, id=id)
    if request.method == 'POST':
        news.delete()
        messages.success(request, 'Новость удалена')
        return redirect('news_list')
    return render(request, 'news_delete.html', {'news': news})