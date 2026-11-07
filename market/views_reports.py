from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import staff_required

import csv

from .forms import ContactForm
from .helpers import deal_parts, deal_rows, get_donor
from .models import ContactMessage
from .views_deals import load_deal

HEADERS = [
    'Date', 'Type', 'Item', 'Category', 'Quantity', 'Unit', 'Status', 'Completed on',
    'Donor name', 'Donor phone', 'Donor email', 'Donor city', 'Donor state',
    'Care centre', 'Centre type', 'Centre phone', 'Centre district', 'Centre state',
    'Hand-over method', 'Pickup address', 'Pickup date', 'Pickup time',
    'Person from centre', 'Person phone', 'Message',
]


@login_required
def export_csv(request):
    rows = deal_rows(request)
    if rows is None:
        messages.info(request, 'Reports are for donor, care centre and admin accounts.')
        return redirect('home')

    year = request.GET.get('year', '')
    month = request.GET.get('month', '')
    if year.isdigit():
        rows = [r for r in rows if timezone.localtime(r['created']).year == int(year)]
    if month.isdigit():
        rows = [r for r in rows if timezone.localtime(r['created']).month == int(month)]

    label = f"{year or 'all-years'}{'-' + month.zfill(2) if month.isdigit() else ''}"
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="kindbridge-records-{label}.csv"'
    response.write('\ufeff')            # lets Excel read Odia / Hindi text correctly
    writer = csv.writer(response)
    writer.writerow(HEADERS)

    for r in rows:
        p = deal_parts(r['kind'], r['obj'])
        o, d, c = r['obj'], p['donor'], p['center']
        writer.writerow([
            timezone.localtime(r['created']).strftime('%Y-%m-%d %H:%M'),
            r['type'], r['title'], r['category'], r['qty'], r['unit'], r['status_label'],
            timezone.localtime(r['completed']).strftime('%Y-%m-%d %H:%M') if r['completed'] else '',
            r['donor_name'], d.phone, d.user.email, d.city, d.state,
            c.name, c.get_center_type_display(), c.phone, c.district, c.state,
            o.get_method_display() if o.method else '',
            o.pickup_address, o.pickup_date or '', o.pickup_time,
            o.person_name, o.person_phone, o.message,
        ])
    return response


@login_required
def certificate(request, kind, pk):
    obj = load_deal(kind, pk)
    parts = deal_parts(kind, obj)
    donor = get_donor(request)
    if donor is None or donor.pk != parts['donor'].pk or obj.bucket != 'completed':
        messages.error(request, 'A certificate is available to the donor after the donation is completed.')
        return redirect('records')
    d = parts['donor']
    return render(request, 'market/certificate.html', {
        'donor_name': d.user.get_full_name() or d.user.username,
        'item': parts['title'], 'quantity': parts['quantity'], 'unit': parts['unit'],
        'center': parts['center'], 'date': obj.completed_at,
        'number': f"KB-{kind[0].upper()}{obj.pk:05d}",
    })


@require_POST
def contact_submit(request):
    back = redirect(reverse('home') + '#contact')
    if request.POST.get('website'):         # hidden field: only robots fill it
        return back
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Thank you. Your message was sent to the KindBridge team.')
    else:
        messages.error(request, 'Please enter your name, a valid email and a message.')
    return back


@login_required
@staff_required
def admin_messages(request):
    show = request.GET.get('show', 'unread')
    qs = ContactMessage.objects.all()
    if show == 'unread':
        qs = qs.filter(is_read=False)
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'market/admin_messages.html', {
        'page': page, 'show': show,
        'unread': ContactMessage.objects.filter(is_read=False).count(),
        'total': ContactMessage.objects.count(),
        'qs': f'show={show}',
    })


@login_required
@staff_required
@require_POST
def message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=['is_read'])
    messages.success(request, 'Message marked as read.' if msg.is_read else 'Message marked as unread.')
    return redirect(request.POST.get('next') or 'admin_messages')

