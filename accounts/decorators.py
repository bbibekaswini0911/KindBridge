from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def donor_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'donor', None) is None:
            messages.info(request, 'This page is for donor accounts.')
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper


def center_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'center_profile', None)
        if profile is None or not profile.is_approved:
            messages.info(request, 'This page is for approved care center accounts.')
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper


def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.info(request, 'This page is for the administrator.')
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper