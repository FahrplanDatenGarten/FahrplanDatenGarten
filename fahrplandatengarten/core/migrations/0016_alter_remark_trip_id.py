# Generated by Django 4.2 on 2024-12-14 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_stop_ifopt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remark',
            name='trip_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]