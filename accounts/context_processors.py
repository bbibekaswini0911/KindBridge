# def roles(request):
#     user = request.user
#     if not user.is_authenticated:
#         return {'role': None}

#     if getattr(user, 'donor', None) is not None:
#         return {'role': 'donor',
#                 'display_name': user.get_full_name() or user.username}

#     profile = getattr(user, 'center_profile', None)
#     if profile is not None:
#         return {'role': 'center',
#                 'display_name': profile.center.name,
#                 'center_profile': profile}

#     return {'role': 'admin' if user.is_staff else 'user',
#             'display_name': user.get_full_name() or user.username}



from django.urls import NoReverseMatch, reverse

# (label, url name, icon). A link is shown only when its url name exists.
MENUS = {
    'donor': [
        ('Dashboard', 'dashboard', 'dash'),
        ('Needs market', 'need_board', 'store'),
        ('Care centres', 'explore', 'search'),
        ('Publish an item', 'publish_offer', 'plus'),
        ('My items', 'my_offers', 'box'),
        ('Records', 'records', 'list'),
        ('My profile', 'profile', 'user'),
    ],
    'center': [
        ('Dashboard', 'center_dashboard', 'dash'),
        ('Post a need', 'post_need', 'plus'),
        ('My needs', 'my_needs', 'box'),
        ('Donor items', 'offer_board', 'store'),
        ('Records', 'records', 'list'),
        ('Centre profile', 'center_profile', 'user'),
    ],
    'admin': [
        ('Dashboard', 'admin_panel', 'dash'),
        ('Messages', 'admin_messages', 'mail'),
        ('Records', 'records', 'list'),
        ('Django admin', 'admin:index', 'admin'),
    ],
}


def _menu(role, current):
    items = []
    for label, name, icon in MENUS.get(role, []):
        try:
            url = reverse(name)
        except NoReverseMatch:
            continue
        items.append({'label': label, 'url': url, 'icon': icon, 'on': name == current})
    return items


def roles(request):
    user = request.user
    if not user.is_authenticated:
        return {'role': None}

    current = getattr(getattr(request, 'resolver_match', None), 'url_name', None)

    if getattr(user, 'donor', None) is not None:
        role, name = 'donor', user.get_full_name() or user.username
        extra = {}
    elif getattr(user, 'center_profile', None) is not None:
        profile = user.center_profile
        role, name = 'center', profile.center.name
        extra = {'center_profile': profile}
    else:
        role = 'admin' if user.is_staff else 'user'
        name = user.get_full_name() or user.username
        extra = {}

    data = {'role': role, 'display_name': name, 'menu': _menu(role, current)}
    data.update(extra)
    return data


