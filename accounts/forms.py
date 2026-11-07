# from django import forms
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth.models import User
# from django.db import transaction

# from centers.models import CareCenter

# from .models import CenterProfile, Donor

# PHONE_ERROR = {'invalid': 'Enter a 10-digit phone number.'}


# class RoleLoginForm(AuthenticationForm):
#     role = forms.ChoiceField(
#         choices=[('donor', 'Donor'), ('center', 'Care center')],
#         widget=forms.HiddenInput, required=False, initial='donor',
#     )

# def confirm_login_allowed(self, user):
#             super().confirm_login_allowed(user)
#             is_donor = getattr(user, 'donor', None) is not None
#             has_center = getattr(user, 'center_profile', None) is not None
#             if user.is_staff and not is_donor and not has_center:
#                 return
#                 role = self.cleaned_data.get('role') or 'donor'
#                 if role == 'donor':
#                     if not is_donor:
#                         raise forms.ValidationError(
#                     'This is not a donor account. Use the Care center tab.', code='wrong_role')
#                 else:
#                     if not has_center:
#                         raise forms.ValidationError(
#                     'This is not a care center account. Use the Donor tab.', code='wrong_role')
#             if not user.center_profile.is_approved:
#                 raise forms.ValidationError(
#                     'Your care center is waiting for administrator approval.', code='pending')


# class DonorRegistrationForm(UserCreationForm):
#     first_name = forms.CharField(max_length=50, label='First name')
#     last_name = forms.CharField(max_length=50, required=False, label='Last name')
#     email = forms.EmailField()
#     phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
#     city = forms.CharField(max_length=60)
#     state = forms.CharField(max_length=60)
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

#     field_order = ['first_name', 'last_name', 'username', 'email', 'phone',
#                    'city', 'state', 'address', 'password1', 'password2']

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email')

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError('An account with this email already exists.')
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data['email']
#         if commit:
#             user.save()
#             Donor.objects.create(
#                 user=user,
#                 phone=self.cleaned_data['phone'],
#                 city=self.cleaned_data['city'],
#                 state=self.cleaned_data['state'],
#                 address=self.cleaned_data['address'],
#             )
#         return user


# class CenterRegistrationForm(UserCreationForm):
#     center_name = forms.CharField(max_length=150, label='Care center name')
#     center_type = forms.ChoiceField(choices=CareCenter.CenterType.choices, label='Type')
#     contact_person = forms.CharField(max_length=100, label='Contact person')
#     phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
#     state = forms.CharField(max_length=60)
#     district = forms.CharField(max_length=60)
#     email = forms.EmailField()
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
#     description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='About your center')

#     field_order = ['center_name', 'center_type', 'contact_person', 'phone', 'state', 'district',
#                    'username', 'email', 'address', 'description', 'password1', 'password2']

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('username', 'email')

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError('An account with this email already exists.')
#         return email

#     def clean_center_name(self):
#         name = self.cleaned_data['center_name'].strip()
#         if CareCenter.objects.filter(name__iexact=name).exists():
#             raise forms.ValidationError('A care center with this name already exists.')
#         return name

#     @transaction.atomic
#     def save(self, commit=True):
#         data = self.cleaned_data
#         user = super().save(commit=False)
#         user.email = data['email']
#         user.first_name = data['contact_person']
#         user.save()
#         center = CareCenter.objects.create(
#             name=data['center_name'], center_type=data['center_type'],
#             state=data['state'], district=data['district'],
#             address=data['address'], description=data['description'],
#             phone=data['phone'], is_active=False,
#         )
#         CenterProfile.objects.create(
#             user=user, center=center,
#             contact_person=data['contact_person'], phone=data['phone'],
#         )
#         return user


# class ProfileForm(forms.Form):
#     first_name = forms.CharField(max_length=50, label='First name')
#     last_name = forms.CharField(max_length=50, required=False, label='Last name')
#     email = forms.EmailField()
#     phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
#     city = forms.CharField(max_length=60)
#     state = forms.CharField(max_length=60)
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

#     def __init__(self, *args, user, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.user = user

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
#             raise forms.ValidationError('Another account already uses this email.')
#         return email

#     def save(self):
#         data = self.cleaned_data
#         user = self.user
#         user.first_name = data['first_name']
#         user.last_name = data['last_name']
#         user.email = data['email']
#         user.save()
#         donor = user.donor
#         donor.phone = data['phone']
#         donor.city = data['city']
#         donor.state = data['state']
#         donor.address = data['address']
#         donor.save()
        
        
        
        
        
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from centers.models import CareCenter

from .models import CenterProfile, Donor

PHONE_ERROR = {'invalid': 'Enter a 10-digit phone number.'}


class RoleLoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[('donor', 'Donor'), ('center', 'Care center')],
        widget=forms.HiddenInput, required=False, initial='donor',
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        is_donor = hasattr(user, 'donor')
        profile = getattr(user, 'center_profile', None)
        has_center = profile is not None

        # Staff accounts without a donor/centre profile use the admin login.
        if user.is_staff and not is_donor and not has_center:
            return

        role = self.cleaned_data.get('role') or 'donor'
        if role == 'donor' and not is_donor:
            raise forms.ValidationError(
                'This is not a donor account. Use the Care center tab.',
                code='wrong_role',
            )
        if role == 'center' and not has_center:
            raise forms.ValidationError(
                'This is not a care center account. Use the Donor tab.',
                code='wrong_role',
            )
        if has_center and not profile.is_approved:
            raise forms.ValidationError(
                'Your care center is waiting for administrator approval.',
                code='pending',
            )


class DonorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='First name')
    last_name = forms.CharField(max_length=50, required=False, label='Last name')
    email = forms.EmailField()
    phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
    city = forms.CharField(max_length=60)
    state = forms.CharField(max_length=60)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    field_order = ['first_name', 'last_name', 'username', 'email', 'phone',
                   'city', 'state', 'address', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Donor.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                address=self.cleaned_data['address'],
            )
        return user


class CenterRegistrationForm(UserCreationForm):
    center_name = forms.CharField(max_length=150, label='Care center name')
    center_type = forms.ChoiceField(choices=CareCenter.CenterType.choices, label='Type')
    contact_person = forms.CharField(max_length=100, label='Contact person')
    phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
    state = forms.CharField(max_length=60)
    district = forms.CharField(max_length=60)
    email = forms.EmailField()
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='About your center')
    image = forms.ImageField(required=False, label='Care center photo')

    field_order = ['center_name', 'center_type', 'contact_person', 'phone', 'state', 'district',
                   'username', 'email', 'address', 'description', 'image', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_center_name(self):
        name = self.cleaned_data['center_name'].strip()
        if CareCenter.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('A care center with this name already exists.')
        return name

    @transaction.atomic
    def save(self, commit=True):
        data = self.cleaned_data
        user = super().save(commit=False)
        user.email = data['email']
        user.first_name = data['contact_person']
        user.save()
        center = CareCenter.objects.create(
            name=data['center_name'], center_type=data['center_type'],
            state=data['state'], district=data['district'],
            address=data['address'], description=data['description'],
            phone=data['phone'], image=data.get('image'), is_active=False,
        )
        CenterProfile.objects.create(
            user=user, center=center,
            contact_person=data['contact_person'], phone=data['phone'],
        )
        return user


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='First name')
    last_name = forms.CharField(max_length=50, required=False, label='Last name')
    email = forms.EmailField()
    phone = forms.RegexField(regex=r'^\d{10}$', label='Phone number', error_messages=PHONE_ERROR)
    city = forms.CharField(max_length=60)
    state = forms.CharField(max_length=60)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Another account already uses this email.')
        return email

    def save(self):
        data = self.cleaned_data
        user = self.user
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.save()
        donor = user.donor
        donor.phone = data['phone']
        donor.city = data['city']
        donor.state = data['state']
        donor.address = data['address']
        donor.save()
        
        

        
