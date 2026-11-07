from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CenterPersonForm, DonorPickupForm
from .helpers import deal_parts, get_center, get_donor
from .models import NeedPledge, OfferClaim


def load_deal(kind, pk):
    if kind == 'pledge':
        return get_object_or_404(
            NeedPledge.objects.select_related('post__center', 'donor__user'), pk=pk)
    if kind == 'claim':
        return get_object_or_404(
            OfferClaim.objects.select_related('offer__donor__user', 'center'), pk=pk)
    raise Http404


def role_of(request, parts):
    donor, center = get_donor(request), get_center(request)
    if donor is not None and donor.pk == parts['donor'].pk:
        return 'donor'
    if center is not None and center.pk == parts['center'].pk:
        return 'center'
    if request.user.is_staff:
        return 'admin'
    return None


@login_required
def deal_detail(request, kind, pk):
    obj = load_deal(kind, pk)
    parts = deal_parts(kind, obj)
    role = role_of(request, parts)
    if role is None:
        messages.error(request, 'You do not have access to this page.')
        return redirect('home')

    pending = obj.bucket == 'pending'
    donor_form = center_form = None

    if request.method == 'POST' and pending:
        which = request.POST.get('form_type')
        if which == 'donor' and role == 'donor':
            donor_form = DonorPickupForm(request.POST)
            if donor_form.is_valid():
                for field, value in donor_form.cleaned_data.items():
                    setattr(obj, field, value)
                obj.save()
                messages.success(request, 'Hand-over details saved. The care centre can see them now.')
                return redirect('deal_detail', kind=kind, pk=pk)
            messages.error(request, 'Please correct the errors below.')
        elif which == 'center' and role == 'center':
            center_form = CenterPersonForm(request.POST)
            if center_form.is_valid():
                for field, value in center_form.cleaned_data.items():
                    setattr(obj, field, value)
                obj.save()
                messages.success(request, 'Person details saved. The donor can see them now.')
                return redirect('deal_detail', kind=kind, pk=pk)
            messages.error(request, 'Please correct the errors below.')

    if role == 'donor' and pending and donor_form is None:
        donor_form = DonorPickupForm(initial={
            'method': obj.method, 'pickup_address': obj.pickup_address,
            'pickup_date': obj.pickup_date, 'pickup_time': obj.pickup_time})
    if role == 'center' and pending and center_form is None:
        center_form = CenterPersonForm(initial={
            'person_name': obj.person_name, 'person_phone': obj.person_phone})

    can_complete = role == 'center' and (
        (kind == 'pledge' and obj.status == 'taken') or (kind == 'claim' and obj.status == 'accepted'))

    return render(request, 'market/deal_detail.html', {
        'obj': obj, 'kind': kind, 'parts': parts, 'role': role, 'pending': pending,
        'contact_open': kind == 'pledge' or obj.status in ('accepted', 'completed'),
        'donor_form': donor_form, 'center_form': center_form,
        'can_complete': can_complete,
        'can_cancel': pending and role in ('donor', 'center'),
    })


@login_required
@require_POST
def deal_complete(request, kind, pk):
    obj = load_deal(kind, pk)
    parts = deal_parts(kind, obj)
    back = redirect('deal_detail', kind=kind, pk=pk)
    if role_of(request, parts) != 'center':
        messages.error(request, 'Only the care centre can mark a donation as received.')
        return back
    ok = (kind == 'pledge' and obj.status == 'taken') or (kind == 'claim' and obj.status == 'accepted')
    if not ok:
        messages.info(request, 'This donation cannot be marked as received right now.')
        return back
    obj.status = 'completed'
    obj.completed_at = timezone.now()
    obj.save(update_fields=['status', 'completed_at'])
    if kind == 'claim':
        obj.offer.status = 'completed'
        obj.offer.save(update_fields=['status'])
    messages.success(request, 'Marked as received. The donor can now download a certificate.')
    return back


@login_required
@require_POST
def deal_cancel(request, kind, pk):
    obj = load_deal(kind, pk)
    parts = deal_parts(kind, obj)
    back = redirect('deal_detail', kind=kind, pk=pk)
    if role_of(request, parts) not in ('donor', 'center'):
        messages.error(request, 'You cannot cancel this donation.')
        return back
    if obj.bucket != 'pending':
        messages.info(request, 'This donation is already finished.')
        return back
    was_accepted = kind == 'claim' and obj.status == 'accepted'
    obj.status = 'cancelled'
    obj.save(update_fields=['status'])
    if was_accepted:
        obj.offer.status = 'open'          # the item is available for centres again
        obj.offer.save(update_fields=['status'])
    messages.warning(request, 'The donation was cancelled.')
    return back