from django import forms

from centers.models import CareCenter

from .models import ContactMessage, NeedPost, Offer, PickupInfo

MAX_PHOTOS = 3
MAX_SIZE = 3 * 1024 * 1024


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Accepts several image files in one field and returns a list."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            files = [single(d, initial) for d in data]
        else:
            files = [single(data, initial)]
        return [f for f in files if f]


def check_photos(files):
    if len(files) > MAX_PHOTOS:
        raise forms.ValidationError(f'Please choose at most {MAX_PHOTOS} photos.')
    for f in files:
        if f.size > MAX_SIZE:
            raise forms.ValidationError('Each photo must be smaller than 3 MB.')
    return files


class NeedPostForm(forms.ModelForm):
    photos = MultipleImageField(required=False, label='Photos (up to 3)')

    class Meta:
        model = NeedPost
        fields = ['title', 'category', 'quantity', 'unit', 'needed_by', 'description']
        labels = {'unit': 'Unit', 'needed_by': 'Needed by (optional)'}
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'For example, Rice for 40 children'}),
            'unit': forms.TextInput(attrs={'placeholder': 'kg, pieces, boxes'}),
            'needed_by': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell donors what exactly you need and why'}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data['quantity']
        if qty < 1:
            raise forms.ValidationError('Quantity must be at least 1.')
        return qty

    def clean_photos(self):
        return check_photos(self.cleaned_data.get('photos') or [])


class OfferForm(forms.ModelForm):
    photos = MultipleImageField(required=False, label='Photos (up to 3)')

    class Meta:
        model = Offer
        fields = ['title', 'category', 'quantity', 'city', 'description', 'address']
        labels = {
            'city': 'City or town',
            'address': 'Pickup address (shown only to the centre you accept)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'For example, 3 school bags in good condition'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Condition, size, age group and anything else useful'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data['quantity']
        if qty < 1:
            raise forms.ValidationError('Quantity must be at least 1.')
        return qty

    def clean_photos(self):
        return check_photos(self.cleaned_data.get('photos') or [])


class PledgeForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))


class ClaimForm(forms.Form):
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))


class DonorPickupForm(forms.Form):
    method = forms.ChoiceField(choices=PickupInfo.METHODS, label='How will the item reach the centre?')
    pickup_address = forms.CharField(
        required=False, label='Address where the person should come',
        widget=forms.Textarea(attrs={'rows': 3}))
    pickup_date = forms.DateField(
        required=False, label='Preferred date',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    pickup_time = forms.CharField(
        required=False, max_length=40, label='Preferred time',
        widget=forms.TextInput(attrs={'placeholder': 'For example, 5 pm to 7 pm'}))

    def clean(self):
        data = super().clean()
        if data.get('method') == 'center_pickup' and not (data.get('pickup_address') or '').strip():
            self.add_error('pickup_address', 'Please give the address where the person should come.')
        return data


class CenterPersonForm(forms.Form):
    person_name = forms.CharField(max_length=100, label='Name of the person who will come')
    person_phone = forms.RegexField(
        regex=r'^\d{10}$', label='Phone number of that person',
        error_messages={'invalid': 'Enter a 10-digit phone number.'})


class CenterProfileForm(forms.ModelForm):
    class Meta:
        model = CareCenter
        fields = ['phone', 'address', 'description', 'image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']

