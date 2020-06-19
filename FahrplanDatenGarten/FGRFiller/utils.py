import datetime
import io
import os
import subprocess
import tempfile
from enum import Enum

from fdfgen import forge_fdf


class FillFormFieldsCompensation(Enum):
    PAYMENT_POS_BANK_TRANSFER = "Auszahlung oder Überweisung"
    VOUCHER = "Gutschein"

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class FillFormFieldsBahnCard100SeasonTicket(Enum):
    BAHNCARD_100 = "BahnCard 100-Nr."
    SEASON_TICKET = "Zeitkarten-Nr."

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


def fill_form_fields(
        travel_date: datetime.date,
        departure_stop_name: str,
        departure_planned_time: datetime.time,
        arrival_stop_name: str,
        arrival_planned_time: datetime.time,
        arrival_actual_datetime: datetime.datetime,
        arrival_actual_product_type: str,
        arrival_actual_product_number: str,
        first_delayed_train_product_type: str,
        first_delayed_train_product_number: str,
        first_delayed_train_departure_planned: datetime.time,
        compensation: FillFormFieldsCompensation,
        **kwargs) -> dict:
    return {
        "S1F1": travel_date.strftime("%d"),  # Reisedatum DD
        "S1F2": travel_date.strftime("%m"),  # Reisedatum MM
        "S1F3": travel_date.strftime("%y"),  # Reisedatum YY
        "S1F4": departure_stop_name,  # Startbahnhof
        "S1F5": departure_planned_time.strftime("%H"),  # Planabfahrt HH
        "S1F6": departure_planned_time.strftime("%M"),  # Planabfahrt MM
        "S1F7": arrival_stop_name,  # Zielbahnhof
        "S1F8": arrival_planned_time.strftime("%H"),  # Planankunft HH
        "S1F9": arrival_planned_time.strftime("%M"),  # Planankunft MM
        "S1F10": arrival_actual_datetime.strftime("%d"),  # Reales Ankunftsdatum DD
        "S1F11": arrival_actual_datetime.strftime("%m"),  # Reales Ankunftsdatum MM
        "S1F12": arrival_actual_datetime.strftime("%y"),  # Reales Ankunftsdatum YY
        "S1F13": arrival_actual_product_type,  # Reale Ankunft Zugart
        "S1F14": arrival_actual_product_number,  # Reale Ankunft Zugnummer
        "S1F15": arrival_actual_datetime.strftime("%H"),  # Reale Ankunft HH
        "S1F16": arrival_actual_datetime.strftime("%M"),  # Reale Ankunft MM
        "S1F17": first_delayed_train_product_type,  # Erster verspaeteter Zug (Zugart)
        "S1F18": first_delayed_train_product_number,  # Erster verspaeteter Zug (Zugnummer)
        "S1F19": first_delayed_train_departure_planned.strftime("%H"),  # Erster verspaeteter Zug (Planabfahrt HH)
        "S1F20": first_delayed_train_departure_planned.strftime("%M"),  # Erster verspaeteter Zug (Planabfahrt MM)
        "S1F21": "Ja" if kwargs.get('connecting_train_missed', False) else "Off",  # Anschlusszug verpasst? (Ja/Off)
        "S1F22": kwargs.get('connecting_train_missed_station', ''),  # Anschlusszug verpasst -> Bahnhofsname
        "S1F23": "Ja" if kwargs.get('changed_train', False) else "Off",  # Umgestiegen?
        "S1F24": kwargs.get('changed_train_last_station', ''),  # Umgestiegen -> Bahnhofsname
        "S1F25": "Ja" if kwargs.get('journey_not_start_or_cut_short', False) else "Off",  # Reise nicht angetreten/abgebrochen? (Ja/Off)
        "S1F26": kwargs.get('journey_not_start_or_cut_short_station', ''),  # Reise nicht angetreten/abgebrochen -> Name des Bahnhofs wo abgebrochen
        "S1F27": "Ja" if kwargs.get('journey_cut_short_additional_costs', False) else "Off",  # Reise abgebrochen mit Zusatzkosten? (Ja/Off)
        "S1F28": kwargs.get('journey_cut_short_additional_costs_station', ''),  # Reise abgebrochen mit Zusatzkosten -> Name des Bahnhofs wo abgebrochen
        "S1F29": compensation.value if compensation is not None else "Off",  # "Gutschein" oder "Auszahlung oder Ueberweisung"?
        "S2F20": kwargs.get('bank_details_account_holder', ''),  # Ueberweisung -> Kontoinhaber
        "S2F21": kwargs.get('bank_details_iban', ''),  # Ueberweisung -> IBAN
        "S2F22": kwargs.get('bank_details_bic', ''),  # Ueberweisung -> BIC
        "S2F1": 'Off',  # "Geschlecht" (Frau/Herr/Off)
        "S2F2": kwargs.get('academic_title', ''),  # Titel
        "S2F3": kwargs.get('company', ''),  # Firma
        "S2F4": kwargs.get('last_name', ''),  # Nachname
        "S2F5": kwargs.get('first_name', ''),  # Vorname
        "S2F6": kwargs.get('address_c_o_extra_details', ''),  # c/o oder Adresszusatz
        "S2F7": kwargs.get('telephone_number', ''),  # Telefonummer
        "S2F8": kwargs.get('address_street', ''),  # Strase
        "S2F9": kwargs.get('address_house_nr', ''),  # Hausnummer
        "S2F10": kwargs.get('address_country', ''),  # Staat (wenn != D)
        "S2F11": kwargs.get('address_postal_code', ''),  # PLZ
        "S2F12": kwargs.get('address_city', ''),  # Wohnort
        "S2F13": kwargs['bahncard_100_season_ticket'].value if kwargs.get('bahncard_100_season_ticket') is not None else "Off",  # "BahnCard 100-Nr."? "Zeitkarten-Nr."?
        "S2F15": kwargs.get('bahncard_100_season_ticket_number', ''),  # BahnCard 100-/Zeitkarten Nummer
        "S2F16": kwargs['date_of_birth'].strftime('%d') if kwargs.get('date_of_birth') is not None else '',  # Geburtsdatum DD
        "S2F17": kwargs['date_of_birth'].strftime('%m') if kwargs.get('date_of_birth') is not None else '',  # Geburtsdatum MM
        "S2F18": kwargs['date_of_birth'].strftime('%Y') if kwargs.get('date_of_birth') is not None else '',  # Geburtsdatum YYYY
        "S2F19": '',  # E-Mail Adresse (Marktforschung)
        "S2F23": '',  # Einverstädnis Marktforschung?
    }


def generate_form(fields, pdftk="pdftk", *args, **kwargs):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    fp = tempfile.NamedTemporaryFile(delete=False)
    fpdf = tempfile.NamedTemporaryFile(delete=False)
    fdf = forge_fdf("", fields, [], [], [])
    fp.write(fdf)
    fp.close()
    subprocess.run([pdftk, dir_path + '/fahrgastrechte.pdf',
                    "fill_form", fp.name, "output", fpdf.name])

    fpdf.seek(0)
    pdf = io.BytesIO()
    pdf.write(fpdf.read())

    fpdf.close()
    os.unlink(fp.name)
    os.unlink(fpdf.name)
    pdf.seek(0)
    return pdf
