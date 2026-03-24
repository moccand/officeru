# Generated manually for date_modif_regles on parcelle / alignement

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_ruregle_type_regle_alter_ruvoie_code_voie_ville_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rualignement',
            name='date_modif_regles',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Dernière modification des règles (détails)',
            ),
        ),
        migrations.AddField(
            model_name='ruparcelle',
            name='date_modif_regles',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Dernière modification des règles (détails)',
            ),
        ),
    ]
