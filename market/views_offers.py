from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import center_required, donor_required

from .forms import ClaimForm, OfferForm
from .helpers import get_center, get_donor, page_query
from .models import CATEGORIES, Offer, OfferClaim, OfferPhoto


# ---------- donor side ----------

@login_required
@donor_required
def publish_offer(request):
    donor = get_donor(request)
    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.donor = donor
            offer.save()
            for f in form.cleaned_data['photos']:
                OfferPhoto.objects.create(offer=offer, image=f)
            messages.success(request, 'Your item is published. Care centres can see it now.')
            return redirect('my_offers')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = OfferForm()
    return render(request, 'market/publish_offer.html', {'form': form})


@login_required
@donor_required
def my_offers(request):
    donor = get_donor(request)
    offers = (Offer.objects.filter(donor=donor)
              .annotate(waiting=Count('claims', filter=Q(claims__status='waiting')))
              .prefetch_related('photos'))
    q = request.GET.get('q', '').strip()
    if q:
        offers = offers.filter(Q(title__icontains=q) | Q(description__icontains=q))
    page = Paginator(offers, 10).get_page(request.GET.get('page'))
    return render(request, 'market/my_offers.html', {'page': page, 'q': q, 'qs': page_query(request)})


@login_required
@donor_required
@require_POST
def offer_close(request, pk):
    offer = get_object_or_404(Offer, pk=pk, donor=get_donor(request))
    if offer.status != 'open':
        messages.info(request, 'Only an open item can be closed.')
        return redirect('offer_detail', pk=pk)
    offer.status = 'closed'
    offer.save(update_fields=['status'])
    offer.claims.filter(status='waiting').update(status='declined')
    messages.warning(request, 'The item is closed. Waiting centres were told it is not available.')
    return redirect('my_offers')


# ---------- care centre side ----------

@login_required
@center_required
def offer_board(request):
    center = get_center(request)
    offers = (Offer.objects.filter(status='open')
              .select_related('donor__user').prefetch_related('photos'))
    values = {
        'q': request.GET.get('q', '').strip(),
        'category': request.GET.get('category', ''),
        'city': request.GET.get('city', '').strip(),
    }
    if values['q']:
        offers = offers.filter(Q(title__icontains=values['q']) | Q(description__icontains=values['q']))
    if values['category']:
        offers = offers.filter(category=values['category'])
    if values['city']:
        offers = offers.filter(city__icontains=values['city'])
    mine = set(OfferClaim.objects.filter(center=center).values_list('offer_id', flat=True))
    page = Paginator(offers, 9).get_page(request.GET.get('page'))
    return render(request, 'market/offer_board.html', {
        'page': page, 'values': values, 'categories': CATEGORIES, 'mine': mine,
        'qs': page_query(request), 'filtered': any(values.values()),
    })


@login_required
def offer_detail(request, pk):
    offer = get_object_or_404(
        Offer.objects.select_related('donor__user').prefetch_related('photos'), pk=pk)
    donor, center = get_donor(request), get_center(request)
    owner = donor is not None and donor.pk == offer.donor_id
    if not (owner or center is not None or request.user.is_staff):
        messages.error(request, 'You do not have access to this page.')
        return redirect('home')

    context = {'offer': offer, 'owner': owner}

    if owner or request.user.is_staff:
        claims = list(offer.claims.select_related('center').order_by('created_at'))
        waiting = [c for c in claims if c.status == 'waiting']
        context.update({'claims': claims, 'first_waiting': waiting[0] if waiting else None})

    if center is not None and not owner:
        my_claim = offer.claims.filter(center=center).first()
        if offer.status != 'open' and my_claim is None:
            messages.info(request, 'This item is no longer available.')
            return redirect('offer_board')
        context['my_claim'] = my_claim
        if my_claim is not None and my_claim.status == 'waiting':
            context['position'] = offer.claims.filter(
                status='waiting', created_at__lt=my_claim.created_at).count() + 1
    return render(request, 'market/offer_detail.html', context)


@login_required
@center_required
@require_POST
def claim_offer(request, pk):
    center = get_center(request)
    offer = get_object_or_404(Offer, pk=pk, status='open')
    form = ClaimForm(request.POST)
    message = form.cleaned_data['message'] if form.is_valid() else ''
    claim, created = OfferClaim.objects.get_or_create(
        offer=offer, center=center, defaults={'message': message})
    if created:
        position = offer.claims.filter(status='waiting', created_at__lt=claim.created_at).count() + 1
        messages.success(request, f'Request sent. You are number {position} in line.')
    else:
        messages.info(request, 'You have already asked for this item.')
    return redirect('offer_detail', pk=pk)


# ---------- donor decides ----------

def _front_of_line(offer):
    return offer.claims.filter(status='waiting').order_by('created_at').first()


@login_required
@donor_required
@require_POST
@transaction.atomic
def claim_accept(request, pk):
    donor = get_donor(request)
    claim = get_object_or_404(OfferClaim.objects.select_related('center'), pk=pk, offer__donor=donor)
    offer = Offer.objects.select_for_update().get(pk=claim.offer_id)
    front = _front_of_line(offer)
    if offer.status != 'open' or front is None or front.pk != claim.pk:
        messages.error(request, 'Only the care centre at the front of the line can be accepted.')
        return redirect('offer_detail', pk=offer.pk)

    claim.status = 'accepted'
    claim.save(update_fields=['status'])
    offer.claims.filter(status='waiting').exclude(pk=claim.pk).update(status='declined')
    offer.status = 'reserved'
    offer.save(update_fields=['status'])
    messages.success(request, f'You accepted {claim.center.name}. Now fill in the hand-over details.')
    return redirect('deal_detail', kind='claim', pk=claim.pk)


@login_required
@donor_required
@require_POST
@transaction.atomic
def claim_decline(request, pk):
    donor = get_donor(request)
    claim = get_object_or_404(OfferClaim.objects.select_related('center'), pk=pk, offer__donor=donor)
    offer = Offer.objects.select_for_update().get(pk=claim.offer_id)
    front = _front_of_line(offer)
    if offer.status != 'open' or front is None or front.pk != claim.pk:
        messages.error(request, 'Only the care centre at the front of the line can be declined.')
        return redirect('offer_detail', pk=offer.pk)

    claim.status = 'declined'
    claim.save(update_fields=['status'])
    nxt = _front_of_line(offer)
    if nxt is not None:
        messages.warning(request, f'{claim.center.name} was declined. {nxt.center.name} is now at the front.')
    else:
        messages.warning(request, f'{claim.center.name} was declined. No other centre is waiting.')
    return redirect('offer_detail', pk=offer.pk)

