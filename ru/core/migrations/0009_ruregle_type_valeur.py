from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_rudetail_rudetailalignement_regle_cascade'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruregle',
            name='type_valeur',
            field=models.CharField(
                blank=False,
                choices=[
                    ('PAS DE VALEUR', 'PAS DE VALEUR'),
                    ('LISTE FIXE', 'LISTE FIXE'),
                    ('SAISIE LIBRE', 'SAISIE LIBRE'),
                ],
                default='PAS DE VALEUR',
                max_length=30,
                verbose_name='Type de valeur',
            ),
        ),
    ]

