from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import donor_required

from .forms import PledgeForm
from .helpers import get_center, get_donor, page_query, with_taken
from .models import CATEGORIES, NeedPledge, NeedPost


def open_needs():
    """Needs that are open and still have units left (one database query)."""
    qs = NeedPost.objects.filter(is_closed=False, center__is_active=True)
    return (with_taken(qs).filter(taken_qty__lt=F('quantity'))
            .select_related('center').prefetch_related('photos'))


@login_required
def need_board(request):
    posts = open_needs()
    values = {
        'q': request.GET.get('q', '').strip(),
        'category': request.GET.get('category', ''),
        'state': request.GET.get('state', '').strip(),
    }
    if values['q']:
        posts = posts.filter(Q(title__icontains=values['q'])
                             | Q(description__icontains=values['q'])
                             | Q(center__name__icontains=values['q']))
    if values['category']:
        posts = posts.filter(category=values['category'])
    if values['state']:
        posts = posts.filter(Q(center__state__icontains=values['state'])
                             | Q(center__district__icontains=values['state']))
    page = Paginator(posts, 9).get_page(request.GET.get('page'))
    return render(request, 'market/need_board.html', {
        'page': page, 'values': values, 'categories': CATEGORIES,
        'qs': page_query(request), 'filtered': any(values.values()),
    })


def need_detail(request, pk):
    qs = with_taken(NeedPost.objects.filter(center__is_active=True)
                    .select_related('center').prefetch_related('photos'))
    post = get_object_or_404(qs, pk=pk)
    donor, center = get_donor(request), get_center(request)

    context = {
        'post': post,
        'base_layout': 'layouts/app.html' if request.user.is_authenticated else 'layouts/public.html',
    }
    if donor is not None:
        context['my_pledge'] = post.pledges.filter(donor=donor, status='taken').first()
    if center is not None and center.pk == post.center_id:
        context['pledges'] = post.pledges.exclude(status='cancelled').select_related('donor__user')
    return render(request, 'market/need_detail.html', context)


@login_required
@donor_required
@require_POST
@transaction.atomic
def take_need(request, pk):
    donor = get_donor(request)
    # lock this row so two donors pressing "Take" together are handled one after the other
    post = get_object_or_404(NeedPost.objects.select_for_update(),
                             pk=pk, is_closed=False, center__is_active=True)
    back = redirect('need_detail', pk=pk)

    form = PledgeForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please enter a valid quantity.')
        return back
    if post.pledges.filter(donor=donor, status='taken').exists():
        messages.info(request, 'You have already taken this request. Open it from your records.')
        return back

    quantity = form.cleaned_data['quantity']
    remaining = post.remaining
    if remaining <= 0:
        messages.warning(request, 'Sorry, another donor has already taken the full quantity.')
        return back
    if quantity > remaining:
        messages.error(request, f'Only {remaining} is still needed. Please lower the quantity.')
        return back

    pledge = NeedPledge.objects.create(
        post=post, donor=donor, quantity=quantity, message=form.cleaned_data['message'])
    messages.success(request, 'You took this request. Contact the care centre and agree on the hand-over.')
    return redirect('deal_detail', kind='pledge', pk=pledge.pk)

