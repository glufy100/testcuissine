from django.contrib import messages
from .access import admin_required, is_admin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import PostForm
from .models import Post, PostImage

def home(request):
    posts = Post.objects.filter(published=True)
    total = posts.count()
    category = request.GET.get('categorie', '')
    query = request.GET.get('q', '').strip()[:150]
    featured = posts.first()
    if category in dict(Post.CATEGORIES):
        posts = posts.filter(category=category)
    else:
        category = ''
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query))
    page = Paginator(posts, 6).get_page(request.GET.get('page'))
    return render(request, 'blog/home.html', {'posts': page, 'featured': featured, 'categories': Post.CATEGORIES, 'category': category, 'query': query, 'total': total})

def detail(request, slug):
    posts = Post.objects.all() if is_admin(request.user) else Post.objects.filter(published=True)
    post = get_object_or_404(posts, slug=slug)
    return render(request, 'blog/detail.html', {'post': post, 'related': Post.objects.filter(published=True).exclude(pk=post.pk)[:3]})

@admin_required
def dashboard(request):
    posts = Post.objects.all()
    status = request.GET.get('statut', '')
    counts = {'total': posts.count(), 'published': posts.filter(published=True).count(), 'drafts': posts.filter(published=False).count()}
    if status in ('publies', 'brouillons'):
        posts = posts.filter(published=status == 'publies')
    return render(request, 'blog/dashboard.html', {'posts': posts, 'counts': counts, 'status': status})

@admin_required
def edit(request, pk=None):
    post = get_object_or_404(Post, pk=pk) if pk else None
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            saved = form.save()
            for image in form.cleaned_data['gallery_images']:
                PostImage.objects.create(post=saved, image=image)
            remove = [int(value) for value in request.POST.getlist('remove_photos') if value.isdigit()]
            saved.gallery.filter(pk__in=remove).delete()
        messages.success(request, 'Article publié !' if saved.published else 'Brouillon enregistré.')
        return redirect('dashboard')
    return render(request, 'blog/editor.html', {'form': form, 'post': post})

@require_POST
@admin_required
def delete(request, pk):
    get_object_or_404(Post, pk=pk).delete()
    messages.success(request, 'Article supprimé.')
    return redirect('dashboard')
