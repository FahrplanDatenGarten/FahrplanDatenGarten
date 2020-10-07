from DBApis.csvImport import parse_db_opendata_stop_csv
from django.db import migrations
from django.db.models import Model


def delete_stops_without_ifopt(apps, schema_editor):
    Stop: Model = apps.get_model('core', 'Stop')
    StopID: Model = apps.get_model('core', 'StopID')
    csv_reader = parse_db_opendata_stop_csv()
    for csv_row in csv_reader:
        if csv_row['IFOPT'] == '':
            stopid_set = StopID.objects.filter(external_id=csv_row['EVA_NR'])
            if stopid_set.count() != 0:
                stopid_set.first().stop.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_huge_refactoring_stop'),
    ]

    operations = [
        # Delete old stop to allow making fields the old source not has not
        # nullable
        migrations.RunSQL(
            "DELETE FROM core_source WHERE internal_name='dbapis'"),
        migrations.RunPython(delete_stops_without_ifopt)
    ]
