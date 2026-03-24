# date -> date_modification + date_creation sur les modèles métier

from django.db import migrations, models
from django.db.models import F


def backfill_date_creation(apps, schema_editor):
    for model_name in (
        'RuParcelle',
        'RuVoie',
        'RuAlignement',
        'RuRegle',
        'RuDetail',
        'RuDetailAlignement',
    ):
        Model = apps.get_model('core', model_name)
        Model.objects.filter(
            date_creation__isnull=True,
            date_modification__isnull=False,
        ).update(date_creation=F('date_modification'))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_ruparcelle_date_modif_regles_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rudetail',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='rudetail',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.AddField(
            model_name='rudetailalignement',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='rudetailalignement',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.AddField(
            model_name='ruregle',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='ruregle',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.AddField(
            model_name='rualignement',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='rualignement',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.AddField(
            model_name='ruparcelle',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='ruparcelle',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.AddField(
            model_name='ruvoie',
            name='date_creation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='ruvoie',
            old_name='date',
            new_name='date_modification',
        ),
        migrations.RunPython(backfill_date_creation, noop_reverse),
    ]
