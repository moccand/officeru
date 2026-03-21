"""
backoffice/management/commands/seed_alignements.py
───────────────────────────────────────────────────
Commande de management Django pour peupler la table ru_alignement
avec des données de test liées aux RuVoie existantes en base.

Prérequis : des RuVoie doivent exister (lancer seed_voies d'abord)

Usage :
    python manage.py seed_alignements              # 3 alignements par voie
    python manage.py seed_alignements --reset      # supprime tout puis réinsère
    python manage.py seed_alignements --par_voie 5 # nb d'alignements par voie
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import RuVoie, RuAlignement, RuParcelle


# ── Données pour la génération ────────────────────────────────────────────────

SUFFIXES = ['bis', 'ter', 'A', 'B', 'C', '']
PARITES  = [0, 1, 2]   # 0=tous, 1=impair, 2=pair


def numero_aleatoire():
    return random.randint(1, 200)


def suffixe_aleatoire():
    return random.choice(SUFFIXES)


def date_aleatoire():
    debut = date(2015, 1, 1)
    jours = random.randint(0, (date.today() - debut).days)
    return debut + timedelta(days=jours)


def generer_alignement(id_alignement, voie, parcelle):
    num_debut = numero_aleatoire()
    num_fin   = num_debut + random.randint(2, 20) * 2  # toujours > début

    return RuAlignement(
        id_alignement  = id_alignement,
        numero_debut   = num_debut,
        adresse_debut  = str(num_debut),
        suffixe_un_debut = suffixe_aleatoire(),
        suffixe_2_debut  = '',
        suffixe_3_debut  = '',
        numero_fin     = num_fin,
        adresse_fin    = str(num_fin),
        suffixe_un_fin = suffixe_aleatoire(),
        suffixe_2_fin  = '',
        suffixe_3_fin  = '',
        id_voie        = voie,
        parite         = random.choice(PARITES),
        id_parcelle    = parcelle,
        commune        = int(voie.code_voie_ville) if voie.code_voie_ville.isdigit() else 75001,
        date           = date_aleatoire(),
    )


class Command(BaseCommand):
    help = 'Peuple la table ru_alignement avec des données de test liées aux RuVoie existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime tous les alignements existants avant d\'insérer',
        )
        parser.add_argument(
            '--par_voie',
            type=int,
            default=3,
            help='Nombre d\'alignements à créer par voie (défaut: 3)',
        )

    def handle(self, *args, **options):

        if options['reset']:
            nb_suppr = RuAlignement.objects.count()
            RuAlignement.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'  {nb_suppr} alignement(s) supprimé(s)')
            )

        # ── Vérifier qu'il y a des voies en base ──
        voies = list(RuVoie.objects.all())
        if not voies:
            self.stdout.write(self.style.ERROR(
                'Aucune voie trouvée en base. '
                'Lancez d\'abord : python manage.py seed_voies'
            ))
            return

        # ── Vérifier qu'il y a des parcelles en base ──
        parcelles = list(RuParcelle.objects.all())
        if not parcelles:
            self.stdout.write(self.style.ERROR(
                'Aucune parcelle trouvée en base. '
                'Les alignements nécessitent des RuParcelle existantes.'
            ))
            return

        self.stdout.write(
            f'  {len(voies)} voie(s) trouvée(s) — '
            f'génération de {options["par_voie"]} alignement(s) par voie…'
        )

        # ── Trouver le prochain id_alignement disponible ──
        dernier_id = (
            RuAlignement.objects
            .order_by('-id_alignement')
            .values_list('id_alignement', flat=True)
            .first()
        ) or 0
        prochain_id = dernier_id + 1

        # ── Générer les alignements ──
        alignements = []
        for voie in voies:
            for _ in range(options['par_voie']):
                parcelle = random.choice(parcelles)
                alignements.append(
                    generer_alignement(prochain_id, voie, parcelle)
                )
                prochain_id += 1

        RuAlignement.objects.bulk_create(alignements, ignore_conflicts=True)

        # ── Résumé par voie ──
        self.stdout.write('')
        for voie in voies:
            nb = voie.alignements.count()
            self.stdout.write(f'  {voie} → {nb} alignement(s)')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed terminé :'
            f'\n  {len(alignements)} alignement(s) créé(s)'
            f'\n  Répartis sur {len(voies)} voie(s)'
            f'\n  Total en base : {RuAlignement.objects.count()} alignement(s)'
        ))
