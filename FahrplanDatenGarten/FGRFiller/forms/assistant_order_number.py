from django import forms


class FGRFillerAsstiantOrderNumberForm(forms.Form):
    order_number = forms.CharField(
        label="Buchungsnummer",
        required=True
    )
    last_name = forms.CharField(
        label="Nachname",
        required=True
    )
