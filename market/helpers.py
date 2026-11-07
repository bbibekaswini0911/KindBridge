from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .models import NeedPledge, OfferClaim


def get_donor(request):
    return getattr(request.user, 'donor', None)


def get_center(request):
    """The approved care centre of the logged-in user, or None."""
    profile = getattr(request.user, 'center_profile', None)
    if profile is not None and profile.is_approved:
        return profile.center
    return None


def with_taken(qs):
    """Add taken_qty (units already reserved) to a NeedPost queryset in one query."""
    return qs.annotate(taken_qty=Coalesce(
        Sum('pledges__quantity', filter=Q(pledges__status__in=['taken', 'completed'])), 0))


def page_query(request):
    """Current filters as a query string without the page number (for pager links)."""
    query = request.GET.copy()
    query.pop('page', None)
    return query.urlencode()


def deal_parts(kind, obj):
    """Same facts for both kinds of deals: 'pledge' (needs market) and 'claim' (donor items)."""
    if kind == 'pledge':
        post = obj.post
        return {
            'donor': obj.donor, 'center': post.center, 'title': post.title,
            'quantity': obj.quantity, 'unit': post.unit,
            'category': post.get_category_display(), 'description': post.description,
            'photos': post.photos.all(), 'type': 'Centre need',
        }
    offer = obj.offer
    return {
        'donor': offer.donor, 'center': obj.center, 'title': offer.title,
        'quantity': offer.quantity, 'unit': '',
        'category': offer.get_category_display(), 'description': offer.description,
        'photos': offer.photos.all(), 'type': 'Donor item',
    }


def deal_rows(request):
    """All deals the logged-in user may see, newest first. None if the user has no role."""
    donor, center = get_donor(request), get_center(request)
    if center is not None:
        pledges = NeedPledge.objects.filter(post__center=center)
        claims = OfferClaim.objects.filter(center=center)
    elif donor is not None:
        pledges = NeedPledge.objects.filter(donor=donor)
        claims = OfferClaim.objects.filter(offer__donor=donor)
    elif request.user.is_staff:
        pledges = NeedPledge.objects.all()
        claims = OfferClaim.objects.all()
    else:
        return None

    rows = []
    sources = (
        ('pledge', pledges.select_related('post__center', 'donor__user')),
        ('claim', claims.select_related('offer__donor__user', 'center')),
    )
    for kind, qs in sources:
        for obj in qs:
            p = deal_parts(kind, obj)
            d = p['donor']
            donor_name = d.user.get_full_name() or d.user.username
            rows.append({
                'kind': kind, 'pk': obj.pk, 'obj': obj,
                'title': p['title'], 'qty': p['quantity'], 'unit': p['unit'],
                'category': p['category'], 'type': p['type'],
                'donor': d, 'donor_name': donor_name, 'center': p['center'],
                'status': obj.status, 'status_label': obj.get_status_display(),
                'bucket': obj.bucket, 'created': obj.created_at, 'completed': obj.completed_at,
                'search': f"{p['title']} {donor_name} {p['center'].name} {p['category']}".lower(),
            })
    rows.sort(key=lambda r: r['created'], reverse=True)
    return rows
