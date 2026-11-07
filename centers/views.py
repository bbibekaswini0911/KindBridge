from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import center_required
from accounts.models import Donor
from market.helpers import with_taken
from market.models import NeedPledge, NeedPost, Offer, OfferClaim

from .models import CareCenter, Requirement


def _filter_centers(request):
    centers = (CareCenter.objects.filter(is_active=True)
               .prefetch_related('requirements').order_by('-created_at'))
    values = {
        'type': request.GET.get('type', ''),
        'need': request.GET.get('need', ''),
        'state': request.GET.get('state', '').strip(),
        'district': request.GET.get('district', '').strip(),
    }
    if values['type']:
        centers = centers.filter(center_type=values['type'])
    if values['need']:
        centers = centers.filter(need_posts__category=values['need'],
                                 need_posts__is_closed=False).distinct()
    if values['state']:
        centers = centers.filter(state__icontains=values['state'])
    if values['district']:
        centers = centers.filter(Q(district__icontains=values['district'])
                                 | Q(name__icontains=values['district']))
    return centers, values


def _page_context(request, centers, values):
    page = Paginator(centers, 9).get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)
    return {
        'page': page,
        'types': CareCenter.CenterType.choices,
        'categories': Requirement.Category.choices,
        'values': values,
        'qs': query.urlencode(),
        'filtered': any(values.values()),
    }


def home_view(request):
    centers = (CareCenter.objects.filter(is_active=True)
               .prefetch_related('requirements').order_by('-created_at')[:6])
    needs = (with_taken(NeedPost.objects.filter(is_closed=False, center__is_active=True))
             .filter(taken_qty__lt=F('quantity'))
             .select_related('center').prefetch_related('photos')[:6])
    return render(request, 'home.html', {
        'centers': centers,
        'needs': needs,
        'types': CareCenter.CenterType.choices,
        'categories': Requirement.Category.choices,
        'stats': {
            'centers': CareCenter.objects.filter(is_active=True).count(),
            'donors': Donor.objects.count(),
            'needs': NeedPost.objects.count(),
            'completed': NeedPledge.objects.filter(status='completed').count()
                         + OfferClaim.objects.filter(status='completed').count(),
        },
    })


def search_view(request):
    """Landing page search. Logged-in users are sent to the sidebar version."""
    if request.user.is_authenticated:
        url = reverse('explore')
        if request.GET:
            url += '?' + request.GET.urlencode()
        return redirect(url)
    centers, values = _filter_centers(request)
    return render(request, 'centers/search.html', _page_context(request, centers, values))


@login_required
def explore_view(request):
    centers, values = _filter_centers(request)
    return render(request, 'centers/explore.html', _page_context(request, centers, values))


def center_detail(request, pk):
    center = get_object_or_404(CareCenter, pk=pk, is_active=True)
    needs = (with_taken(NeedPost.objects.filter(center=center, is_closed=False))
             .prefetch_related('photos'))
    return render(request, 'centers/detail.html', {
        'center': center,
        'needs': needs,
        'base_layout': 'layouts/app.html' if request.user.is_authenticated
                       else 'layouts/public.html',
    })


@login_required
@center_required
def center_dashboard(request):
    center = request.user.center_profile.center
    pledges = NeedPledge.objects.filter(post__center=center)
    claims = OfferClaim.objects.filter(center=center)
    stats = {
        'open_needs': center.need_posts.filter(is_closed=False).count(),
        'pending': pledges.filter(status='taken').count()
                   + claims.filter(status__in=['waiting', 'accepted']).count(),
        'completed': pledges.filter(status='completed').count()
                     + claims.filter(status='completed').count(),
        'donor_items': Offer.objects.filter(status='open').count(),
    }
    return render(request, 'centers/dashboard.html', {
        'center': center,
        'stats': stats,
        'recent': pledges.select_related('post', 'donor__user')[:5],
        'items': (Offer.objects.filter(status='open')
                  .select_related('donor__user').prefetch_related('photos')[:4]),
    })
