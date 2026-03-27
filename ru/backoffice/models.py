from django.db import models

from django.contrib.auth.models import Group
from django.conf import settings

class GroupProfile(models.Model):
    """
    Extension du modèle Group de Django via une relation OneToOne.
    Permet d'ajouter des champs sans toucher au modèle Group natif.
    Compatible avec toutes les montées de version Django.
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Groupe',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Description',
        help_text='Décrit le rôle de ce groupe dans l\'application.',
    )

    class Meta:
        verbose_name        = 'Profil de groupe'
        verbose_name_plural = 'Profils de groupes'

    def __str__(self):
        return f'Profil — {self.group.name}'


class RuExport(models.Model):
    """
    Suivi des exports Internet (SN RU + Règles d'urbanisme).

    Les champs "fichier" et les compteurs numériques sont laissés optionnels tant que
    l'export n'est pas encore terminé.
    """

    class Statut(models.TextChoices):
        EN_COURS = 'EN COURS', 'EN COURS'
        EN_ERREUR = 'EN ERREUR', 'EN ERREUR'
        TERMINE = 'TERMINE', 'TERMINE'
        ARCHIVE_SUPPRIMEE = 'ARCHIVE SUPPRIMEE', 'ARCHIVE SUPPRIMEE'

    datetime_demande_export = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de la demande d export',
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exports',
        verbose_name='Agent',
    )
    commentaire = models.TextField(
        blank=True,
        null=True,
        verbose_name='Commentaire',
    )
    datetime_fin_export = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date de fin de l export',
    )
    statut = models.CharField(
        max_length=30,
        choices=Statut.choices,
        default=Statut.EN_COURS,
        verbose_name='Statut de l export',
    )
    nom_du_fichier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Nom du fichier',
    )
    poids_du_fichier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Poids du fichier',
    )
    nombre_de_parcelles = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Nombre de parcelles',
    )
    nombre_d_alignements = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Nombre d alignements',
    )
    nombre_de_regles = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Nombre de regles',
    )
    nombre_de_details = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Nombre de details',
    )

    def __str__(self) -> str:
        return f'Export {self.pk} — {self.statut}'
