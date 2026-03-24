# Suppression d'une règle : supprime les RuDetail / RuDetailAlignement liés
# (sans toucher aux parcelles ni aux alignements).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_date_creation_date_modification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rudetail',
            name='id_regle',
            field=models.ForeignKey(
                db_column='id_regle',
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='details',
                to='core.ruregle',
            ),
        ),
        migrations.AlterField(
            model_name='rudetailalignement',
            name='id_regle',
            field=models.ForeignKey(
                db_column='id_regle',
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='details_alignement',
                to='core.ruregle',
            ),
        ),
    ]
