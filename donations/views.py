# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from centers.models import CareCenter

from .forms import DonationRequestForm
from .models import DonationRequest
from django.db.models import Sum


@login_required
def donate_view(request, center_id):
    center = get_object_or_404(CareCenter, pk=center_id, is_active=True)
    donor = getattr(request.user, 'donor', None)
    if donor is None:
        messages.error(request, 'Only registered donors can send requests. Please register a donor account.')
        return redirect('center_detail', pk=center.pk)

    if request.method == 'POST':
        form = DonationRequestForm(request.POST, center=center)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = donor
            donation.center = center
            donation.save()
            messages.success(request, 'Request submitted. Status: Pending.')
            return redirect('donation_confirmation', pk=donation.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        initial = {}
        item = request.GET.get('item')
        if item:
            initial['requirement'] = item
        form = DonationRequestForm(center=center, initial=initial)

    return render(request, 'donations/donate.html', {'form': form, 'center': center})


@login_required
def confirmation_view(request, pk):
    donation = get_object_or_404(DonationRequest, pk=pk, donor__user=request.user)
    return render(request, 'donations/confirmation.html', {'donation': donation})

@login_required
def track_view(request):
    donor = getattr(request.user, 'donor', None)
    if donor is None:
        messages.info(request, 'Tracking is for donor accounts.')
        return redirect('home')

    status = request.GET.get('status', '')
    items = donor.requests.select_related('center', 'requirement')
    if status in DonationRequest.Status.values:
        items = items.filter(status=status)
    else:
        status = ''
    return render(request, 'donations/track.html', {
        'items': items,
        'current': status,
        'statuses': DonationRequest.Status.choices,
    })


@login_required
def history_view(request):
    donor = getattr(request.user, 'donor', None)
    if donor is None:
        messages.info(request, 'History is for donor accounts.')
        return redirect('home')

    approved = (donor.requests.filter(status=DonationRequest.Status.APPROVED)
                .select_related('center', 'requirement').order_by('-updated_at'))
    total_units = approved.aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'donations/history.html', {
        'items': approved,
        'total_units': total_units,
    })