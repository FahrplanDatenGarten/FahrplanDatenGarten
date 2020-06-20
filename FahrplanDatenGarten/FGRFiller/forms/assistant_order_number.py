from django import forms


class FGRFillerAsstiantOrderNumberForm(forms.Form):
    order_number = forms.CharField(
        label="Buchungsnummer:",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    last_name = forms.CharField(
        label="Nachname:",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
