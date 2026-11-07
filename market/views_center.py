from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import center_required

from .forms import CenterProfileForm, NeedPostForm
from .helpers import get_center, page_query, with_taken
from .models import NeedPhoto, NeedPost


@login_required
@center_required
def post_need(request):
    center = get_center(request)
    if request.method == 'POST':
        form = NeedPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.center = center
            post.save()
            for f in form.cleaned_data['photos']:
                NeedPhoto.objects.create(post=post, image=f)
            messages.success(request, 'Your request is live. Every donor can see it now.')
            return redirect('my_needs')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = NeedPostForm()
    return render(request, 'market/post_need.html', {'form': form})


@login_required
@center_required
def my_needs(request):
    center = get_center(request)
    posts = with_taken(NeedPost.objects.filter(center=center)).prefetch_related('photos')
    q = request.GET.get('q', '').strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(description__icontains=q))
    page = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, 'market/my_needs.html', {'page': page, 'q': q, 'qs': page_query(request)})


@login_required
@center_required
@require_POST
def close_need(request, pk):
    post = get_object_or_404(NeedPost, pk=pk, center=get_center(request))
    post.is_closed = not post.is_closed
    post.save(update_fields=['is_closed'])
    if post.is_closed:
        messages.warning(request, 'This request is closed. Donors can no longer take it.')
    else:
        messages.success(request, 'This request is open again.')
    return redirect('my_needs')


@login_required
@center_required
def center_profile(request):
    center = get_center(request)
    if request.method == 'POST':
        form = CenterProfileForm(request.POST, request.FILES, instance=center)
        if form.is_valid():
            form.save()
            messages.success(request, 'Centre profile updated.')
            return redirect('center_profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CenterProfileForm(instance=center)
    return render(request, 'centers/profile.html', {'form': form, 'center': center})
