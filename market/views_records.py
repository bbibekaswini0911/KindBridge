import calendar

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .helpers import deal_rows

PER_PAGE = 10


@login_required
def records(request):
    rows = deal_rows(request)
    if rows is None:
        messages.info(request, 'Records are for donor, care centre and admin accounts.')
        return redirect('home')

    tab = request.GET.get('tab', 'pending')
    if tab not in ('pending', 'completed', 'history'):
        tab = 'pending'
    q = request.GET.get('q', '').strip()

    counts = {
        'pending': sum(1 for r in rows if r['bucket'] == 'pending'),
        'completed': sum(1 for r in rows if r['bucket'] == 'completed'),
        'history': len(rows),
    }

    shown = rows if tab == 'history' else [r for r in rows if r['bucket'] == tab]
    if q:
        needle = q.lower()
        shown = [r for r in shown if needle in r['search']]

    page = Paginator(shown, PER_PAGE).get_page(request.GET.get('page'))

    query = request.GET.copy()
    query.pop('page', None)

    return render(request, 'market/records.html', {
        'page': page,
        'tab': tab,
        'q': q,
        'counts': counts,
        'qs': query.urlencode(),
        'years': sorted({r['created'].year for r in rows}, reverse=True),
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    })
