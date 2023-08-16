from decimal import Decimal

import django.db.models.deletion
import django_countries.fields
from DBApis.csvImport import parse_db_opendata_stop_csv
from django.db import migrations, models
from django.db.models import Model


def migrate_old_data(apps, schema_editor):
    Provider: Model = apps.get_model('core', 'Provider')
    Source: Model = apps.get_model('core', 'Source')
    Stop: Model = apps.get_model('core', 'Stop')
    StopID: Model = apps.get_model('core', 'StopID')
    StopIDKind: Model = apps.get_model('core', 'StopIDKind')
    StopLocation: Model = apps.get_model('core', 'StopLocation')
    Journey: Model = apps.get_model('core', 'Journey')
    if Stop.objects.all().count() != 0:
        provider = Provider.objects.create(
            internal_name='db',
            friendly_name='Deutsche Bahn'
        )
        source_hafas = Source.objects.create(
            internal_name='db_hafas',
            friendly_name='Deutsche Bahn HAFAS',
            provider=provider
        )
        source_csv = Source.objects.create(
            internal_name='db_csv',
            friendly_name='DB Open-Data-Portal CSV',
            provider=provider)

        stops_to_update = []
        stopids_to_update = []
        stopidkinds_to_update = []
        journeys_to_update = []

        csv_reader = parse_db_opendata_stop_csv()
        for csv_row in csv_reader:
            stopid = StopID.objects.filter(external_id=csv_row['EVA_NR'])
            if stopid.count() == 0:
                return
            stopid = stopid.first()
            stopid.source = source_csv
            stopids_to_update.append(stopid)
            stop = stopid.stop
            if csv_row['IFOPT'] != "":
                stop.ifopt = csv_row['IFOPT']
                stop.name = csv_row['NAME']
                stop.has_long_distance_traffic = csv_row['Verkehr'] == 'FV'
                stop.country = csv_row['IFOPT'][:2]
                stop.provider = provider
                stop.latitude = Decimal(csv_row['Breite'].replace(',', '.'))
                stop.longitude = Decimal(csv_row['Laenge'].replace(',', '.'))
                stops_to_update.append(stop)

        for stopidkind in StopIDKind.objects.all():
            stopidkind.provider = provider
            stopidkinds_to_update.append(stopidkind)

        for journey in Journey.objects.all():
            journey.source = source_hafas
            journeys_to_update.append(journey)

        Stop.objects.bulk_update(
            objs=stops_to_update,
            fields=[
                'ifopt',
                'name',
                'has_long_distance_traffic',
                'country',
                'latitude',
                'longitude',
                'provider'])
        StopID.objects.bulk_update(
            objs=stopids_to_update,
            fields=['source'])
        StopIDKind.objects.bulk_update(
            objs=stopidkinds_to_update,
            fields=['provider'])
        Journey.objects.bulk_update(
            objs=journeys_to_update,
            fields=['source'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_journey_cancelled'),
    ]

    operations = [
        # Add and rename fields, create provider model
        # At this stage some new fields are nullable. These are filled and made
        # not-nullable afterwards
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('friendly_name', models.CharField(max_length=255)),
                ('internal_name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.RenameField(
            model_name='source',
            old_name='name',
            new_name='internal_name',
        ),
        migrations.AlterField(
            model_name='source',
            name='internal_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.RenameField(
            model_name='stopid',
            old_name='name',
            new_name='external_id',
        ),
        migrations.RemoveField(
            model_name='journey',
            name='agency',
        ),
        migrations.AddField(
            model_name='source',
            name='friendly_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='country',
            field=django_countries.fields.CountryField(
                max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='stop',
            name='has_long_distance_traffic',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='ifopt',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='stop',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True),
        ),
        migrations.AddField(
            model_name='stop',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True),
        ),
        migrations.AddField(
            model_name='stop',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.provider'),
        ),
        migrations.AddField(
            model_name='stop',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.provider'),
        ),
        migrations.AddField(
            model_name='stopidkind',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.provider'),
        ),

        # Add data for new fields to old stops (if existent)
        migrations.RunPython(migrate_old_data),

        # Remove old models
        migrations.DeleteModel(
            name='Agency',
        ),
        migrations.DeleteModel(
            name='StopLocation',
        ),
        migrations.DeleteModel(
            name='StopName',
        ),
        migrations.AlterModelOptions(
            name='journeystop',
            options={},
        ),
    ]
