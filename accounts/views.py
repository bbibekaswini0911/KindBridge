# from django.contrib import messages
# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.views import LoginView
# from django.db.models import Count, Q
# from django.shortcuts import redirect, render, get_object_or_404
# from django.urls import reverse
# from django.utils import timezone
# from django.views.decorators.http import require_POST
# from market.models import ContactMessage

# import datetime

# from django.db.models import F
# from market.helpers import with_taken
# from market.models import NeedPledge, NeedPost, Offer, OfferClaim

# from donations.models import DonationRequest
# from .decorators import staff_required
# from .models import CenterProfile, Donor
# from .forms import (
#     CenterRegistrationForm,
#     DonorRegistrationForm,
#     ProfileForm,
#     RoleLoginForm,
# )

# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')
#     if request.method == 'POST':
#         form = DonorRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Account created successfully. Please log in.')
#             return redirect('login')
#         messages.error(request, 'Please correct the errors below.')
#     else:
#         form = DonorRegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form})


# def center_register_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')
#     if request.method == 'POST':
#         form = CenterRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request,
#                 'Registration received. You can log in after the administrator approves your care center.')
#             return redirect('login')
#         messages.error(request, 'Please correct the errors below.')
#     else:
#         form = CenterRegistrationForm()
#     return render(request, 'accounts/register_center.html', {'form': form})


# class RoleLoginView(LoginView):
#     template_name = 'accounts/login.html'
#     authentication_form = RoleLoginForm
#     redirect_authenticated_user = True
    
#     def get_success_url(self):
#         target = self.get_redirect_url()
#         if target:
#             return target
#         user = self.request.user
#         if hasattr(user, 'center_profile'):
#             return reverse('center_dashboard')
#         if user.is_staff and not hasattr(user, 'donor'):
#             return reverse('admin_panel')
#         return reverse('dashboard')

#     def form_valid(self, form):
#         user = form.get_user()
#         profile = getattr(user, 'center_profile', None)
#         name = profile.center.name if profile else (user.first_name or user.username)
#         messages.success(self.request, f'Welcome back, {name}.')
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         errors = form.non_field_errors()
#         messages.error(self.request, errors[0] if errors else 'Please check your details and try again.')
#         return super().form_invalid(form)


# @require_POST
# def logout_view(request):
#     logout(request)
#     messages.info(request, 'You have been logged out.')
#     return redirect('home')


# @login_required
# def dashboard_view(request):
#     user = request.user
#     if hasattr(user, 'center_profile'):
#         return redirect('center_dashboard')
#     donor = getattr(user, 'donor', None)
#     if donor is None:
#         if user.is_staff:
#             return redirect('admin_panel')
#         messages.info(request, 'The dashboard is for donor accounts.')
#         return redirect('home')

#     pledges = NeedPledge.objects.filter(donor=donor)
#     claims = OfferClaim.objects.filter(offer__donor=donor)
#     stats = {
#         'taken': pledges.filter(status='taken').count(),
#         'completed': pledges.filter(status='completed').count() + claims.filter(status='completed').count(),
#         'items': Offer.objects.filter(donor=donor).count(),
#         'waiting': claims.filter(status='waiting').count(),
#     }
#     needs = (with_taken(NeedPost.objects.filter(is_closed=False, center__is_active=True))
#              .filter(taken_qty__lt=F('quantity'))
#              .select_related('center').prefetch_related('photos')[:6])
#     return render(request, 'accounts/dashboard.html', {'stats': stats, 'needs': needs})


# @login_required
# def profile_view(request):
#     donor = getattr(request.user, 'donor', None)
#     if donor is None:
#         messages.info(request, 'Profiles are for donor accounts.')
#         return redirect('home')

#     user = request.user
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, user=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated.')
#             return redirect('profile')
#         messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ProfileForm(user=user, initial={
#             'first_name': user.first_name, 'last_name': user.last_name,
#             'email': user.email, 'phone': donor.phone, 'city': donor.city,
#             'state': donor.state, 'address': donor.address,
#         })
#     return render(request, 'accounts/profile.html', {'form': form})

# def _monthly(months=6):
#     """Donation activity (pledges + claims) for each of the last months."""
#     now = timezone.localtime()
#     keys, y, m = [], now.year, now.month
#     for _ in range(months):
#         keys.append((y, m))
#         m -= 1
#         if m == 0:
#             m, y = 12, y - 1
#     keys.reverse()
#     first = timezone.make_aware(datetime.datetime(keys[0][0], keys[0][1], 1))
#     counts = {k: 0 for k in keys}
#     for qs in (NeedPledge.objects.filter(created_at__gte=first),
#                OfferClaim.objects.filter(created_at__gte=first)):
#         for created in qs.values_list('created_at', flat=True):
#             local = timezone.localtime(created)
#             key = (local.year, local.month)
#             if key in counts:
#                 counts[key] += 1
#     top = max(counts.values()) or 1
#     return [{'label': datetime.date(y, m, 1).strftime('%b %Y'),
#              'n': counts[(y, m)],
#              'pct': round(counts[(y, m)] * 100 / top)} for y, m in keys]


# @login_required
# @staff_required
# def admin_panel(request):
#     pending = (CenterProfile.objects.filter(is_approved=False)
#                .select_related('user', 'center').order_by('created_at'))
#     completed = (NeedPledge.objects.filter(status='completed').count()
#                  + OfferClaim.objects.filter(status='completed').count())
#     return render(request, 'accounts/admin_panel.html', {
#         'pending': pending,
#         'stats': {
#             'pending': pending.count(),
#             'centers': CenterProfile.objects.filter(is_approved=True).count(),
#             'donors': Donor.objects.count(),
#             'needs': NeedPost.objects.count(),
#             'items': Offer.objects.count(),
#             'completed': completed,
#             'unread': ContactMessage.objects.filter(is_read=False).count(),
#         },
#         'monthly': _monthly(),
#     })



# @require_POST
# @login_required
# @staff_required
# def approve_center(request, pk):
#     profile = get_object_or_404(CenterProfile, pk=pk)
#     profile.is_approved = True
#     profile.save(update_fields=['is_approved'])
#     profile.center.is_active = True
#     profile.center.save(update_fields=['is_active'])
#     messages.success(request, f'{profile.center.name} approved. They can log in now.')
#     return redirect('admin_panel')


# @require_POST
# @login_required
# @staff_required
# def reject_center(request, pk):
#     profile = get_object_or_404(CenterProfile, pk=pk, is_approved=False)
#     name = profile.center.name
#     user = profile.user
#     profile.center.delete()
#     user.delete()
#     messages.warning(request, f'Registration of {name} was rejected and removed.')
#     return redirect('admin_panel')


from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from market.models import ContactMessage

import datetime

from django.db.models import F
from market.helpers import with_taken
from market.models import NeedPledge, NeedPost, Offer, OfferClaim

from donations.models import DonationRequest
from .decorators import staff_required
from .models import CenterProfile, Donor
from .forms import (
    CenterRegistrationForm,
    DonorRegistrationForm,
    ProfileForm,
    RoleLoginForm,
)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = DonorRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def center_register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CenterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Registration received. You can log in after the administrator approves your care center.')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CenterRegistrationForm()
    return render(request, 'accounts/register_center.html', {'form': form})


class RoleLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = RoleLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        target = self.get_redirect_url()
        if target:
            return target
        user = self.request.user
        if hasattr(user, 'center_profile'):
            return reverse('center_dashboard')
        if user.is_staff and not hasattr(user, 'donor'):
            return reverse('admin_panel')
        return reverse('dashboard')

    def form_valid(self, form):
        user = form.get_user()
        profile = getattr(user, 'center_profile', None)
        name = profile.center.name if profile else (user.first_name or user.username)
        messages.success(self.request, f'Welcome back, {name}.')
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = form.non_field_errors()
        messages.error(self.request, errors[0] if errors else 'Please check your details and try again.')
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard_view(request):
    user = request.user
    if hasattr(user, 'center_profile'):
        return redirect('center_dashboard')
    donor = getattr(user, 'donor', None)
    if donor is None:
        if user.is_staff:
            return redirect('admin_panel')
        messages.info(request, 'The dashboard is for donor accounts.')
        return redirect('home')

    pledges = NeedPledge.objects.filter(donor=donor)
    claims = OfferClaim.objects.filter(offer__donor=donor)
    stats = {
        'taken': pledges.filter(status='taken').count(),
        'completed': pledges.filter(status='completed').count() + claims.filter(status='completed').count(),
        'items': Offer.objects.filter(donor=donor).count(),
        'waiting': claims.filter(status='waiting').count(),
    }
    needs = (with_taken(NeedPost.objects.filter(is_closed=False, center__is_active=True))
             .filter(taken_qty__lt=F('quantity'))
             .select_related('center').prefetch_related('photos')[:6])
    return render(request, 'accounts/dashboard.html', {'stats': stats, 'needs': needs})


@login_required
def profile_view(request):
    donor = getattr(request.user, 'donor', None)
    if donor is None:
        messages.info(request, 'Profiles are for donor accounts.')
        return redirect('home')

    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(user=user, initial={
            'first_name': user.first_name, 'last_name': user.last_name,
            'email': user.email, 'phone': donor.phone, 'city': donor.city,
            'state': donor.state, 'address': donor.address,
        })
    return render(request, 'accounts/profile.html', {'form': form})

def _monthly(months=6):
    """Donation activity (pledges + claims) for each of the last months."""
    now = timezone.localtime()
    keys, y, m = [], now.year, now.month
    for _ in range(months):
        keys.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    keys.reverse()
    first = timezone.make_aware(datetime.datetime(keys[0][0], keys[0][1], 1))
    counts = {k: 0 for k in keys}
    for qs in (NeedPledge.objects.filter(created_at__gte=first),
               OfferClaim.objects.filter(created_at__gte=first)):
        for created in qs.values_list('created_at', flat=True):
            local = timezone.localtime(created)
            key = (local.year, local.month)
            if key in counts:
                counts[key] += 1
    top = max(counts.values()) or 1
    return [{'label': datetime.date(y, m, 1).strftime('%b %Y'),
             'n': counts[(y, m)],
             'pct': round(counts[(y, m)] * 100 / top)} for y, m in keys]


@login_required
@staff_required
def admin_panel(request):
    pending = (CenterProfile.objects.filter(is_approved=False)
               .select_related('user', 'center').order_by('created_at'))
    completed = (NeedPledge.objects.filter(status='completed').count()
                 + OfferClaim.objects.filter(status='completed').count())
    return render(request, 'accounts/admin_panel.html', {
        'pending': pending,
        'stats': {
            'pending': pending.count(),
            'centers': CenterProfile.objects.filter(is_approved=True).count(),
            'donors': Donor.objects.count(),
            'needs': NeedPost.objects.count(),
            'items': Offer.objects.count(),
            'completed': completed,
            'unread': ContactMessage.objects.filter(is_read=False).count(),
        },
        'monthly': _monthly(),
    })



@require_POST
@login_required
@staff_required
def approve_center(request, pk):
    profile = get_object_or_404(CenterProfile, pk=pk)
    profile.is_approved = True
    profile.save(update_fields=['is_approved'])
    profile.center.is_active = True
    profile.center.save(update_fields=['is_active'])
    messages.success(request, f'{profile.center.name} approved. They can log in now.')
    return redirect('admin_panel')


@require_POST
@login_required
@staff_required
def reject_center(request, pk):
    profile = get_object_or_404(CenterProfile, pk=pk, is_approved=False)
    name = profile.center.name
    user = profile.user
    profile.center.delete()
    user.delete()
    messages.warning(request, f'Registration of {name} was rejected and removed.')
    return redirect('admin_panel')