import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_huge_refactoring_delete_old_objects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.provider'),
        ),
        migrations.AlterField(
            model_name='stop',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='stop',
            name='ifopt',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='stop',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='stop',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.provider'),
        ),
        migrations.AlterField(
            model_name='stopid',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.stopidkind'),
        ),
        migrations.AlterField(
            model_name='stopid',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.source'),
        ),
        migrations.AlterField(
            model_name='stopidkind',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.provider'),
        ),
    ]
