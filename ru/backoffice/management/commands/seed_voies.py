"""
backoffice/management/commands/seed_voies.py
─────────────────────────────────────────────
Commande de management Django pour peupler la table ru_voie avec des données de test.

Usage :
    python manage.py seed_voies              # insère les données (skip si déjà présentes)
    python manage.py seed_voies --reset      # supprime tout puis réinsère
    python manage.py seed_voies --count 50   # génère 50 voies aléatoires en plus
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import RuVoie


# ── Données fixes réalistes (voies parisiennes) ──────────────────────────────

VOIES_FIXES = [
    {
        'id_voie':         1001,
        'libelle_long':    'Rue de Rivoli',
        'libelle_court':   'R DE RIVOLI',
        'code_voie_rivoli':'6780',
        'code_voie_ville': '7501',
        'voie_privee':     0,
        'date_creation':    date(2020, 1, 15),
        'date_modification': date(2020, 1, 15),
    },
    {
        'id_voie':         1002,
        'libelle_long':    'Avenue des Champs-Élysées',
        'libelle_court':   'AV CHAMPS ELYSEES',
        'code_voie_rivoli':'1570',
        'code_voie_ville': '7508',
        'voie_privee':     0,
        'date_creation':    date(2019, 6, 3),
        'date_modification': date(2019, 6, 3),
    },
    {
        'id_voie':         1003,
        'libelle_long':    'Boulevard Haussmann',
        'libelle_court':   'BD HAUSSMANN',
        'code_voie_rivoli':'4370',
        'code_voie_ville': '7509',
        'voie_privee':     0,
        'date_creation':    date(2021, 3, 22),
        'date_modification': date(2021, 3, 22),
    },
    {
        'id_voie':         1004,
        'libelle_long':    'Rue du Faubourg Saint-Antoine',
        'libelle_court':   'R FBG ST ANTOINE',
        'code_voie_rivoli':'3515',
        'code_voie_ville': '7511',
        'voie_privee':     0,
        'date_creation':    date(2018, 11, 7),
        'date_modification': date(2018, 11, 7),
    },
    {
        'id_voie':         1005,
        'libelle_long':    'Impasse des Acacias',
        'libelle_court':   'IMP DES ACACIAS',
        'code_voie_rivoli':'0012',
        'code_voie_ville': '7516',
        'voie_privee':     1,
        'date_creation':    date(2022, 4, 10),
        'date_modification': date(2022, 4, 10),
    },
    {
        'id_voie':         1006,
        'libelle_long':    'Place de la Bastille',
        'libelle_court':   'PL DE LA BASTILLE',
        'code_voie_rivoli':'0670',
        'code_voie_ville': '7512',
        'voie_privee':     0,
        'date_creation':    date(2020, 8, 19),
        'date_modification': date(2020, 8, 19),
    },
    {
        'id_voie':         1007,
        'libelle_long':    'Rue Lepic',
        'libelle_court':   'R LEPIC',
        'code_voie_rivoli':'5290',
        'code_voie_ville': '7518',
        'voie_privee':     0,
        'date_creation':    date(2023, 1, 5),
        'date_modification': date(2023, 1, 5),
    },
    {
        'id_voie':         1008,
        'libelle_long':    'Villa des Artistes',
        'libelle_court':   'VILLA DES ARTISTES',
        'code_voie_rivoli':'9934',
        'code_voie_ville': '7514',
        'voie_privee':     1,
        'date_creation':    date(2017, 9, 28),
        'date_modification': date(2017, 9, 28),
    },
    {
        'id_voie':         1009,
        'libelle_long':    'Quai de la Tournelle',
        'libelle_court':   'Q DE LA TOURNELLE',
        'code_voie_rivoli':'7812',
        'code_voie_ville': '7505',
        'voie_privee':     0,
        'date_creation':    date(2021, 12, 1),
        'date_modification': date(2021, 12, 1),
    },
    {
        'id_voie':         1010,
        'libelle_long':    'Allée des Cygnes',
        'libelle_court':   'ALL DES CYGNES',
        'code_voie_rivoli':'0234',
        'code_voie_ville': '7515',
        'voie_privee':     0,
        'date_creation':    date(2019, 2, 14),
        'date_modification': date(2019, 2, 14),
    },
]


# ── Données pour la génération aléatoire ─────────────────────────────────────

PREFIXES = ['Rue', 'Avenue', 'Boulevard', 'Impasse', 'Place', 'Allée',
            'Villa', 'Quai', 'Passage', 'Cité', 'Résidence', 'Square']

NOMS = [
    'de la Paix', 'du Commerce', 'des Lilas', 'Victor Hugo', 'Jean Jaurès',
    'de la République', 'du Général de Gaulle', 'des Fleurs', 'de la Liberté',
    'Émile Zola', 'des Minimes', 'du Temple', 'de Bercy', 'de Tolbiac',
    'des Pyrénées', 'de Ménilmontant', 'de Belleville', 'de la Villette',
    'du Château', 'de la Fontaine', 'des Maraîchers', 'de la Butte',
    'Saint-Denis', 'Saint-Martin', 'Saint-Jacques', 'du Bac',
]

ARRONDISSEMENTS = [f'75{str(i).zfill(2)}' for i in range(1, 21)]


def generer_voie_aleatoire(id_voie: int) -> dict:
    prefix = random.choice(PREFIXES)
    nom    = random.choice(NOMS)
    arr    = random.choice(ARRONDISSEMENTS)
    code_rivoli = str(random.randint(100, 9999)).zfill(4)
    debut  = date(2015, 1, 1)
    jours  = random.randint(0, (date.today() - debut).days)
    d      = debut + timedelta(days=jours)

    return {
        'id_voie':         id_voie,
        'libelle_long':    f'{prefix} {nom}',
        'libelle_court':   f'{prefix[:1]} {nom[:10].upper()}',
        'code_voie_rivoli': code_rivoli,
        'code_voie_ville':  arr,
        'voie_privee':      random.choice([0, 0, 0, 1]),  # 25% privées
        'date_creation':    d,
        'date_modification': d,
    }


# ── Commande ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Peuple la table ru_voie avec des données de test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime toutes les voies existantes avant d\'insérer',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=0,
            help='Nombre de voies aléatoires supplémentaires à générer (défaut: 0)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            nb_suppr = RuVoie.objects.count()
            RuVoie.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'  {nb_suppr} voie(s) supprimée(s)')
            )

        # ── Insérer les voies fixes ──
        nb_crees = 0
        nb_skips = 0

        for data in VOIES_FIXES:
            _, created = RuVoie.objects.get_or_create(
                id_voie=data['id_voie'],
                defaults=data,
            )
            if created:
                nb_crees += 1
            else:
                nb_skips += 1

        # ── Générer des voies aléatoires si --count est fourni ──
        nb_aleatoires = 0
        if options['count'] > 0:
            # Trouver le prochain id_voie disponible
            dernier_id = RuVoie.objects.order_by('-id_voie').values_list('id_voie', flat=True).first() or 2000
            prochain_id = dernier_id + 1

            voies_aleatoires = [
                RuVoie(**generer_voie_aleatoire(prochain_id + i))
                for i in range(options['count'])
            ]
            RuVoie.objects.bulk_create(voies_aleatoires, ignore_conflicts=True)
            nb_aleatoires = options['count']

        # ── Résumé ──
        self.stdout.write(self.style.SUCCESS(
            f'\nSeed terminé :'
            f'\n  {nb_crees} voie(s) fixe(s) créée(s)'
            f'\n  {nb_skips} voie(s) fixe(s) déjà présente(s) (skippées)'
            f'\n  {nb_aleatoires} voie(s) aléatoire(s) générée(s)'
            f'\n  Total en base : {RuVoie.objects.count()} voie(s)'
        ))
