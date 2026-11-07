from django import forms

from .models import DonationRequest


class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ['requirement', 'quantity', 'message']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional note for the center'}),
        }

    def __init__(self, *args, center, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields['requirement']
        field.queryset = center.requirements.filter(is_active=True)
        field.empty_label = 'Choose an item'
        field.label = 'Item to donate'
        field.label_from_instance = lambda r: (
            f'{r.item_name} ({r.get_category_display()}), needs {r.quantity_needed}'
        )

    def clean(self):
        cleaned = super().clean()
        requirement = cleaned.get('requirement')
        quantity = cleaned.get('quantity')
        if quantity is not None and quantity < 1:
            self.add_error('quantity', 'Quantity must be at least 1.')
        elif requirement and quantity and quantity > requirement.quantity_needed:
            self.add_error(
                'quantity',
                f'This center needs at most {requirement.quantity_needed} of this item.',
            )
        return cleaned