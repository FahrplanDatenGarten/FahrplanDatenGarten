from django import forms

from FGRFiller.utils import (FillFormFieldsBahnCard100SeasonTicket,
                             FillFormFieldsCompensation)


class FGRFillerDataForm(forms.Form):
    travel_date = forms.DateField(
        label="Reisedatum:",
        required=True,
    )
    departure_stop_name = forms.CharField(
        label="Startbahnhof:",
        required=True,
        max_length=26,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    departure_planned_time = forms.TimeField(
        label="Abfahrt laut Fahrplan:",
        required=True
    )
    arrival_stop_name = forms.CharField(
        label="Zielbahnhof:",
        required=True,
        max_length=26,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    arrival_planned_time = forms.TimeField(
        label="Ankunft laut Fahrplan:",
        required=True
    )
    arrival_actual_date = forms.DateField(
        label="Echtes Ankunftsdatum:",
        required=True
    )
    arrival_actual_time = forms.TimeField(
        label="Echte Ankunftsuhrzeit:",
        required=True
    )
    arrival_actual_product_type = forms.CharField(
        label="Letzter Zug (Ankunftszug) - Art (ICE/IC/RE...):",
        max_length=3,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    arrival_actual_product_number = forms.CharField(
        label="Letzter Zug (Ankunftszug) - Nummer:",
        max_length=5,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    first_delayed_train_product_type = forms.CharField(
        label="Erster verspäteter Zug - Art (ICE/IC/RE...)",
        max_length=3,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    first_delayed_train_product_number = forms.CharField(
        label="Erster verspäteter Zug - Nummer:",
        max_length=5,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    first_delayed_train_departure_planned = forms.TimeField(
        label="Geplante Abfahrt des ersten verspäteten Zugs:",
        required=True
    )
    changed_train = forms.BooleanField(
        label="Umgestiegen?",
        required=False
    )
    changed_train_last_station = forms.CharField(
        required=False,
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Letzter Umstiegsbahnhof'
            }
        ),
    )
    connecting_train_missed = forms.BooleanField(
        label="Anschlusszug verpasst?",
        required=False
    )
    connecting_train_missed_station = forms.CharField(
        required=False,
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Bahnhof wo Anschlusszug verpasst'
            }
        )
    )
    journey_not_start_or_cut_short = forms.BooleanField(
        label="Reise nicht angetreten oder zurückgefahren?",
        required=False
    )
    journey_not_start_or_cut_short_station = forms.CharField(
        required=False,
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Bahnhof wo zurückgefahren'
            }
        )
    )
    journey_cut_short_additional_costs = forms.BooleanField(
        label="Reise unterbrochen und mit anderen Verkehrsmittel weitergefahren (mit Zusatzkosten)",
        required=False)
    journey_cut_short_additional_costs_station = forms.CharField(
        required=False,
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Bahnhof wo Reise unterbrochen'
            }
        )
    )
    compensation = forms.ChoiceField(
        choices=[(tag, tag.value) for tag in FillFormFieldsCompensation],
        label="Art der Erstattung:",
        required=False,
        widget=forms.RadioSelect()
    )
    first_name = forms.CharField(
        label="Vorname:",
        max_length=18,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    last_name = forms.CharField(
        label="Nachname:",
        max_length=18,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    academic_title = forms.CharField(
        label="Titel",
        max_length=10,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    company = forms.CharField(
        label="Firma:",
        max_length=37,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_c_o_extra_details = forms.CharField(
        label="c/o oder Adresszusatz:",
        max_length=18,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    telephone_number = forms.CharField(
        label="Telefonnummer:",
        max_length=18,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_street = forms.CharField(
        label="Adresse - Straße:",
        max_length=32,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_house_nr = forms.CharField(
        label="Adresse - Hausnummer:",
        max_length=4,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_city = forms.CharField(
        label="Adresse - Stadt:",
        max_length=23,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_postal_code = forms.CharField(
        label="Adresse - PLZ:",
        max_length=5,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    address_country = forms.CharField(
        label="Staat (wenn nicht D):",
        max_length=3,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    bahncard_100_season_ticket = forms.ChoiceField(
        choices=[(tag, tag.value) for tag in FillFormFieldsBahnCard100SeasonTicket],
        required=False,
        label="BahnCard 100 oder Zeitkarte vorhanden?:",
        widget=forms.RadioSelect()
    )
    bahncard_100_season_ticket_number = forms.CharField(
        label="BahnCard 100-/Zeitkarten-Nr:",
        max_length=18,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input'
            }
        ),
    )
    date_of_birth = forms.DateField(
        label="Geburtsdatum (nur bei BC100)",
        required=False
    )
